import traceback
from types import TracebackType

from vbcore.types import StrDict


class VBException(Exception):
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

    def to_dict(self) -> StrDict:
        return {
            "error": self.error_type,
            "message": str(self),
            "traceback": self.dump_traceback(),
        }
