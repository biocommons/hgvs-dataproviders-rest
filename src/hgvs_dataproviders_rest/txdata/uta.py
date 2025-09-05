# -*- coding: utf-8 -*-
"""implements an hgvs data provider interface using UTA
(https://github.com/biocommons/uta)

"""

import contextlib
import inspect
import logging
import os
import weakref

import psycopg2
import psycopg2.extras
import psycopg2.pool
from bioutils.assemblies import make_ac_name_map
from bioutils.digests import seq_md5
from urllib import parse as urlparse

from src import hgvs_dataproviders_rest
from src.hgvs_dataproviders_rest import HGVSError, HGVSDataNotAvailableError
from src.hgvs_dataproviders_rest.txdata.txdata_interface import TxDataInterface

_logger = logging.getLogger(__name__)


class UTABase(TxDataInterface):
    required_version = "1.1"

    _queries = {
        "acs_for_protein_md5": """
            select ac
            from seq_anno
            where seq_id=?
            """,
        "gene_info": """
            select *
            from gene
            where hgnc=?
            """,
        # TODO: reconcile tx_exons query and build_tx_cigar
        # built_tx_cigar says it expects exons in transcript order,
        # but tx_exons isn't do that (on the - strand).
        "tx_exons": """
            select *
            from tx_exon_aln_v
            where tx_ac=? and alt_ac=? and alt_aln_method=?
            order by alt_start_i
            """,
        "tx_for_gene": """
            select hgnc, cds_start_i, cds_end_i, tx_ac, alt_ac, alt_aln_method
            from transcript T
            join exon_set ES on T.ac=ES.tx_ac where alt_aln_method != 'transcript' and hgnc=?
            """,
        "alignments_for_region": """
            select tx_ac,alt_ac,alt_strand,alt_aln_method,min(start_i) as start_i,max(end_i) as end_i
            from exon_set ES
            join exon E on ES.exon_set_id=E.exon_set_id
            where alt_ac=?
            group by tx_ac,alt_ac,alt_strand,alt_aln_method
            having min(start_i) < ? and ? <= max(end_i)
            """,
        "tx_identity_info": """
            select distinct(tx_ac), alt_ac, alt_aln_method, cds_start_i, cds_end_i, lengths, hgnc
            from tx_def_summary_v
            where tx_ac=?
            """,
        "tx_info": """
            select hgnc, cds_start_i, cds_end_i, tx_ac, alt_ac, alt_aln_method
            from transcript T
            join exon_set ES on T.ac=ES.tx_ac
            where tx_ac=? and alt_ac=? and alt_aln_method=?
            """,
        "tx_mapping_options": """
            select distinct tx_ac,alt_ac,alt_aln_method
            from tx_exon_aln_v where tx_ac=? and exon_aln_id is not NULL
            """,
        "tx_seq": """
            select seq
            from seq S
            join seq_anno SA on S.seq_id=SA.seq_id
            where ac=?
            """,
        "tx_similar": """
            select *
            from tx_similarity_v
            where tx_ac1 = ?
            """,
        "tx_to_pro": """
            select * from associated_accessions where tx_ac = ? order by pro_ac desc
            """,
    }

    def __init__(self, url, mode=None, cache=None):
        self.url = url
        self.seqfetcher = SeqFetcher()
        if mode != "run":
            self._connect()
        super(UTABase, self).__init__(mode, cache)

    def __str__(self):
        return (
            "{n} <data_version:{dv}; schema_version:{sv}; application_name={self.application_name};"
            " url={self.url}; sequences-from={sf}>"
        ).format(
            n=type(self).__name__,
            self=self,
            dv=self.data_version(),
            sv=self.schema_version(),
            sf=self.sequence_source(),
        )

    def _fetchone(self, sql, *args):
        with self._get_cursor() as cur:
            cur.execute(sql, *args)
            return cur.fetchone()

    def _fetchall(self, sql, *args):
        with self._get_cursor() as cur:
            cur.execute(sql, *args)
            return cur.fetchall()

    ############################################################################
    # Queries

    def data_version(self):
        return self.url.schema

    def schema_version(self):
        return self._fetchone("select * from meta where key = 'schema_version'")["value"]

    @staticmethod
    def sequence_source():
        seqrepo_dir = os.environ.get("HGVS_SEQREPO_DIR")
        seqrepo_url = os.environ.get("HGVS_SEQREPO_URL")
        if seqrepo_dir:
            return seqrepo_dir
        elif seqrepo_url:
            return seqrepo_url
        else:
            return "seqfetcher"

    def get_acs_for_protein_seq(self, seq):
        """
        returns a list of protein accessions for a given sequence.  The
        list is guaranteed to contain at least one element with the
        MD5-based accession (MD5_01234abc...def56789) at the end of the
        list.
        """
        md5 = seq_md5(seq)
        return [r["ac"] for r in self._fetchall(self._queries["acs_for_protein_md5"], [md5])] + [
            "MD5_" + md5
        ]

    def get_gene_info(self, gene):
        """
        returns basic information about the gene.

        :param gene: HGNC gene name
        :type gene: str

        # database results
        hgnc    | ATM
        maploc  | 11q22-q23
        descr   | ataxia telangiectasia mutated
        summary | The protein encoded by this gene belongs to the PI3/PI4-kinase family. This...
        aliases | AT1,ATA,ATC,ATD,ATE,ATDC,TEL1,TELO1
        added   | 2014-02-04 21:39:32.57125

        """
        return self._fetchone(self._queries["gene_info"], [gene])

    def get_tx_exons(self, tx_ac, alt_ac, alt_aln_method):
        """
        return transcript exon info for supplied accession (tx_ac, alt_ac, alt_aln_method), or None if not found

        :param tx_ac: transcript accession with version (e.g., 'NM_000051.3')
        :type tx_ac: str

        :param alt_ac: specific genomic sequence (e.g., NC_000011.4)
        :type alt_ac: str

        :param alt_aln_method: sequence alignment method (e.g., splign, blat)
        :type alt_aln_method: str

        # tx_exons = db.get_tx_exons('NM_199425.2', 'NC_000020.10', 'splign')
        # len(tx_exons)
        3

        tx_exons have the following attributes::

            {
                'tes_exon_set_id' : 98390
                'aes_exon_set_id' : 298679
                'tx_ac'           : 'NM_199425.2'
                'alt_ac'          : 'NC_000020.10'
                'alt_strand'      : -1
                'alt_aln_method'  : 'splign'
                'ord'             : 2
                'tx_exon_id'      : 936834
                'alt_exon_id'     : 2999028
                'tx_start_i'      : 786
                'tx_end_i'        : 1196
                'alt_start_i'     : 25059178
                'alt_end_i'       : 25059588
                'cigar'           : '410='
            }

        For example:

        # tx_exons[0]['tx_ac']
        'NM_199425.2'

        """
        rows = self._fetchall(self._queries["tx_exons"], [tx_ac, alt_ac, alt_aln_method])
        if len(rows) == 0:
            raise HGVSDataNotAvailableError(
                "No tx_exons for (tx_ac={tx_ac},alt_ac={alt_ac},alt_aln_method={alt_aln_method})".format(
                    tx_ac=tx_ac, alt_ac=alt_ac, alt_aln_method=alt_aln_method
                )
            )

        # TODO: Check that end == transcript sequence length (but length N/A in current hdp)
        ex0 = 0 if (rows[0]["alt_strand"] == 1) else -1
        if rows[ex0]["tx_start_i"] != 0:
            raise HGVSDataNotAvailableError(
                "Alignment is incomplete; cannot use transcript for mapping"
                "(tx_ac={tx_ac},alt_ac={alt_ac},alt_aln_method={alt_aln_method})".format(
                    tx_ac=tx_ac, alt_ac=alt_ac, alt_aln_method=alt_aln_method
                )
            )
        return rows

    def get_tx_for_gene(self, gene):
        """
        return transcript info records for supplied gene, in order of decreasing length

        :param gene: HGNC gene name
        :type gene: str
        """
        return self._fetchall(self._queries["tx_for_gene"], [gene])

    def get_tx_for_region(self, alt_ac, alt_aln_method, start_i, end_i):
        """
        return transcripts that overlap given region

        :param str alt_ac: reference sequence (e.g., NC_000007.13)
        :param str alt_aln_method: alignment method (e.g., splign)
        :param int start_i: 5' bound of region
        :param int end_i: 3' bound of region
        """

        return self.get_alignments_for_region(
            alt_ac=alt_ac, start_i=start_i, end_i=end_i, alt_aln_method=alt_aln_method
        )

    def get_alignments_for_region(self, alt_ac, start_i, end_i, alt_aln_method=None):
        """
        return transcripts that overlap given region

        :param str alt_ac: reference sequence (e.g., NC_000007.13)
        :param int start_i: 5' bound of region
        :param int end_i: 3' bound of region
        :param str alt_aln_method: OPTIONAL alignment method (e.g., splign)
        """

        alignments = self._fetchall(
            self._queries["alignments_for_region"], [alt_ac, start_i, end_i]
        )
        if alt_aln_method is not None:
            alignments = [a for a in alignments if a["alt_aln_method"] == alt_aln_method]
        return alignments

    def get_tx_identity_info(self, tx_ac):
        """returns features associated with a single transcript.

        :param tx_ac: transcript accession with version (e.g., 'NM_199425.2')
        :type tx_ac: str

        # database output
        -[ RECORD 1 ]--+-------------
        tx_ac          | NM_199425.2
        alt_ac         | NM_199425.2
        alt_aln_method | transcript
        cds_start_i    | 283
        cds_end_i      | 1003
        lengths        | {707,79,410}
        hgnc           | VSX1

        """
        rows = self._fetchall(self._queries["tx_identity_info"], [tx_ac])
        if len(rows) == 0:
            raise HGVSDataNotAvailableError(
                "No transcript definition for (tx_ac={tx_ac})".format(tx_ac=tx_ac)
            )
        return rows[0]

    def get_tx_info(self, tx_ac, alt_ac, alt_aln_method):
        """return a single transcript info for supplied accession (tx_ac, alt_ac, alt_aln_method), or None if not found

        :param tx_ac: transcript accession with version (e.g., 'NM_000051.3')
        :type tx_ac: str

        :param alt_ac: specific genomic sequence (e.g., NC_000011.4)
        :type alt_ac: str

        :param alt_aln_method: sequence alignment method (e.g., splign, blat)
        :type alt_aln_method: str

        # database output
        -[ RECORD 1 ]--+------------
        hgnc           | ATM
        cds_start_i    | 385
        cds_end_i      | 9556
        tx_ac          | NM_000051.3
        alt_ac         | AC_000143.1
        alt_aln_method | splign

        """
        rows = self._fetchall(self._queries["tx_info"], [tx_ac, alt_ac, alt_aln_method])
        if len(rows) == 0:
            raise HGVSDataNotAvailableError(
                "No tx_info for (tx_ac={tx_ac},alt_ac={alt_ac},alt_aln_method={alt_aln_method})".format(
                    tx_ac=tx_ac, alt_ac=alt_ac, alt_aln_method=alt_aln_method
                )
            )
        elif len(rows) == 1:
            return rows[0]
        else:
            raise HGVSError(
                "Multiple ({n}) replies for tx_info(tx_ac="
                "{tx_ac},alt_ac={alt_ac},alt_aln_method={alt_aln_method})".format(
                    n=len(rows), tx_ac=tx_ac, alt_ac=alt_ac, alt_aln_method=alt_aln_method
                )
            )

    def get_tx_mapping_options(self, tx_ac):
        """Return all transcript alignment sets for a given transcript
        accession (tx_ac); returns empty list if transcript does not
        exist.  Use this method to discovery possible mapping options
        supported in the database

        :param tx_ac: transcript accession with version (e.g., 'NM_000051.3')
        :type tx_ac: str

        # database output
        -[ RECORD 1 ]--+------------
        hgnc           | ATM
        cds_start_i    | 385
        cds_end_i      | 9556
        tx_ac          | NM_000051.3
        alt_ac         | AC_000143.1
        alt_aln_method | splign
        -[ RECORD 2 ]--+------------
        hgnc           | ATM
        cds_start_i    | 385
        cds_end_i      | 9556
        tx_ac          | NM_000051.3
        alt_ac         | NC_000011.9
        alt_aln_method | blat

        """
        rows = self._fetchall(self._queries["tx_mapping_options"], [tx_ac])
        return rows

    def get_similar_transcripts(self, tx_ac):
        """Return a list of transcripts that are similar to the given
        transcript, with relevant similarity criteria.

        >> sim_tx = hdp.get_similar_transcripts('NM_001285829.1')
        >> dict(sim_tx[0])
        { 'cds_eq': False,
        'cds_es_fp_eq': False,
        'es_fp_eq': True,
        'tx_ac1': 'NM_001285829.1',
        'tx_ac2': 'ENST00000498907' }

        where:

        * cds_eq means that the CDS sequences are identical
        * es_fp_eq means that the full exon structures are identical
          (i.e., incl. UTR)
        * cds_es_fp_eq means that the cds-clipped portions of the exon
          structures are identical (i.e., ecluding. UTR)
        * Hint: "es" = "exon set", "fp" = "fingerprint", "eq" = "equal"

        "exon structure" refers to the start and end coordinates on a
        specified reference sequence. Thus, having the same exon
        structure means that the transcripts are defined on the same
        reference sequence and have the same exon spans on that
        sequence.

        """

        rows = self._fetchall(self._queries["tx_similar"], [tx_ac])
        return rows

    def get_pro_ac_for_tx_ac(self, tx_ac):
        """Return the (single) associated protein accession for a given transcript
        accession, or None if not found."""

        rows = self._fetchall(self._queries["tx_to_pro"], [tx_ac])
        try:
            return rows[0]["pro_ac"]
        except IndexError:
            return None

    def get_assembly_map(self, assembly_name):
        """return a list of accessions for the specified assembly name (e.g., GRCh38.p5)"""
        return make_ac_name_map(assembly_name)


class UTA_postgresql(UTABase):
    def __init__(
        self,
        url,
        pooling=True,
        pool_min: int=1,
        pool_max: int=10,
        application_name=None,
        mode=None,
        cache=None,
    ):
        if url.schema is None:
            raise Exception("No schema name provided in {url}".format(url=url))
        self.application_name = application_name
        self.pooling = pooling
        self.pool_min = pool_min
        self.pool_max = pool_max
        self._conn = None
        self._pool = None
        # If we're using connection pooling, track the set of DB
        # connections we've seen; on first use we set the schema
        # search path. Use weak references to avoid keeping connection
        # objects alive unnecessarily.
        self._conns_seen = weakref.WeakSet()
        super(UTA_postgresql, self).__init__(url, mode, cache)

    def __del__(self):
        self.close()

    def close(self):
        if self.pooling:
            if self._pool is not None:
                self._pool.closeall()
        else:
            if self._conn is not None:
                self._conn.close()

    def _connect(self):
        if self.application_name is None:
            st = inspect.stack()
            self.application_name = os.path.basename(st[-1][1])
        conn_args = dict(
            host=self.url.hostname,
            port=self.url.port,
            database=self.url.database,
            user=self.url.username,
            password=self.url.password,
            application_name=self.application_name + "/" + hgvs_dataproviders_rest.__version__,
        )
        if self.pooling:
            _logger.info("Using UTA ThreadedConnectionPool")
            self._pool = psycopg2.pool.ThreadedConnectionPool(self.pool_min, self.pool_max, **conn_args
            )
        else:
            self._conn = psycopg2.connect(**conn_args)
            self._conn.autocommit = True
            with self._get_cursor() as cur:
                self._set_search_path(cur)

        self._ensure_schema_exists()

        # remap sqlite's ? placeholders to psycopg2's %s
        self._queries = {k: v.replace("?", "%s") for k, v in self._queries.items()}

    def _ensure_schema_exists(self):
        # N.B. On AWS RDS, information_schema.schemata always returns zero rows
        r = self._fetchone(
            "select exists(SELECT 1 FROM pg_namespace WHERE nspname = %s)", [self.url.schema]
        )
        if r[0]:
            return
        raise HGVSDataNotAvailableError(
            "specified schema ({}) does not exist (url={})".format(self.url.schema, self.url)
        )

    @contextlib.contextmanager
    def _get_cursor(self, n_retries=1):
        """Returns a context manager for obtained from a single or pooled
        connection, and sets the PostgreSQL search_path to the schema
        specified in the connection URL.

        Although *connections* are threadsafe, *cursors* are bound to
        connections and are *not* threadsafe. Do not share cursors
        across threads.

        Use this funciton like this::

            with hdp._get_cursor() as cur:
                # your code

        Do not call this function outside a contextmanager.

        """

        n_tries_rem = n_retries + 1
        while n_tries_rem > 0:
            try:
                conn = self._pool.getconn() if self.pooling else self._conn

                # autocommit=True obviates closing explicitly
                conn.autocommit = True

                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                if self.pooling:
                    # this might be a new connection, in which case we
                    # need to set the search path
                    if conn not in self._conns_seen:
                        self._set_search_path(cur)
                        self._conns_seen.add(conn)

                yield cur

                # contextmanager executes these when context exits
                cur.close()
                if self.pooling:
                    self._pool.putconn(conn)

                break

            except psycopg2.OperationalError:
                _logger.warning(
                    "Lost connection to {url}; attempting reconnect".format(url=self.url)
                )
                if self.pooling:
                    self._pool.putconn(conn)
                    _logger.warning("Put away pool connection from {url}".format(url=self.url))
                else:
                    self._connect()
                    _logger.warning("Reconnected to {url}".format(url=self.url))

            n_tries_rem -= 1

        else:
            # N.B. Probably never reached
            raise HGVSError(
                "Permanently lost connection to {url} ({n} retries)".format(
                    url=self.url, n=n_retries
                )
            )

    def _set_search_path(self, cur):
        cur.execute("set search_path = {self.url.schema},public;".format(self=self))


class ParseResult(urlparse.ParseResult):
    """Subclass of url.ParseResult that adds database and schema methods,
    and provides stringification.

    """

    def __new__(cls, pr):
        return super(ParseResult, cls).__new__(cls, *pr)

    @property
    def database(self):
        path_elems = self.path.split("/")
        return path_elems[1] if len(path_elems) > 1 else None

    @property
    def schema(self):
        path_elems = self.path.split("/")
        return path_elems[2] if len(path_elems) > 2 else None

    def __str__(self):
        return self.geturl()


def _parse_url(db_url):
    """parse database connection urls into components

    UTA database connection URLs follow that of SQLAlchemy, except
    that a schema may be optionally specified after the database. The
    skeleton format is:

       driver://user:pass@host/database/schema

    >>> params = _parse_url("driver://user:pass@host:9876/database/schema")

    >>> params.scheme
    u'driver'

    >>> params.hostname
    u'host'

    >>> params.username
    u'user'

    >>> params.password
    u'pass'

    >>> params.database
    u'database'

    >>> params.schema
    u'schema'

    """

    return ParseResult(urlparse.urlparse(db_url))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
