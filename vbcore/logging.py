import atexit
import json
import logging.config
import socket
import struct
import timeit
import typing as t
from contextlib import contextmanager
from datetime import timedelta
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

DEFAULT_LISTENER_PORT = logging.config.DEFAULT_LOGGING_CONFIG_PORT


class LoggingSettings(t.NamedTuple):
    level: str = "WARNING"
    config_file: t.Optional[str] = None
    logger_name: t.Optional[str] = None
    listen_for_reload: bool = False
    listener_daemon: bool = True
    listener_port: int = DEFAULT_LISTENER_PORT


class Loggers:
    def __call__(self, name: t.Optional[str] = None):
        return logging.getLogger(name)

    def __init__(self, config: t.Optional[LoggingSettings] = None, **kwargs):
        self.config = config or LoggingSettings()
        if self.config.config_file:
            with open(self.config.config_file, encoding="utf-8") as file:
                logging.config.dictConfig(json.load(file))
        else:
            kwargs.setdefault("level", self.config.level)
            logging.basicConfig(**kwargs)

        if self.config.listen_for_reload:
            listener = logging.config.listen(self.config.listener_port)
            listener.setDaemon(self.config.listener_daemon)
            listener.start()

    @staticmethod
    @contextmanager
    def execution_time(
        message: t.Optional[str] = None,
        logger_name: str = __name__,
        **kwargs,
    ):
        start_time = timeit.default_timer()
        yield

        logger = logging.getLogger(logger_name)
        logger.info(
            "%s%s",
            message or "execution time: ",
            timedelta(seconds=timeit.default_timer() - start_time),
            extra=kwargs,
        )

    @classmethod
    def reload(
        cls,
        config_file: str,
        host: str = "localhost",
        port: int = DEFAULT_LISTENER_PORT,
    ):
        with open(config_file, "rb") as file:
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
        self, handlers, respect_handler_level=False, auto_run=True, queue=Queue(-1)
    ):
        queue = self._resolve_queue(queue)
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
