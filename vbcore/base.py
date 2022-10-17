import logging
from functools import cached_property
from typing import Generic, TypeVar

LogClass = TypeVar("LogClass", bound=logging.Logger)


class LoggerMixin(Generic[LogClass]):
    @classmethod
    def logger(cls) -> LogClass:
        return logging.getLogger(cls.__module__)

    @cached_property
    def log(self) -> LogClass:
        return self.logger()


class BaseLoggerMixin(LoggerMixin[logging.Logger]):
    """default class for logger"""
