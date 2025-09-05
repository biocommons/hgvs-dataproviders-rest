import abc
from typing import Optional


class SeqFetcherInterface(abc.ABC):
    @abc.abstractmethod
    def fetch_seq(self, ac: str, start_i: Optional[int] = None, end_i: Optional[int] = None) -> str:
        pass
