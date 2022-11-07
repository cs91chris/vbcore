import typing as t
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse

from vbcore.base import BaseDTO

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
    protocol: str
    hostname: str
    port: t.Optional[int] = None
    username: t.Optional[str] = None
    password: t.Optional[str] = None
    path: t.Optional[str] = None
    fragment: t.Optional[str] = None
    query: t.Optional[str] = None
    params: dict = field(default_factory=dict)

    @classmethod
    def from_raw(cls, url: str) -> "Url":
        parsed_url = urlparse(url)
        return cls(
            protocol=parsed_url.scheme,
            hostname=parsed_url.hostname,
            port=parsed_url.port,
            username=parsed_url.username or None,
            password=parsed_url.password or None,
            path=parsed_url.path or None,
            fragment=parsed_url.fragment or None,
            query=parsed_url.query or None,
            params=parse_query_string(parsed_url.query),
        )

    def encode(self):
        auth = f"{self.username}:{self.password}@" if self.username else ""
        port = f":{self.port}" if self.port is not None else ""
        query = f"?{self.query}" if self.query else ""
        fragment = f"#{self.fragment}" if self.fragment else ""
        return (
            f"{self.protocol}://{auth}{self.hostname}{port}"
            f"{self.path or ''}{query}{fragment}"
        )
