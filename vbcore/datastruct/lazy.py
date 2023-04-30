import typing as t

from vbcore.exceptions import VBException
from vbcore.importer import Importer, ImporterError
from vbcore.types import BytesType, OptStr


class Lazy:
    def __init__(self, callback: t.Callable, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._callback = callback

    def __call__(self, *args, **kwargs) -> t.Any:
        return self._callback(*self._args, **self._kwargs)


class LazyException(Lazy):
    def __init__(self, exception: Exception):
        super().__init__(callback=self.trigger)
        self.exception = exception

    def trigger(self):
        if isinstance(self.exception, VBException):
            raise self.exception from self.exception.orig
        raise self.exception

    def __str__(self) -> str:
        return str(self.exception)

    def __getattr__(self, item):
        self(item)

    def __getitem__(self, item):
        self(item)


class LazyImporter:
    @classmethod
    def do_import(
        cls,
        name: str,
        package: OptStr = None,
        message: OptStr = None,
        subclass_of: t.Optional[t.Type] = None,
        instance_of: t.Optional[t.Type] = None,
    ) -> t.Any:
        try:
            return Importer.from_module(
                name,
                package=package,
                subclass_of=subclass_of,
                instance_of=instance_of,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            exception = ImporterError(message, orig=exc) if message else exc
            return LazyException(exception)

    @classmethod
    def import_many(
        cls,
        *args,
        package: OptStr = None,
        message: OptStr = None,
        subclass_of: t.Optional[t.Type] = None,
        instance_of: t.Optional[t.Type] = None,
    ) -> t.Tuple[t.Any, ...]:
        return tuple(
            cls.do_import(name, package, message, subclass_of, instance_of)
            for name in args
        )


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
