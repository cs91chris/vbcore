import atexit
import json
import logging.config
import socket
import struct
import typing as t
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from vbcore.files import FileHandler

DEFAULT_FORMAT = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"
DEFAULT_LISTENER_PORT = logging.config.DEFAULT_LOGGING_CONFIG_PORT


@dataclass(frozen=True)
class LoggingSettings:
    level: str = "INFO"
    config_file: t.Optional[str] = None
    listen_for_reload: bool = False
    listener_daemon: bool = True
    listener_port: int = DEFAULT_LISTENER_PORT


class Loggers:
    def __call__(self, name: t.Optional[str] = None):
        return logging.getLogger(name)

    def __init__(self, config: t.Optional[LoggingSettings] = None, **kwargs):
        self.config = config or LoggingSettings()
        if self.config.config_file:
            with FileHandler(self.config.config_file).open() as file:
                logging.config.dictConfig(json.load(file))
        else:
            kwargs.setdefault("level", self.config.level)
            kwargs.setdefault("format", DEFAULT_FORMAT)
            logging.basicConfig(**kwargs)

        if self.config.listen_for_reload:
            listener = logging.config.listen(self.config.listener_port)
            listener.daemon = self.config.listener_daemon
            listener.start()

    @classmethod
    @contextmanager
    def execution_time(
        cls,
        message: t.Optional[str] = None,
        logger_name: str = None,
        **kwargs,
    ):
        start_time = datetime.now()
        yield

        logger = logging.getLogger(logger_name)
        logger.info(
            "%s%s",
            message or "execution time: ",
            datetime.now() - start_time,
            extra=kwargs,
        )

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


valid_ident = logging.config.valid_ident
# noinspection PyUnresolvedReferences
ConvertingDict = logging.config.ConvertingDict  # type: ignore
# noinspection PyUnresolvedReferences
ConvertingList = logging.config.ConvertingList  # type: ignore


class QueueListenerHandler(QueueHandler):
    def __init__(
        self, handlers, respect_handler_level=False, auto_run=True, queue=None
    ):
        queue = self._resolve_queue(queue or Queue(-1))
        super().__init__(queue)
        handlers = self._resolve_handlers(handlers)
        # noinspection PyUnresolvedReferences
        self._listener = QueueListener(
            self.queue, *handlers, respect_handler_level=respect_handler_level
        )
        if auto_run:
            self.start()
            atexit.register(self.stop)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    @staticmethod
    def _resolve_handlers(h):
        if not isinstance(h, ConvertingList):
            return h
        return [h[i] for i in range(len(h))]

    @staticmethod
    def _resolve_queue(q):
        if not isinstance(q, ConvertingDict):
            return q
        if "__resolved_value__" in q:
            return q["__resolved_value__"]

        cname = q.pop("class")
        klass = q.configurator.resolve(cname)
        props = q.pop(".", None) or {}
        kwargs = {k: q[k] for k in q if valid_ident(k)}
        result = klass(**kwargs)
        for name, value in props.items():
            setattr(result, name, value)

        q["__resolved_value__"] = result
        return result
