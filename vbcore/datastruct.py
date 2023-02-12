import itertools
import time
import typing as t
from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock

from vbcore.base import BaseDTO

T = t.TypeVar("T")
D = t.TypeVar("D", bound="IDict")
OD = t.TypeVar("OD", bound="ObjectDict")


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class IDict(dict):
    def patch(self: D, __dict: D, **kwargs) -> D:
        super().update(__dict, **kwargs)
        return self

    def get_namespace(
        self: D,
        prefix: str,
        lowercase: bool = True,
        trim: bool = True,
    ) -> D:
        """
        Returns a dictionary containing a subset of configuration options
        that match the specified prefix.

        :param prefix: a configuration prefix
        :param lowercase: a flag indicating if the keys should be lowercase
        :param trim: a flag indicating if the keys should include the namespace
        """
        data: D = self.__class__()
        for k, v in self.items():
            if k.startswith(prefix):
                key = k[len(prefix) :] if trim else k
                data[key.lower() if lowercase else key] = v
        return data


class ObjectDict(IDict):
    def __init__(self: OD, seq=None, **kwargs):
        super().__init__()
        self.__setstate__(kwargs if seq is None else dict(seq))

    def __setstate__(self, state: dict):
        for k, v in state.items():
            self.__setattr__(k, v)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def __setattr__(self, name, value):
        self[name] = self.normalize(value, raise_exc=False)

    def __delattr__(self, name):
        if name in self:
            del self[name]

    @classmethod
    def normalize(cls, data, raise_exc=True) -> t.Any:
        # TODO using cls instead of ObjectDict
        def normalize_iterable(_data: t.Any):
            for r in _data:
                yield ObjectDict(**r) if isinstance(r, t.Mapping) else r

        try:
            if isinstance(data, t.Mapping):
                return ObjectDict(**data)

            if isinstance(data, (tuple, list, set)):
                return type(data)(normalize_iterable(data))

            raise TypeError(f"can not convert '{type(data)}' into {cls}")
        except (TypeError, ValueError, AttributeError):
            if raise_exc is True:
                raise
            return data


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


@dataclass
class GeoJsonPoint(BaseDTO):
    coordinates: t.List[float]
    type: str

    def __init__(self, lat: float = 0.0, lon: float = 0.0):
        self.type = "Point"
        self.coordinates = [lon, lat]
        self.lat = lat
        self.lon = lon


class BufferManager(t.Generic[T]):
    def __init__(self, max_size: int = 0):
        self._max_size = max_size
        self._buffer: t.List[T] = []

    @property
    def buffer(self) -> t.List[T]:
        return self._buffer

    @property
    def size(self) -> int:
        return len(self.buffer)

    def pre_flush_hook(self):
        """Derived class can hook at flush time, so it can handle buffered data"""

    def clear(self):
        self.buffer.clear()

    def load(self, record: T) -> int:
        self._buffer.append(record)
        if self._max_size and len(self._buffer) >= self._max_size:
            self.flush()
        return self.size

    def loads(self, records: t.Iterable[T]) -> int:
        for record in records:
            self.load(record)
        return self.size

    def flush(self):
        if self.size > 0:
            self.pre_flush_hook()
            self.clear()


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
        self._lock = RLock()
        self.max_len = max_len
        self.max_age = max_age

    @staticmethod
    def _item_age(item) -> float:
        return time.time() - item[1]

    def __contains__(self, key):
        try:
            with self._lock:
                item = super().__getitem__(key)
                if self._item_age(item) < self.max_age:
                    return True
                del self[key]
        except KeyError:
            pass
        return False

    def __getitem__(self, key, with_age: bool = False):
        with self._lock:
            item = super().__getitem__(key)
            item_age = self._item_age(item)
            if item_age < self.max_age:
                if with_age:
                    return item[0], item_age
                return item[0]
            del self[key]
            raise KeyError(key)

    def __setitem__(self, key, value, set_time=None):
        with self._lock:
            if len(self) == self.max_len:
                if key in self:
                    del self[key]
                else:
                    try:
                        self.popitem(last=False)
                    except KeyError:
                        pass
            super().__setitem__(key, (value, set_time or time.time()))

    def items(self):
        values = []
        for key in list(self.keys()):  # pylint: disable=consider-using-dict-items
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
        for key in list(self.keys()):  # pylint: disable=consider-using-dict-items
            try:
                values.append(self[key])
            except KeyError:
                pass
        return values

    def pop(self, key, default=None):
        with self._lock:
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

    def get(self, key, default=None, with_age: bool = False):
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
            with self._lock:
                del self[key]
        except KeyError:
            pass


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
