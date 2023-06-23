import traceback
import typing as t
from types import TracebackType

from vbcore.types import OptStr


class VBException(Exception):
    def __init__(
        self,
        message: str,
        *args,
        orig: t.Optional[Exception] = None,
        **kwargs,
    ) -> None:
        super().__init__(message, *args)
        self.orig = orig
        self.message = message
        self.kwargs = kwargs

    @property
    def error_type(self) -> str:
        return self.__class__.__name__

    @property
    def cause(self) -> BaseException:
        return self.__cause__

    @property
    def traceback(self) -> TracebackType:
        return self.__traceback__

    def dump_traceback(self) -> str:
        return "\n".join(traceback.format_exception(self))


class VBEmptyFileError(VBException):
    def __init__(self, filename: str, *args, message: OptStr = None, **kwargs):
        self.filename = filename
        _message = message or "empty file"
        super().__init__(_message, *args, **kwargs)
