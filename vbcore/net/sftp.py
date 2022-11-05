import contextlib
import os.path
import re
from dataclasses import dataclass
from typing import cast, Generator, Optional

from paramiko import PKey, SFTPClient, Transport


@dataclass(frozen=True)
class SFTPOptions:
    host: str
    port: int
    user: str
    password: Optional[str] = None
    host_key: Optional[str] = None


class SFTPHandler:
    def __init__(self, options: SFTPOptions):
        self.host = options.host
        self.port = options.port
        self.user = options.user
        self.password = options.password
        self.host_key = PKey(data=options.host_key) if options.host_key else None

        self.sftp: Optional[SFTPClient] = None
        self.transport: Optional[Transport] = None

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()

    def connect(self) -> SFTPClient:
        if (
            self.sftp is None
            or self.transport is None
            or not self.transport.is_active()
        ):
            self.transport = Transport((self.host, self.port))
            self.transport.connect(self.host_key, self.user, self.password)
            self.sftp = SFTPClient.from_transport(self.transport)
        return cast(SFTPClient, self.sftp)

    @contextlib.contextmanager
    def context(self) -> Generator[SFTPClient, None, None]:
        conn = self.connect()
        yield conn
        self.disconnect()

    def download_file(self, remote: str, local: str, **kwargs):
        with self.context() as conn:
            conn.get(remote, local, **kwargs)

    def upload_file(self, local: str, remote: str, **kwargs):
        with self.context() as conn:
            conn.put(local, remote, **kwargs)

    def filter_file(
        self,
        filename: str,
        only: Optional[re.Pattern] = None,
        exclude: Optional[re.Pattern] = None,
    ) -> bool:
        is_filtered = bool(
            exclude and exclude.match(filename) or only and not only.match(filename)
        )
        if is_filtered:
            self.sftp.logger.info("file '%s' filtered")
        return is_filtered

    def upload_dir(
        self,
        local_path: str = ".",
        remote_path: str = ".",
        only: Optional[re.Pattern] = None,
        exclude: Optional[re.Pattern] = None,
        **kwargs,
    ) -> int:
        counter = 0
        with self.context() as conn:
            for filename in os.listdir(local_path):
                local_file = os.path.join(local_path, filename)
                remote_file = os.path.join(remote_path, filename)

                if self.filter_file(filename, only, exclude):
                    continue

                conn.put(remote_file, local_file, **kwargs)
                counter += 1
        return counter

    def download_dir(
        self,
        remote_path: str = ".",
        local_path: str = ".",
        only: Optional[re.Pattern] = None,
        exclude: Optional[re.Pattern] = None,
        **kwargs,
    ) -> int:
        counter = 0
        with self.context() as conn:
            for filename in conn.listdir(path=remote_path):
                local_file = os.path.join(local_path, filename)
                remote_file = os.path.join(remote_path, filename)

                if self.filter_file(filename, only, exclude):
                    continue

                conn.get(remote_file, local_file, **kwargs)
                counter += 1
        return counter
