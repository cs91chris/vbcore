import logging
import logging.config
import os
import socket
import struct
import typing as t
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from vbcore import json
from vbcore.base import Static
from vbcore.context import ContextCorrelationId, ContextMetadata
from vbcore.files import FileHandler
from vbcore.types import OptStr

ALERT = logging.WARN + 5
TRACE = logging.DEBUG - 5
DEFAULT_LISTENER_PORT = logging.config.DEFAULT_LOGGING_CONFIG_PORT

if t.TYPE_CHECKING:
    LoggerClass = logging.Logger
else:
    LoggerClass = logging.getLoggerClass()


class VBLogger(LoggerClass):
    def alert(self, msg, *args, **kwargs):
        if self.isEnabledFor(ALERT):
            self._log(ALERT, msg, args, **kwargs)

    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(TRACE):
            self._log(TRACE, msg, args, **kwargs)


class VBRootLogger(logging.RootLogger, VBLogger):
    pass


@dataclass(frozen=True, kw_only=True)
class LoggingSettings:
    level: str = "INFO"
    force: bool = True
    config_file: OptStr = None
    listen_for_reload: bool = False
    listener_daemon: bool = True
    listener_port: int = DEFAULT_LISTENER_PORT
    default_date_format = "%Y-%m-%d %H:%M:%S"
    default_format: str = (
        "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(message)s"
    )


class SetupLoggers:
    def __init__(
        self,
        config: t.Optional[LoggingSettings] = None,
        config_file: OptStr = None,
        **kwargs,
    ):
        self.config = config or LoggingSettings()
        self.config_file = config_file or self.config.config_file

        if not self.prepare_file_config():
            self.prepare_basic_config(**kwargs)

        if self.config.listen_for_reload:
            self.prepare_listener()

    def prepare_basic_config(self, **kwargs):
        kwargs.setdefault("force", self.config.force)
        kwargs.setdefault("level", self.config.level)
        kwargs.setdefault("format", self.config.default_format)
        kwargs.setdefault("datefmt", self.config.default_date_format)
        kwargs["level"] = os.environ.get("LOG_LEVEL") or self.config.level
        logging.basicConfig(**kwargs)

    def prepare_file_config(self) -> bool:
        config_file = os.environ.get("LOG_FILE_CONFIG") or self.config_file
        if not config_file:
            return False

        with FileHandler(config_file).open() as file:
            logging.config.dictConfig(json.loads(file.read()))
        return True

    def prepare_listener(self):
        listener = logging.config.listen(
            port=self.config.listener_port,
            verify=self.verify_config_from_socket,
        )
        listener.daemon = self.config.listener_daemon
        listener.start()

    def verify_config_from_socket(self, data: bytes) -> bytes | None:
        # TODO no default implementation provided
        _ = self
        return data

    @classmethod
    def reload(
        cls,
        config_file: str,
        host: str = "localhost",
        port: int = DEFAULT_LISTENER_PORT,
    ):
        with FileHandler(config_file).open_binary() as file:
            configuration = file.read()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.send(bytes(struct.pack(">L", len(configuration))))
        sock.send(configuration)
        sock.close()


class LogContextFilter(logging.Filter):
    _metadata: t.Type[ContextMetadata] = ContextCorrelationId

    def __init__(
        self,
        name: str = "",
        default: str = "-",
        fields: t.Sequence[str] = (),
    ) -> None:
        super().__init__(name)
        self.default = default
        self.fields = fields or self._metadata.field_names()

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            metadata: t.Any = self._metadata.get()
        except LookupError:
            metadata = object()

        for field in self.fields:
            value = getattr(metadata, field, None)
            setattr(record, field, value or self.default)

        return True


class Log(metaclass=Static):
    @classmethod
    def get(cls, name: OptStr = None) -> VBLogger:
        return t.cast(VBLogger, logging.getLogger(name))

    @classmethod
    @contextmanager
    def execution_time(cls, logger: OptStr = None, message: OptStr = None, **kwargs):
        start_time = datetime.now()
        yield

        cls.get(logger).info(
            "%s%s",
            message or "execution time: ",
            datetime.now() - start_time,
            extra=kwargs,
        )


def patch_logging():
    setattr(logging, "ALERT", ALERT)  # noqa: B010
    setattr(logging, "TRACE", TRACE)  # noqa: B010

    logging.addLevelName(ALERT, "ALERT")
    logging.addLevelName(TRACE, "TRACE")
    logging.setLoggerClass(VBLogger)

    __root_logger = VBRootLogger(logging.WARNING)
    logging.Logger.manager = logging.Manager(__root_logger)
    logging.root = __root_logger

    logging.captureWarnings(os.environ.get("LOG_CAPTURE_WARNING", True))
