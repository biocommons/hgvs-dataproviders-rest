# -*- coding: utf-8 -*-
"""Defines the abstract data provider interface"""

from ..seqfetcher.seqfetcher_interface import SeqFetcherInterface
from ..txdata.txdata_interface import TxDataInterface

class Interface(TxDataInterface, SeqFetcherInterface):
    """ Historical HGVS DataProvider interface (used by HGVS internals) """
    pass
