import contextlib
import re
from dataclasses import dataclass
from ftplib import FTP, FTP_TLS  # nosec
from functools import cached_property
from typing import Generator, Optional, Union

from vbcore.base import BaseDTO
from vbcore.loggers import VBLoggerMixin
from vbcore.types import OptStr


@dataclass(frozen=True, kw_only=True)
class FTPOptions(BaseDTO):
    host: str
    port: int
    user: OptStr = None
    password: OptStr = None
    timeout: int = 300
    debug: bool = False
    encoding: str = "utf-8"
    tls: bool = False


class FTPHandler(VBLoggerMixin):
    def __init__(self, options: FTPOptions):
        self.options = options

    @cached_property
    def client(self) -> Union[FTP, FTP_TLS]:
        ftp_class = FTP_TLS if self.options.tls else FTP  # nosec
        return ftp_class(timeout=self.options.timeout, encoding=self.options.encoding)

    @contextlib.contextmanager
    def connect(self) -> Generator[FTP, None, None]:
        opts = self.options
        with self.client as ftp:
            ftp.debugging = 3 if opts.debug else 0
            ftp.connect(opts.host, opts.port)
            ftp.login(opts.user, opts.password or "")

            if self.options.tls and isinstance(ftp, FTP_TLS):
                ftp.prot_p()
            yield ftp

    def download_file(self, remote_path: str, local_path: str):
        with self.connect() as conn:
            with open(local_path, "wb") as file:
                self.log.info("downloading '%s' -> '%s'...", remote_path, local_path)
                conn.retrbinary(f"RETR {remote_path}", file.write)

    def upload_file(self, local_path: str, remote_path: str):
        with self.connect() as conn:
            with open(local_path, "rb") as file:
                self.log.info("uploading '%s' -> '%s'...", local_path, remote_path)
                conn.storbinary(f"STOR {remote_path}", file)

    def upload_dir(
        self,
        local_path: str = ".",
        remote_path: str = ".",
        only: Optional[re.Pattern] = None,
        exclude: Optional[re.Pattern] = None,
    ) -> int:
        raise NotImplementedError

    def download_dir(
        self,
        remote_path: str = ".",
        local_path: str = ".",
        only: Optional[re.Pattern] = None,
        exclude: Optional[re.Pattern] = None,
    ) -> int:
        raise NotImplementedError
