import abc
import typing as t
from dataclasses import dataclass, field

from vbcore.base import BaseDTO
from vbcore.factory import Item
from vbcore.types import BytesType

T = t.TypeVar("T", bound="HashOptions")

HashableType = t.Union[str, BytesType]


@dataclass(frozen=True)
class HashOptions(BaseDTO):
    encoding: str = field(default="utf-8")


class Hasher(Item[T], t.Generic[T]):
    @abc.abstractmethod
    def hash(self, data: HashableType) -> str:
        """
        @param data:
        """

    @abc.abstractmethod
    def verify(
        self, given_hash: str, data: HashableType, raise_exc: bool = False
    ) -> bool:
        """
        @param given_hash:
        @param data:
        @param raise_exc:
        """

    def to_bytes(self, data: str) -> bytes:
        return data.encode(encoding=self.options.encoding)

    def to_string(self, data: bytes) -> str:
        return data.decode(encoding=self.options.encoding)
