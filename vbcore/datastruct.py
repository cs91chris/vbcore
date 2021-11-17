import enum

import typing as t
from collections import OrderedDict
from dataclasses import asdict, fields, dataclass

BytesType = t.Union[bytes, bytearray, memoryview]


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class ObjectDict(dict):
    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            self[k] = self.normalize(v)

    def __dict__(self):
        data: t.Dict = {}
        for k, v in self.items():
            if isinstance(v, ObjectDict):
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

    def patch(self, m, **kwargs):
        """

        :param m:
        :param kwargs:
        :return:
        """
        super().update(m, **kwargs)
        return self

    @staticmethod
    def normalize(
        data: t.Union[t.Iterable, t.Dict]
    ) -> t.Union["ObjectDict", t.Iterable, t.Dict]:
        """

        :param data:
        :return:
        """
        try:
            if isinstance(data, dict):
                return ObjectDict(**data)
            if isinstance(data, str):
                return data
            return [ObjectDict(**r) if isinstance(r, dict) else r for r in data]
        except (TypeError, ValueError, AttributeError):
            return data

    def get_namespace(
        self, prefix: str, lowercase: bool = True, trim: bool = True
    ) -> t.Dict:
        """
        Returns a dictionary containing a subset of configuration options
        that match the specified prefix.

        :param prefix: a configuration prefix
        :param lowercase: a flag indicating if the keys should be lowercase
        :param trim: a flag indicating if the keys should include the namespace
        """
        res = {}
        for k, v in self.items():
            if k.startswith(prefix):
                key = k[len(prefix) :] if trim else k
                res[key.lower() if lowercase else key] = v
        return res


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


class Dumper:
    def __init__(self, data, *args, callback: t.Optional[t.Callable] = None, **kwargs):
        """

        :param data:
        :param callback:
        :param args:
        :param kwargs:
        """
        self.data = data
        self._args = args
        self._kwargs = kwargs
        self._callback = callback

    def dump(self):
        if self._callback is not None:
            return self._callback(self.data, *self._args, **self._kwargs)
        return str(self.data)

    def __str__(self):
        return self.dump()


class BytesWrap:
    encoding = "utf-8"

    def __init__(self, data: BytesType, **__):
        self.data = data

    def __str__(self) -> str:
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
    def to_dict(self, **__) -> dict:
        # noinspection PyDataclass
        return asdict(self)

    @classmethod
    def field_types(cls) -> dict:
        # noinspection PyDataclass
        return {item.name: item.type.__name__ for item in fields(cls)}


@dataclass
class GeoJsonPoint(DataClassDictable):
    coordinates: t.List[float]
    type: str

    def __init__(self, lat=0.0, lon=0.0):
        self.type = "Point"
        self.coordinates = [lon, lat]
