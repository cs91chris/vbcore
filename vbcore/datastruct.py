import enum
import itertools
import time
import typing as t
from collections import OrderedDict
from dataclasses import asdict, dataclass, fields
from threading import RLock

T = t.TypeVar("T")
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
        # pylint: disable=unnecessary-dunder-call
        return self.__setitem__(key, value)


class DataClassDictable:
    def to_dict(self, factory: CallableDictType = ObjectDict) -> dict:
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


# based on: https://github.com/mailgun/expiringdict
class ExpiringCache(OrderedDict):
    """
    Dictionary with auto-expiring values for caching purposes.
    Expiration happens on any access, object is locked during cleanup from expired
    values. Can not store more than max_len elements - the oldest will be deleted.
    The values stored in the following way:
    {
        key1: (value1, created_time1),
        key2: (value2, created_time2)
    }
    NOTE: iteration over dict and also keys() do not remove expired values!
    """

    def __init__(self, max_len: int = 128, max_age: float = 0):
        super().__init__(self)
        self.lock = RLock()
        self.max_len = max_len
        self.max_age = max_age

    def __contains__(self, key):
        try:
            with self.lock:
                item = super().__getitem__(key)
                if self.__item_age(item) < self.max_age:
                    return True
                del self[key]
        except KeyError:
            pass
        return False

    def __getitem__(self, key, with_age: bool = False):
        with self.lock:
            item = super().__getitem__(key)
            item_age = self.__item_age(item)
            if item_age < self.max_age:
                if with_age:
                    return item[0], item_age
                return item[0]
            del self[key]
            raise KeyError(key)

    def __setitem__(self, key, value, set_time=None):
        with self.lock:
            if len(self) == self.max_len:
                if key in self:
                    del self[key]
                else:
                    try:
                        self.popitem(last=False)
                    except KeyError:
                        pass
            super().__setitem__(key, (value, set_time or time.time()))

    @staticmethod
    def __item_age(item) -> int:
        return time.time() - item[1]

    def items(self):
        values = []
        for key in list(self.keys()):
            try:
                values.append((key, self[key]))
            except KeyError:
                pass
        return values

    def items_with_age(self):
        values = []
        for key in list(self.keys()):
            try:
                values.append((key, super().__getitem__(key)))
            except KeyError:
                pass
        return values

    def values(self):
        values = []
        for key in list(self.keys()):
            try:
                values.append(self[key])
            except KeyError:
                pass
        return values

    def pop(self, key, default=None):
        with self.lock:
            try:
                item = super().__getitem__(key)
                del self[key]
                return item[0]
            except KeyError:
                return default

    def ttl(self, key):
        _, key_age = self.get(key, with_age=True)
        if key_age:
            key_ttl = self.max_age - (key_age or 0)
            return key_ttl if key_ttl > 0 else None
        return None

    def get(self, key, default=None, with_age=False):
        try:
            # pylint: disable=unnecessary-dunder-call
            return self.__getitem__(key, with_age)
        except KeyError:
            if with_age:
                return default, None
            return default

    def set(self, key, value, set_time=None):
        # pylint: disable=unnecessary-dunder-call
        self.__setitem__(key, value, set_time=set_time)

    def delete(self, key):
        try:
            with self.lock:
                del self[key]
        except KeyError:
            pass


@dataclass(frozen=True)
class BaseDTO:
    def to_dict(self) -> dict:
        return asdict(self)


class Singleton(type):
    __instances: t.Dict[t.Type, t.Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]


class OrderedSet(t.MutableSet[T]):
    __slots__ = ("_data",)

    def __init__(self, iterable: t.Optional[t.Iterable[T]] = None):
        self._data = dict.fromkeys(iterable) if iterable else {}

    def add(self, value: T) -> None:
        self._data[value] = None

    def clear(self) -> None:
        self._data.clear()

    def discard(self, value: T) -> None:
        self._data.pop(value, None)

    def remove(self, value: T) -> None:
        self._data.pop(value)

    def __getitem__(self, index) -> T:
        try:
            return next(itertools.islice(self._data, index, index + 1))
        except StopIteration as exc:
            raise IndexError(f"index {index} out of range") from exc

    def __contains__(self, x: object) -> bool:
        return self._data.__contains__(x)

    def __len__(self) -> int:
        return self._data.__len__()

    def __iter__(self) -> t.Iterator[T]:
        return self._data.__iter__()

    def __str__(self):
        return f"{{{', '.join(str(i) for i in self)}}}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self}>"
