# UTA Rest
"""implements a hgvs data provider interface using a REST interface for UTA
(https://github.com/biocommons/uta-rest)

which uses:
(https://github.com/biocommons/uta)

"""

import restapi
import requests
import uvicorn
from hgvs.dataproviders.interface import Interface

def connect():
    return UTAREST("http://127.0.0.1:8000")

class UTAREST(Interface):
    required_version = "1.0"
    
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
        # TODO: see uta.py
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

    def __init__(self, server_url, mode=None, cache=None):
        self.server = server_url
        self._connect()
        super(UTAREST, self).__init__(mode, cache)
        
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
        
    def _connect(self):
        return
        
    ############################################################################
    # Queries
    
    def data_version(self):
        return "uta_20180821"
    
    def schema_version(self):
        return "1.0"
    
    def optional_parameters(self, names: list, params: list) -> str:
        if not len(names) == len(params): 
            raise Exception("Ensure there is a matching value for each parameter name.")
        retval = ""
        no_params = True
        for (param, name) in zip(params, names):
            if not param == None:
                if no_params:
                    retval += "?"
                else:
                    retval += "&"
                retval += ("{name}={param}").format(name=name,param=param)
                no_params = False
        return retval
    
    #print(optional_parameters(["start_i", "end_i", "align_method"], [0, 1, "splign"]))
    
    def get_seq(self, ac, start_i=None, end_i=None):
        url = ("{serv}/seq/{ac}").format(serv=self.server,ac=ac)
        url += self.optional_parameters(["start_i", "end_i"], [start_i, end_i])
        return requests.get(url)    
    
    def get_acs_for_protein_seq(self, seq):
        """
        returns a list of protein accessions for a given sequence.  The
        list is guaranteed to contain at least one element with the
        MD5-based accession (MD5_01234abc...def56789) at the end of the
        list.
        """
        url = ("{serv}/acs_for_protein_seq/{seq}").format(serv=self.server,seq=seq)
        return requests.get(url)
    
    def get_gene_info(self, gene):
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
        url = ("{serv}/gene_info/{gene}").format(serv=self.server,gene=gene)
        return requests.get(url)
    
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
        url = (
            "{serv}/tx_exons/{tx_ac}/{alt_ac}?alt_aln_method={alt_aln_method}"
        ).format(
            serv=self.server,
            tx_ac=tx_ac,
            alt_ac=alt_ac,
            alt_aln_method=alt_aln_method
        )
        return requests.get(url)
    
    def get_tx_for_gene(self, gene):
        """
        return transcript info records for supplied gene, in order of decreasing length

        :param gene: HGNC gene name
        :type gene: str
        """
        url = ("{serv}/tx_for_gene/{gene}").format(serv=self.server,gene=gene)
        return requests.get(url)
    
    def get_tx_for_region(self, alt_ac, alt_aln_method, start_i, end_i):
        """
        return transcripts that overlap given region

        :param str alt_ac: reference sequence (e.g., NC_000007.13)
        :param str alt_aln_method: alignment method (e.g., splign)
        :param int start_i: 5' bound of region
        :param int end_i: 3' bound of region
        """
        url = (
            "{serv}/tx_for_region/{alt_ac}?alt_aln_method={alt_aln_method}&start_i={start_i}&end_i={end_i}"
        ).format(
            serv=self.server,
            alt_ac=alt_ac,
            alt_aln_method=alt_aln_method,
            start_i=start_i,
            end_i=end_i
        )
        return requests.get(url)
    
    def get_alignments_for_region(self, alt_ac, start_i, end_i, alt_aln_method=None):
        """
        return transcripts that overlap given region

        :param str alt_ac: reference sequence (e.g., NC_000007.13)
        :param int start_i: 5' bound of region
        :param int end_i: 3' bound of region
        :param str alt_aln_method: OPTIONAL alignment method (e.g., splign)
        """
        url = (
            "{serv}/alignments_for_region/{alt_ac}?start_i={start_i}&end_i={end_i}"
        ).format(
            serv=self.server,
            alt_ac=alt_ac,
            start_i=start_i,
            end_i=end_i
        )
        self.optional_parameters(["alt_aln_method"], [alt_aln_method])
        """
        Technically fewer lines of execution
        if not alt_aln_method == None:
            url += ("alt_aln_method={alt_aln_method}").format(alt_aln_method=alt_aln_method)
        """
        return requests.get(url)
    
    def get_tx_identity_info(self, tx_ac):
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
        url = ("{serv}/tx_identity_info/{tx_ac}").format(serv=self.server,tx_ac=tx_ac)
        return requests.get(url)
    
    def get_tx_info(self, tx_ac, alt_ac, alt_aln_method):
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
        url = (
            "{serv}/tx_info/{tx_ac}/{alt_ac}?alt_aln_method={alt_aln_method}"
        ).format(
            serv=self.server,
            tx_ac=tx_ac,
            alt_ac=alt_ac,
            alt_aln_method=alt_aln_method
        )
        return requests.get(url)
    
    def get_tx_mapping_options(self, tx_ac):
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
        url = ("{serv}/tx_mapping_options/{tx_ac}").format(serv=self.server,tx_ac=tx_ac)
        return requests.get(url)
    
    def get_similar_transcripts(self, tx_ac):
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
        url = ("{serv}/similar_transcripts/{tx_ac}").format(serv=self.server,tx_ac=tx_ac)
        return requests.get(url)
    
    def get_pro_ac_for_tx_ac(self, tx_ac):
        """Return the (single) associated protein accession for a given transcript
        accession, or None if not found."""
        url = ("{serv}/pro_ac_for_tx_ac/{tx_ac}").format(serv=self.server,tx_ac=tx_ac)
        return requests.get(url)
    
    def get_assembly_map(self, assembly_name):
        """Return a list of accessions for the specified assembly name (e.g., GRCh38.p5)."""
        url = ("{serv}/assembly_map/{assembly_name}").format(serv=self.server,assembly_name=assembly_name)
        return requests.get(url)
    