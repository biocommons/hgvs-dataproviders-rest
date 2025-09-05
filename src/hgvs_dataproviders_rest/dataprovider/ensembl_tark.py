from src.hgvs_dataproviders_rest.seqfetcher.seqfetcher_ensembl_tark import EnsemblTarkSeqFetcher
from src.hgvs_dataproviders_rest.txdata.txdata_ensembl_tark import EnsemblTarkDataProvider


def connect():
    tx_data_provider = EnsemblTarkDataProvider()
    ensembl_tark_seqfetcher = EnsemblTarkSeqFetcher()
    # EnsemblTark returns Transcripts and Sequences - so we need to hook them together
    ensembl_tark_seqfetcher.set_data_provider(tx_data_provider)

