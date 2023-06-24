import enum
from typing import List

from vbcore.datastruct import ObjectDict
from vbcore.types import CoupleStr


class EnumMixin:
    __members__: dict

    @classmethod
    def items(cls) -> List[str]:
        return list(cls.__members__.keys())


class IntEnum(enum.IntEnum):
    @classmethod
    def to_list(cls):
        return [
            ObjectDict(id=getattr(cls, m).value, label=getattr(cls, m).name)
            for m in cls.__members__
        ]

    def to_dict(self):
        return ObjectDict(id=self.value, label=self.name)

    def __repr__(self):
        return f"<{self.value}: {self.name}>"

    def __str__(self):
        return self.name


class StrEnum(str, enum.Enum):
    """
    StrEnum is at the same time ``enum.Enum`` and ``str``.
    The ``auto()`` behavior uses the member name as its value.

        >>> import enum

        >>> class MyEnum(StrEnum):
        >>>    EXAMPLE = enum.auto()

        >>> assert MyEnum.EXAMPLE == "example"
        >>> assert MyEnum.EXAMPLE.upper() == "EXAMPLE"
    """

    def __str__(self):
        return self.value

    def __hash__(self):
        return hash(self._name_)  # pylint: disable=no-member

    @classmethod
    def _missing_(cls, value):
        return cls(cls.__members__.get(str(value).upper()))

    def _generate_next_value_(self, *_):  # pylint: disable=arguments-differ
        return self


class LStrEnum(StrEnum):
    """StrEnum with lower values"""

    def _generate_next_value_(self, *_):
        return self.lower()

    def __str__(self):
        return self.value.lower()

    def __hash__(self):
        return hash(self._name_)  # pylint: disable=no-member


class IStrEnum(LStrEnum):
    """StrEnum with lower values and case-insensitive"""

    def _comparable_values(self, other) -> CoupleStr:
        other_value = other if isinstance(other, str) else other.value
        return self.value.lower(), other_value.lower()

    def __hash__(self):
        return hash(self._name_)  # pylint: disable=no-member

    def __eq__(self, other):
        value, other = self._comparable_values(other)
        return value == other

    def __ne__(self, other):
        value, other = self._comparable_values(other)
        return value != other

    def __gt__(self, other):
        value, other = self._comparable_values(other)
        return value > other
