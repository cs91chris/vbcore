import dataclasses
import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Dict, Generic, Tuple, Type, TypeVar

LogClass = TypeVar("LogClass", bound=logging.Logger)


class LoggerMixin(Generic[LogClass], ABC):
    @classmethod
    @abstractmethod
    def logger(cls) -> LogClass:
        """returns the logger instance"""

    @cached_property
    def log(self) -> LogClass:
        return self.logger()


class BaseLoggerMixin(LoggerMixin[logging.Logger]):
    @classmethod
    def logger(cls) -> logging.Logger:
        return logging.getLogger(cls.__module__)


# noinspection PyDataclass
class BaseDTO:
    """
    Use this class as mixin for dataclasses
    """

    def __call__(self, *_, **kwargs):
        """implements prototype pattern"""
        return self.__class__.from_dict(**{**self.to_dict(), **kwargs})

    @classmethod
    def field_names(cls) -> Tuple[str, ...]:
        return tuple(f.name for f in dataclasses.fields(cls))

    def to_dict(self, *_, **__) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, *_, **kwargs):
        # noinspection PyArgumentList
        return cls(**{k: v for k, v in kwargs.items() if k in cls.field_names()})


class Singleton(type):
    """
    Makes classes singleton, use this as metaclass, i.e.:

    >>> class MyClass:
    ...     pass
    ...
    >>> class MySingletonClass(MyClass, metaclass=Singleton):
    ...     pass
    ...
    >>> MyClass() is MyClass()
    False
    >>> MySingletonClass() is MySingletonClass()
    True
    """

    # private map of instances
    __instances: Dict[Type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]


class Static(type):
    """
    Makes classes static, use this as metaclass, i.e.:

    >>> class MyStaticClass(metaclass=Static):
    ...     pass
    ...
    >>> MyStaticClass()
    Traceback (most recent call last):
        ...
    TypeError: Can't instantiate class MyStaticClass
    """

    def __call__(cls):
        raise TypeError(f"Can't instantiate class {cls.__name__}")
