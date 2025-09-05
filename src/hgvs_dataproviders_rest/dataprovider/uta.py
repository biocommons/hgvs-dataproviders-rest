from src.hgvs_dataproviders_rest.dataprovider.dataprovider_delegator import DataProviderDelegator
from src.hgvs_dataproviders_rest.seqfetcher.seqfetcher import SeqFetcher
from src.hgvs_dataproviders_rest.txdata.txdata_cache import TxDataCache
from src.hgvs_dataproviders_rest.txdata.uta import UTA_postgresql


def connect(url):
    # This is mostly just an example and will likely live in HGVS

    tx_data = TxDataCache(UTA_postgresql(url))
    seqfetcher = SeqFetcher()
    return DataProviderDelegator(tx_data, seqfetcher)
