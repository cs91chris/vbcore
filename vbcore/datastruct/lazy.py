import typing as t

from vbcore.types import BytesType


class Lazy:
    def __init__(self, callback: t.Callable, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._callback = callback

    def __call__(self, *args, **kwargs):
        return self._callback(*self._args, **self._kwargs)


class LazyException(Lazy):
    def __init__(self, exception: Exception):
        super().__init__(callback=self.trigger)
        self.exception = exception

    def trigger(self):
        raise self.exception

    def __str__(self) -> str:
        return str(self.exception)

    def __getattr__(self, item):
        self(item)

    def __getitem__(self, item):
        self(item)


class LazyDump(Lazy):
    def __str__(self):
        return self()


class Dumper(Lazy):
    def __init__(
        self, data: t.Any, *args, callback: t.Optional[t.Callable] = None, **kwargs
    ):
        super().__init__(callback or str, data, *args, **kwargs)
        self.data = data

    def dump(self) -> str:
        return self(self.data)

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
