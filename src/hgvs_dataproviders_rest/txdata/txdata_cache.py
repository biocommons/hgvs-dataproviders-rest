from functools import lru_cache

from src.hgvs_dataproviders_rest.txdata.txdata_interface import TxDataInterface


class TxDataCache(TxDataInterface):
    def __init__(self, object: TxDataInterface):
        super().__init__()
        self._object = object

    @lru_cache
    def data_version(self):
        return self._object.data_version()

    @lru_cache
    def schema_version(self):
        return self._object.schema_version()

    @lru_cache
    def get_acs_for_protein_seq(self, seq):
        return self._object.get_acs_for_protein_seq(seq)

    @lru_cache
    def get_assembly_map(self, assembly_name):
        return self._object.get_assembly_map(assembly_name)

    @lru_cache
    def get_gene_info(self, gene):
        return self._object.get_gene_info(gene)

    @lru_cache
    def get_pro_ac_for_tx_ac(self, tx_ac):
        return self._object.get_pro_ac_for_tx_ac(tx_ac)

    @lru_cache
    def get_similar_transcripts(self, tx_ac):
        return self._object.get_similar_transcripts(tx_ac)

    @lru_cache
    def get_tx_exons(self, tx_ac, alt_ac, alt_aln_method):
        return self.get_tx_exons(tx_ac, alt_ac, alt_aln_method)

    @lru_cache
    def get_tx_for_gene(self, gene):
        return self._object.get_tx_for_gene(gene)

    @lru_cache
    def get_tx_for_region(self, alt_ac, alt_aln_method, start_i, end_i):
        return self._object.get_tx_for_region(alt_ac, alt_aln_method, start_i, end_i)

    @lru_cache
    def get_tx_identity_info(self, tx_ac):
        return self._object.get_tx_identity_info(tx_ac)

    @lru_cache
    def get_tx_info(self, tx_ac, alt_ac, alt_aln_method):
        return self._object.get_tx_info(tx_ac, alt_ac, alt_aln_method)

    @lru_cache
    def get_tx_mapping_options(self, tx_ac):
        return self._object.get_tx_mapping_options(tx_ac)
