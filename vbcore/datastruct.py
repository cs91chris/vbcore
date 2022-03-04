import enum

import typing as t
from collections import OrderedDict
from dataclasses import asdict, fields, dataclass

BytesType = t.Union[bytes, bytearray, memoryview]
CallableDictType = t.Callable[[t.List[t.Tuple[str, t.Any]]], t.Any]


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class ObjectDict(dict):
    def __init__(self, seq=None, **kwargs):
        super().__init__()
        self.__setstate__(kwargs if seq is None else dict(seq))

    def __dict__(self):
        data: t.Dict = {}
        for k, v in self.items():
            if hasattr(v, "__dict__"):
                data[k] = v.__dict__()
            elif isinstance(v, list):
                data[k] = [i.__dict__() if hasattr(i, "__dict__") else i for i in v]
            else:
                data[k] = v

        return data

    def __getstate__(self):
        return self.__dict__()  # pylint: disable=not-callable

    def __setstate__(self, state):
        for k, v in state.items():
            self.__setattr__(k, v)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def __setattr__(self, name, value):
        self[name] = self.normalize(value)

    def __delattr__(self, name):
        if name in self:
            del self[name]

    def patch(self, __dict, **kwargs) -> "ObjectDict":
        super().update(__dict, **kwargs)
        return self

    @staticmethod
    def normalize(data: t.Any, raise_exc: bool = False):
        try:
            if isinstance(data, (list, tuple, set)):
                return [ObjectDict(**r) if isinstance(r, dict) else r for r in data]
            return ObjectDict(**data)
        except (TypeError, ValueError, AttributeError):
            if raise_exc is True:
                raise
            return data

    def get_namespace(
        self, prefix: str, lowercase: bool = True, trim: bool = True
    ) -> "ObjectDict":
        """
        Returns a dictionary containing a subset of configuration options
        that match the specified prefix.

        :param prefix: a configuration prefix
        :param lowercase: a flag indicating if the keys should be lowercase
        :param trim: a flag indicating if the keys should include the namespace
        """
        data = ObjectDict()
        for k, v in self.items():
            if k.startswith(prefix):
                key = k[len(prefix) :] if trim else k
                data[key.lower() if lowercase else key] = v
        return data


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

    def _generate_next_value_(self, *_):
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
    """StrEnum with lower values and case insensitive"""

    def _comparable_values(self, other) -> t.Tuple[str, str]:
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


class Dumper:
    def __init__(
        self, data: t.Any, *args, callback: t.Optional[t.Callable] = None, **kwargs
    ):
        self.data = data
        self._args = args
        self._kwargs = kwargs
        self._callback = callback

    def dump(self) -> str:
        data = self.data
        if callable(self._callback):
            data = self._callback(data, *self._args, **self._kwargs)
        return str(data)

    def __str__(self):
        return self.dump()


class BytesWrap(Dumper):
    def __init__(self, data: BytesType, encoding: str = "utf-8"):
        super().__init__(data)
        self.encoding = encoding

    def dump(self) -> str:
        if isinstance(self.data, memoryview):
            return self.data.hex()
        return self.data.decode(encoding=self.encoding)

    def __repr__(self) -> str:
        return self.__str__()


class BDict(dict):
    @classmethod
    def from_dict(cls, data: t.Dict) -> "BDict":
        return cls(**data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inverse = {v: k for k, v in self.items()}

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.inverse[value] = key

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.inverse[self[key]]


class LRUCache(OrderedDict):
    """
    Limit size, evicting the least recently looked-up key when full
    """

    def __init__(self, maxsize: int = 128, **kwargs):
        self.maxsize = maxsize
        super().__init__(**kwargs)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]

    def set(self, key, value):
        return self.__setitem__(key, value)


class DataClassDictable:
    def to_dict(self, factory: CallableDictType = ObjectDict, **__) -> dict:
        # noinspection PyDataclass
        return asdict(self, dict_factory=factory)

    @classmethod
    def field_types(cls) -> dict:
        # noinspection PyDataclass
        return {item.name: item.type.__name__ for item in fields(cls)}


@dataclass
class GeoJsonPoint(DataClassDictable):
    coordinates: t.List[float]
    type: str

    def __init__(self, lat: float = 0.0, lon: float = 0.0):
        self.type = "Point"
        self.coordinates = [lon, lat]
        self.lat = lat
        self.lon = lon


class BufferManager:
    def __init__(self, max_size: int = 0):
        self._max_size = max_size
        self._buffer: list = []

    @property
    def buffer(self) -> list:
        return self._buffer

    def buffer_flush_hook(self):
        """Derived class can hook at flush time, so it can handle buffered data"""

    def buffer_load(self, record):
        self._buffer.append(record)
        if self._max_size and len(self._buffer) >= self._max_size:
            self.buffer_flush()

    def buffer_flush(self):
        if self._buffer:
            self.buffer_flush_hook()
            self._buffer.clear()
