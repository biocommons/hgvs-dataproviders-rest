# hgvs dataproviders rest client
"""implements the hgvs data provider interface as a client for the hgvs dataprovider REST api
(https://github.com/biocommons/hgvs-dataproviders-rest)
(https://github.com/biocommons/uta)

"""

import os
from typing import List, Optional, Union

import requests

from src.hgvs_dataproviders_rest.txdata.txdata_interface import TxDataInterface


def connect():
    # Eventually replace this fake default url :)
    url = os.environ.get("UTAREST_URL", "https://api.biocommons.org/utarest/0")
    return UTARESTService(url)


class UTARESTService(TxDataInterface):
    required_version = "1.0"

    def __init__(self, server_url, mode=None, cache=None, timeout=30):
        self.server = server_url
        self.application_name = "UTA REST"
        self.timeout = timeout
        self.pingresponse = requests.get(server_url + "/ping", timeout=self.timeout).json()
        super().__init__()

    def __str__(self):
        n = type(self).__name__,
        self = self,
        dv = self.data_version(),
        sv = self.schema_version(),
        sf = self.sequence_source(),
        return (
            f"{n} <data_version:{dv}; schema_version:{sv}; application_name={self.application_name};"
            f" url={self.url}; sequences-from={sf}>"
        )

    ############################################################################
    # Queries

    def data_version(self) -> str:
        return self.pingresponse["data_version"]

    def schema_version(self) -> str:
        return self.pingresponse["schema_version"]

    def sequence_source(self) -> str:
        return self.pingresponse["sequence_source"]

    def optional_parameters(self, names: list, params: list) -> str:
        """
        TODO: You may actually be able to do this using the params argument in requests.get()

        returns a string representation of query parameters that can be appended to a url
        example: optional_parameters(["start_i", "end_i", "align_method"], [0, 1, "splign"]))
        returns: ?start_i=0&end_i=1&align_method=splign
        """
        if not len(names) == len(params):
            raise Exception("Ensure there is a matching value for each parameter name.")
        retval = "?"
        params_added = False
        for (param, name) in zip(params, names):
            if param:
                if params_added:
                    retval += "&"
                retval += f"{name}={param}"
                params_added = True
        return retval

    def get_acs_for_protein_seq(self, seq: str) -> List:
        """
        returns a list of protein accessions for a given sequence.  The
        list is guaranteed to contain at least one element with the
        MD5-based accession (MD5_01234abc...def56789) at the end of the
        list.
        """
        url = f"{self.server}/acs_for_protein_seq/{seq}"
        return requests.get(url, timeout=self.timeout).json()

    def get_gene_info(self, gene: str) -> Union[dict, None]:
        """
        returns basic information about the gene.

        :param gene: HGNC gene name
        :type gene: str

        genes have the following attributes:
        {
            'hgnc'    : ATM
            'maploc'  : 11q22-q23
            'descr'   : ataxia telangiectasia mutated
            'summary' : The protein encoded by this gene belongs to the PI3/PI4-kinase family. This...
            'aliases' : AT1,ATA,ATC,ATD,ATE,ATDC,TEL1,TELO1
            'added'   : 2014-02-04 21:39:32.57125
        }

        """
        url = f"{self.server}/gene_info/{self.gene}"
        return requests.get(url, timeout=self.timeout).json()

    def get_tx_exons(self, tx_ac: str, alt_ac: str, alt_aln_method: str) -> List[dict]:
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

        tx_exons have the following attributes:

            {
                'hgnc'             : VSX1
                'tx_ac'            : NM_199425.2
                'alt_ac'           : NC_000020.10
                'alt_aln_method'   : splign
                'alt_strand'       : -1
                'ord'              : 2
                'tx_start_i'       : 786
                'tx_end_i'         : 1196
                'alt_start_i'      : 25059178
                'alt_end_i'        : 25059588
                'cigar'            : 410=
                'tx_aseq'          : null
                'alt_aseq'         : null
                'test_exon_set_id' : 98390
                'aes_exon_set_id'  : 298679
                'tx_exon_id'       : 936834
                'alt_exon_id'      : 2999028
                'exon_aln_id'      : 1148619
            }

        For example:

        # tx_exons[0]['tx_ac']
        'NM_199425.2'

        """
        url = f"{self.server}/tx_exons/{tx_ac}/{alt_ac}?alt_aln_method={alt_aln_method}"
        return requests.get(url, timeout=self.timeout).json()

    def get_tx_for_gene(self, gene: str) -> Union[List[dict], None]:
        """
        return transcript info records for supplied gene, in order of decreasing length

        :param gene: HGNC gene name
        :type gene: str
        """
        url = f"{self.server}/tx_for_gene/{gene}"
        return requests.get(url, timeout=self.timeout).json()

    def get_tx_for_region(self, alt_ac: str, alt_aln_method: str, start_i: int, end_i: int) -> Union[List[dict], None]:
        """
        return transcripts that overlap given region

        :param str alt_ac: reference sequence (e.g., NC_000007.13)
        :param str alt_aln_method: alignment method (e.g., splign)
        :param int start_i: 5' bound of region
        :param int end_i: 3' bound of region
        """
        url = f"{self.server}/tx_for_region/{alt_ac}?alt_aln_method={alt_aln_method}&start_i={start_i}&end_i={end_i}"
        return requests.get(url, timeout=self.timeout).json()

    def get_alignments_for_region(
        self, alt_ac: str, start_i: int, end_i: int, alt_aln_method: Optional[str] = None
    ) -> List:
        """
        return transcripts that overlap given region

        :param str alt_ac: reference sequence (e.g., NC_000007.13)
        :param int start_i: 5' bound of region
        :param int end_i: 3' bound of region
        :param str alt_aln_method: OPTIONAL alignment method (e.g., splign)
        """
        url = f"{self.server}/alignments_for_region/{alt_ac}?start_i={start_i}&end_i={end_i}"
        self.optional_parameters(["alt_aln_method"], [alt_aln_method])
        return requests.get(url, timeout=self.timeout).json()

    def get_tx_identity_info(self, tx_ac: str) -> dict:
        """returns features associated with a single transcript.

        :param tx_ac: transcript accession with version (e.g., 'NM_199425.2')
        :type tx_ac: str

        transcripts have the following attributes:
        {
            hgnc           : ATM
            cds_start_i    : 385
            cds_end_i      : 9556
            tx_ac          : NM_000051.3
            alt_ac         : AC_000143.1
            alt_aln_method : splign
            lengths        : {707,79,410}
        }

        """
        url = f"{self.server}/tx_identity_info/{tx_ac}"
        return requests.get(url, timeout=self.timeout).json()

    def get_tx_info(self, tx_ac: str, alt_ac: str, alt_aln_method: str) -> dict:
        """return a single transcript info for supplied accession (tx_ac, alt_ac, alt_aln_method), or None if not found

        :param tx_ac: transcript accession with version (e.g., 'NM_000051.3')
        :type tx_ac: str

        :param alt_ac: specific genomic sequence (e.g., NC_000011.4)
        :type alt_ac: str

        :param alt_aln_method: sequence alignment method (e.g., splign, blat)
        :type alt_aln_method: str

        transcripts have the following attributes:
        {
            hgnc           : ATM
            cds_start_i    : 385
            cds_end_i      : 9556
            tx_ac          : NM_000051.3
            alt_ac         : AC_000143.1
            alt_aln_method : splign
        }

        """
        url = f"{self.server}/tx_info/{tx_ac}/{alt_ac}?alt_aln_method={alt_aln_method}"
        return requests.get(url, timeout=self.timeout).json()

    def get_tx_mapping_options(self, tx_ac: str) -> Union[List[dict], None]:
        """Return all transcript alignment sets for a given transcript
        accession (tx_ac); returns empty list if transcript does not
        exist.  Use this method to discovery possible mapping options
        supported in the database

        :param tx_ac: transcript accession with version (e.g., 'NM_000051.3')
        :type tx_ac: str

        alignment setes have the following attributes:
        {
            tx_ac          : NM_000051.3
            alt_ac         : AC_000143.1
            alt_aln_method : splign
        }

        """
        url = f"{self.server}/tx_mapping_options/{tx_ac}"
        return requests.get(url, timeout=self.timeout).json()

    def get_similar_transcripts(self, tx_ac: str) -> Union[List[dict], None]:
        """Return a list of transcripts that are similar to the given
        transcript, with relevant similarity criteria.

        similar transcripts have the following attributes:
        {
            tx_ac1                 : NM_000051.3
            tx_ac2                 : ENST00000278616
            hgnc_eq                : true
            cds_eq                 : false*
            es_fp_eq               : false
            cds_es_fp_eq           : false*
            cds_exon_lengths_fp_eq : true*
        }
        * = may be null, field is optional

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
        url = f"{self.server}/similar_transcripts/{tx_ac}"
        return requests.get(url, timeout=self.timeout).json()

    def get_pro_ac_for_tx_ac(self, tx_ac: str) -> Union[str, None]:
        """Return the (single) associated protein accession for a given transcript
        accession, or None if not found."""
        url = f"{self.server}/pro_ac_for_tx_ac/{tx_ac}"
        return requests.get(url, timeout=self.timeout).json()

    def get_assembly_map(self, assembly_name: str) -> dict:
        """Return a list of accessions for the specified assembly name (e.g., GRCh38.p5)."""
        url = f"{self.server}/assembly_map/{assembly_name}"
        return requests.get(url, timeout=self.timeout).json()
