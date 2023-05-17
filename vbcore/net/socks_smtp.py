import enum
import typing as t
from smtplib import SMTP

import socks


class ProxyType(enum.Enum):
    PROXY_TYPE_HTTP = socks.PROXY_TYPE_HTTP
    PROXY_TYPE_SOCKS4 = socks.PROXY_TYPE_SOCKS4
    PROXY_TYPE_SOCKS5 = socks.PROXY_TYPE_SOCKS5


class SocksSMTP(SMTP):
    def __init__(
        self,
        host: str,
        port: int,
        timeout: int = 10,
        local_hostname=None,
        source_address=None,
        proxy_type: t.Optional[ProxyType] = None,
        **kwargs,
    ):
        self.proxy_args = kwargs
        self.proxy_type = proxy_type
        super().__init__(host, port, local_hostname, timeout, source_address)

    def create_socks_connection(
        self, host: str, port: int, timeout: int
    ) -> socks.socksocket:
        if self.proxy_type is None:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            get_socket = super()._get_socket  # type: ignore
            return get_socket(host, port, timeout)

        if self.debuglevel > 0:
            # noinspection PyUnresolvedReferences
            print_debug = self._print_debug  # type: ignore
            print_debug("connect to:", (host, port), self.source_address)

        return socks.create_connection(
            (host, port),
            timeout=timeout,
            source_address=self.source_address,
            proxy_type=self.proxy_type.value,
            **self.proxy_args,
        )

    def _get_socket(self, host: str, port: int, timeout: int) -> socks.socksocket:
        return self.create_socks_connection(host, port, timeout)
