import contextlib
import os.path
import re
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Generator, Optional, Union

from paramiko import DSSKey, ECDSAKey, Ed25519Key, PKey, RSAKey, SFTPClient, Transport
from paramiko.common import DEFAULT_MAX_PACKET_SIZE, DEFAULT_WINDOW_SIZE

from vbcore.base import BaseDTO
from vbcore.enums import EnumMixin
from vbcore.loggers import VBLoggerMixin
from vbcore.types import OptStr, StrList


class AlgoKeyEnum(EnumMixin, Enum):
    RSA = RSAKey
    DSS = DSSKey
    ECDSA = ECDSAKey
    ED25519 = Ed25519Key


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True, kw_only=True)
class TransportOptions:
    timeout: int = 300
    hostkey: Optional[PKey] = None
    disabled_algorithms: Optional[dict] = None
    default_window_size: int = DEFAULT_WINDOW_SIZE
    default_max_packet_size: int = DEFAULT_MAX_PACKET_SIZE
    server_sig_algs: bool = True
    gss_kex: bool = False
    gss_deleg_creds: bool = True
    gss_host: OptStr = None
    gss_auth: bool = False
    gss_trust_dns: bool = True


@dataclass(frozen=True, kw_only=True)
class SFTPOptions(BaseDTO):
    host: str
    port: int
    user: OptStr = None
    password: OptStr = None
    private_key_file: OptStr = None
    key_type: Union[str, AlgoKeyEnum] = AlgoKeyEnum.RSA
    timeout: int = 300
    debug: bool = False
    encoding: str = "utf-8"


class SFTPHandler(VBLoggerMixin):
    def __init__(
        self,
        options: SFTPOptions,
        transport_options: Optional[TransportOptions] = None,
    ):
        self.options = options
        self.transport_options = transport_options or TransportOptions()

    def prepare_key(self) -> Optional[PKey]:
        if not self.options.private_key_file:
            return None

        key_type = self.options.key_type
        algo_key = AlgoKeyEnum(key_type) if isinstance(key_type, str) else key_type
        return algo_key.value.from_private_key_file(self.options.private_key_file)

    @cached_property
    def sftp(self) -> SFTPClient:
        return SFTPClient.from_transport(self.transport)

    @cached_property
    def transport(self) -> Transport:
        return Transport(
            (self.options.host, self.options.port),
            default_window_size=self.transport_options.default_window_size,
            default_max_packet_size=self.transport_options.default_max_packet_size,
            gss_kex=self.transport_options.gss_kex,
            gss_deleg_creds=self.transport_options.gss_deleg_creds,
            disabled_algorithms=self.transport_options.disabled_algorithms,
            server_sig_algs=self.transport_options.server_sig_algs,
        )

    def connect(self) -> SFTPClient:
        if not self.transport.is_active():
            self.transport.auth_timeout = self.transport_options.timeout
            self.transport.banner_timeout = self.transport_options.timeout
            self.transport.connect(
                username=self.options.user,
                password=self.options.password,
                pkey=self.prepare_key(),
                hostkey=self.transport_options.hostkey,
                gss_host=self.transport_options.gss_host,
                gss_auth=self.transport_options.gss_auth,
                gss_kex=self.transport_options.gss_kex,
                gss_deleg_creds=self.transport_options.gss_deleg_creds,
                gss_trust_dns=self.transport_options.gss_trust_dns,
            )
        return self.sftp

    def disconnect(self) -> None:
        self.sftp.close()
        self.transport.close()

    @contextlib.contextmanager
    def context(self) -> Generator[SFTPClient, None, None]:
        conn = self.connect()
        yield conn
        self.disconnect()

    def walk(self, remote_path: str = ".") -> StrList:
        with self.context() as conn:
            return conn.listdir(path=remote_path)

    def download(self, remote: str, local: str) -> None:
        self.log.info("downloading '%s' -> '%s' ...", remote, local)
        self.sftp.get(remote, local)

    def upload(self, local: str, remote: str) -> None:
        self.log.info("uploading '%s' -> '%s' ...", local, remote)
        self.sftp.put(local, remote)

    def download_file(self, remote: str, local: str) -> None:
        with self.context():
            self.download(remote, local)

    def upload_file(self, local: str, remote: str) -> None:
        with self.context():
            self.upload(local, remote)

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
            self.log.info("file '%s' filtered", filename)
        return is_filtered

    def upload_dir(
        self,
        local_path: str = ".",
        remote_path: str = ".",
        only: Optional[re.Pattern] = None,
        exclude: Optional[re.Pattern] = None,
    ) -> int:
        counter = 0
        with self.context():
            for filename in os.listdir(local_path):
                if self.filter_file(filename, only, exclude):
                    continue

                self.upload(
                    os.path.join(local_path, filename),
                    os.path.join(remote_path, filename),
                )
                counter += 1
        return counter

    def download_dir(
        self,
        remote_path: str = ".",
        local_path: str = ".",
        only: Optional[re.Pattern] = None,
        exclude: Optional[re.Pattern] = None,
    ) -> int:
        counter = 0
        with self.context() as conn:
            for filename in conn.listdir(path=remote_path):
                if self.filter_file(filename, only, exclude):
                    continue

                self.download(
                    os.path.join(remote_path, filename),
                    os.path.join(local_path, filename),
                )
                counter += 1
        return counter
