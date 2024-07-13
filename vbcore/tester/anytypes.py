import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


class AnyType:
    def __init__(self, *types: type[Any]):
        self.types = types

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.types)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        _types = (
            self.types[0].__name__
            if len(self.types) == 1
            else tuple(t.__name__ for t in self.types)
        )
        return f"<{self.__class__.__name__}={_types}>"


ANY_STR: Any = AnyType(str)
ANY_BYTES: Any = AnyType(bytes)
ANY_INT: Any = AnyType(int)
ANY_FLOAT: Any = AnyType(float)
ANY_TUPLE: Any = AnyType(tuple)
ANY_LIST: Any = AnyType(list)
ANY_SET: Any = AnyType(set)
ANY_DICT: Any = AnyType(dict)
ANY_UUID: Any = AnyType(UUID)
ANY_DECIMAL: Any = AnyType(Decimal)
ANY_DATE: Any = AnyType(datetime.date)
ANY_DATETIME: Any = AnyType(datetime.datetime)
