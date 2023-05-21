import json
import logging.config
import socket
import struct
import typing as t
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

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
