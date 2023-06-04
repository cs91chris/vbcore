import typing as t
from abc import abstractmethod

from vbcore.base import BaseDTO
from vbcore.factory import Item

D = t.TypeVar("D", bound=BaseDTO)

RecordType = t.Union[dict, t.List[dict]]


class Builder(Item[D], t.Generic[D]):
    @abstractmethod
    def to_self(self, data: t.Any) -> t.Any:
        raise NotImplementedError

    @abstractmethod
    def build(self, data: t.Any) -> t.Any:
        raise NotImplementedError

    def build_from(self, builder: "Builder", data: t.Any) -> t.Any:
        return self.to_self(builder.build(data))


class StringBuilder(Builder[D]):
    @abstractmethod
    def to_string(self, data: RecordType) -> str:
        raise NotImplementedError

    def build(self, data: RecordType) -> str:
        return self.to_string(data)


class DictBuilder(Builder[D]):
    @abstractmethod
    def to_dict(self, data: str) -> RecordType:
        raise NotImplementedError

    def build(self, data: str) -> RecordType:
        return self.to_dict(data)
