import abc
import typing as t

from vbcore.base import BaseDTO
from vbcore.factory import Item

T = t.TypeVar("T", bound=BaseDTO)


class Crypto(Item[T], t.Generic[T]):
    @abc.abstractmethod
    def hash(self, data: str) -> str:
        pass

    @abc.abstractmethod
    def verify(self, given_hash: str, data: str, exc: bool = False) -> bool:
        pass
