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
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    @classmethod
    def from_dict(cls, *_, **kwargs) -> Self:
        return cls(
            correlation_id=kwargs["correlation_id"],
            timestamp=float(kwargs["timestamp"]),
        )

    def to_dict(self, *_, **__) -> dict:
        return {k: str(v) for k, v in super().to_dict().items()}


@dataclass(frozen=True, kw_only=True)
class Message(BaseDTO):
    topic: str = field()
    data: bytes = field(default=b"")
    reply: str = field(default="")
    headers: Optional[Header] = field(default=None)
