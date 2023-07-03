from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import ClassVar, Optional, Type, TypeVar

from vbcore.base import BaseDTO
from vbcore.misc import check_uuid, get_uuid

C = TypeVar("C", bound="ContextMetadata")


@dataclass(frozen=True, kw_only=True)
class ContextMetadata(BaseDTO):
    """
    Helper class that manages context vars with metadata as DTO

    >>> @dataclass(frozen=True)
    ... class MyContext(ContextMetadata):
    ...     id: int
    ...     name: str
    ...
    >>> MyContext.get()  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    LookupError: <ContextVar name='MyContext' at 0x...>
    >>> MyContext.set(id=1, name="name")
    >>> MyContext.get()
    MyContext(id=1, name='name')
    """

    __context: ClassVar[ContextVar]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__context = ContextVar(cls.__name__)

    @classmethod
    def get(cls: Type[C]) -> C:
        return cls.__context.get()

    @classmethod
    def set(cls, metadata: Optional[C] = None, **kwargs) -> None:
        cls.__context.set(metadata if metadata else cls(**kwargs))


@dataclass(frozen=True, kw_only=True)
class ContextCorrelationId(ContextMetadata):
    correlation_id: Optional[str] = field(default=None, kw_only=True)

    @classmethod
    def generate_correlation_id(cls) -> str:
        return str(get_uuid(hex_=False))

    @classmethod
    def check_correlation_id(cls, correlation_id: str) -> bool:
        return check_uuid(correlation_id)
