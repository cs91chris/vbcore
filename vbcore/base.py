import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Generic, TypeVar

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
