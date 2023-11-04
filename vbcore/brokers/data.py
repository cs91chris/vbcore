import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union

from typing_extensions import Self

from vbcore.base import BaseDTO


@dataclass(frozen=True, kw_only=True)
class BrokerOptions(BaseDTO):
    servers: Union[str, list[str]] = field()
    timeout: float = field(default=3)


@dataclass(frozen=True, kw_only=True)
class Header(BaseDTO):
    @staticmethod
    def default_correlation_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def current_timestamp() -> float:
        return datetime.now().timestamp()

    correlation_id: str = field(default_factory=default_correlation_id)
    timestamp: float = field(default_factory=current_timestamp)

    @classmethod
    def from_dict(cls, *_, **kwargs) -> Self:
        return cls(
            correlation_id=kwargs.get("correlation_id") or cls.default_correlation_id(),
            timestamp=float(kwargs.get("timestamp") or cls.current_timestamp()),
        )

    def to_dict(self, *_, **__) -> dict:
        return {k: str(v) for k, v in super().to_dict().items()}


@dataclass(frozen=True, kw_only=True)
class Message(BaseDTO):
    topic: str = field()
    data: bytes = field(default=b"")
    reply: str = field(default="")
    headers: Optional[Header] = field(default=None)
