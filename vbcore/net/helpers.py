import typing as t
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse

from vbcore.base import BaseDTO
from vbcore.types import OptInt, OptStr

ParamsT = t.Dict[str, t.Union[None, str, t.List[str]]]


def parse_query_string(qs: str, allow_multi: bool = True) -> ParamsT:
    result: ParamsT = {}
    for key, value in parse_qs(qs, keep_blank_values=True).items():
        if not allow_multi or len(value) == 1:
            result[key] = value[0] or None
        else:
            result[key] = [v or None for v in value]
    return result


@dataclass(frozen=True)
class Url(BaseDTO):
    protocol: OptStr = None
    hostname: OptStr = None
    port: OptInt = None
    username: OptStr = None
    password: OptStr = None
    path: OptStr = None
    fragment: OptStr = None
    query: OptStr = None
    params: dict = field(default_factory=dict)

    @classmethod
    def from_raw(cls, url: str) -> "Url":
        parsed_url = urlparse(url)
        return cls(
            protocol=parsed_url.scheme or None,
            hostname=parsed_url.hostname or None,
            port=parsed_url.port,
            username=parsed_url.username or None,
            password=parsed_url.password or None,
            path=parsed_url.path or None,
            fragment=parsed_url.fragment or None,
            query=parsed_url.query or None,
            params=cls.parse_query(parsed_url.query),
        )

    @classmethod
    def parse_query(cls, qs: str, allow_multi: bool = True) -> ParamsT:
        return parse_query_string(qs, allow_multi=allow_multi)

    def encode(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        host = f"{self.hostname}" if self.hostname is not None else ""
        port = f":{self.port}" if self.port is not None else ""
        query = f"?{self.query}" if self.query else ""
        frag = f"#{self.fragment}" if self.fragment else ""
        protocol = f"{self.protocol}://" if self.protocol else ""
        return f"{protocol}{auth}{host}{port}{self.path or ''}{query}{frag}"
