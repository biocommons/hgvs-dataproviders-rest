"""Provides access to the NCBI table that allows to access transcripts by NCBI gene ids

This file is specific to Invitae and is nearly a copy of uta.py.  It
is not tested (see pytest.ini for exclusion).

"""

import contextlib
import inspect
import logging
import os

import psycopg2
import psycopg2.extras
import psycopg2.pool
from urllib import parse as urlparse

from src import hgvs_dataproviders_rest
from src.hgvs_dataproviders_rest import HGVSError, HGVSDataNotAvailableError
from src.hgvs_dataproviders_rest.txdata.txdata_interface import TxDataInterface

_logger = logging.getLogger(__name__)


class NCBIBase(TxDataInterface):
    required_version = "1.1"

    _queries = {
        "gene_id_for_hgnc": """
            select distinct(gene_id)
            from assocacs
            where hgnc=?
            """,
        "gene_id_for_tx": """
            select gene_id
            from assocacs
            where tx_ac=?
            """,
        "tx_for_gene_id": """
            select tx_ac
            from assocacs
            where gene_id=?
            """,
        "hgnc_for_gene_id": """
            select distinct(hgnc)
            from assocacs
            where gene_id=?
            """,
        "gene_info_for_gene_id": """
            select gene_id, tax_id, hgnc, maploc, aliases, type, summary, descr, xrefs
            from geneinfo
            where gene_id=?
            """,
        "gene_info_for_hgnc": """
            select gene_id, tax_id, hgnc, maploc, aliases, type, summary, descr, xrefs
            from geneinfo
            where hgnc=?
            """,
        "all_transcripts": """
                select distinct(tx_ac)
                from assocacs
            """,
    }

    def __init__(self, url):
        super().__init__()
        self.url = url

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

    def _update(self, sql, *args):
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

    def get_ncbi_gene_id_for_hgnc(self, hgnc):
        rows = self._fetchall(self._queries["gene_id_for_hgnc"], [hgnc])
        return [r["gene_id"] for r in rows]

    def get_ncbi_gene_id_for_tx(self, tx_ac):
        rows = self._fetchall(self._queries["gene_id_for_tx"], [tx_ac])
        return [r["gene_id"] for r in rows]

    def get_tx_for_ncbi_gene_id(self, gene_id):
        rows = self._fetchall(self._queries["tx_for_gene_id"], [gene_id])
        return [r["tx_ac"] for r in rows]

    def get_hgnc_for_ncbi_gene_id(self, gene_id):
        rows = self._fetchall(self._queries["hgnc_for_gene_id"], [gene_id])
        return [r["hgnc"] for r in rows]

    def get_gene_info_for_ncbi_gene_id(self, gene_id):
        rows = self._fetchall(self._queries["gene_info_for_gene_id"], [gene_id])
        return rows

    def get_gene_info_for_hgnc(self, hgnc):
        rows = self._fetchall(self._queries["gene_info_for_hgnc"], [hgnc])
        return rows

    def get_all_transcripts(self):
        rows = self._fetchall(self._queries["all_transcripts"], [])
        return [r["tx_ac"] for r in rows]

    def store_assocacs(self, hgnc, tx_ac, gene_id, pro_ac, origin):
        sql = """
                insert into assocacs (hgnc, tx_ac, gene_id, pro_ac, origin)
                values (%s,%s,%s,%s,%s)

            """
        self._update(sql, [hgnc, tx_ac, gene_id, pro_ac, origin])


class NCBI_postgresql(NCBIBase):
    def __init__(
        self,
        url,
        pooling=True,
        pool_min: int = 1,
        pool_max: int = 10,
        application_name=None
    ):
        if url.schema is None:
            raise Exception("No schema name provided in {url}".format(url=url))
        self.application_name = application_name
        self.pooling = pooling
        self.pool_min = pool_min
        self.pool_max = pool_max
        self._conn = None
        super(NCBI_postgresql, self).__init__(url)

    def __del__(self):
        self.close()

    def close(self):
        if self.pooling:
            _logger.warning("Closing pool; future mapping and validation will fail.")
            self._pool.closeall()
        else:
            _logger.warning("Closing connection; future mapping and validation will fail.")
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
            self._pool = psycopg2.pool.ThreadedConnectionPool(self.pool_min, self.pool_max, **conn_args)
        else:
            self._conn = psycopg2.connect(**conn_args)
            self._conn.autocommit = True

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
                cur.execute("set search_path = {self.url.schema};".format(self=self))

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
                    self._pool.closeall()
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
