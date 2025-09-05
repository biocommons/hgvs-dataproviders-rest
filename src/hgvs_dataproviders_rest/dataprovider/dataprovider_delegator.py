from typing import Optional

from src.hgvs_dataproviders_rest.dataprovider.dataprovider_interface import Interface
from src.hgvs_dataproviders_rest.seqfetcher.seqfetcher_interface import SeqFetcherInterface
from src.hgvs_dataproviders_rest.txdata.txdata_interface import TxDataInterface


class DataProviderDelegator(Interface):
    """
        This class implements the historical HGVS DataProvider (Interface) by delegating to
        a tx_data and seqfetcher objects
    """
    def __init__(self, tx_data: TxDataInterface, seqfetcher: SeqFetcherInterface):
        super().__init__()
        self._tx_data = tx_data
        self._seqfetcher = seqfetcher

    def data_version(self):
        return self._tx_data.data_version()

    def schema_version(self):
        return self._tx_data.schema_version()

    def get_acs_for_protein_seq(self, seq):
        return self._tx_data.get_acs_for_protein_seq(seq)

    def get_assembly_map(self, assembly_name):
        return self._tx_data.get_assembly_map(assembly_name)

    def get_gene_info(self, gene):
        return self._tx_data.get_gene_info(gene)

    def get_pro_ac_for_tx_ac(self, tx_ac):
        return self._tx_data.get_pro_ac_for_tx_ac(tx_ac)

    def get_similar_transcripts(self, tx_ac):
        return self._tx_data.get_similar_transcripts(tx_ac)

    def get_tx_exons(self, tx_ac, alt_ac, alt_aln_method):
        return self._tx_data.get_tx_exons(tx_ac, alt_ac, alt_aln_method)

    def get_tx_for_gene(self, gene):
        return self._tx_data.get_tx_for_gene(gene)

    def get_tx_for_region(self, alt_ac, alt_aln_method, start_i, end_i):
        return self._tx_data.get_tx_for_region(alt_ac, alt_aln_method, start_i, end_i)

    def get_tx_identity_info(self, tx_ac):
        return self._tx_data.get_tx_identity_info(tx_ac)

    def get_tx_info(self, tx_ac, alt_ac, alt_aln_method):
        return self._tx_data.get_tx_info(tx_ac, alt_ac, alt_aln_method)

    def get_tx_mapping_options(self, tx_ac):
        return self._tx_data.get_tx_mapping_options(tx_ac)

    def fetch_seq(self, ac: str, start_i: Optional[int] = None, end_i: Optional[int] = None) -> str:
        return self._seqfetcher.fetch_seq(ac, start_i, end_i)


