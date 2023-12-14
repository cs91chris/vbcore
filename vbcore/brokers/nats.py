from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, cast, Optional

from nats import NATS
from nats.aio.msg import Msg
from nats.errors import (
    ConnectionClosedError,
    NoServersError,
    TimeoutError as NatsTimeoutError,
)
from nats.js import JetStreamContext
from typing_extensions import Self

from vbcore.types import OptStr

from .base import BrokerClient, Callback
from .data import BrokerOptions, Header, Message


@dataclass(frozen=True, kw_only=True)
class NatsOptions(BrokerOptions):
    consumer_group: OptStr = None
    nack_delay: int = 30


class NatsBrokerAdapter(BrokerClient[NATS, NatsOptions]):
    retryable_errors = (
        ConnectionClosedError,
        NatsTimeoutError,
        NoServersError,
    )

    def instance(self) -> NATS:
        return NATS()

    @property
    def stream(self) -> JetStreamContext:
        return self.client.jetstream()

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[Self]:
        # force to list because nats-py raise error
        servers = list(self.options.servers)
        await self.client.connect(servers, connect_timeout=int(self.options.timeout))
        try:
            yield self
        finally:
            await self.client.close()

    def _wrap_message(self, message: Msg) -> Message:
        return Message(
            topic=message.subject,
            data=message.data,
            reply=message.reply,
            headers=Header.from_dict(**message.headers) if message.headers else None,
        )

    async def _publish(
        self, topic: str, message: Any, headers: Optional[Header] = None, **kwargs
    ) -> None:
        await self.stream.publish(
            subject=topic,
            payload=message,
            timeout=self.options.timeout,
            headers=headers.to_dict() if headers else None,  # type: ignore
            **kwargs,
        )

    async def _subscribe(self, topic: str, callback: Callback, **kwargs) -> None:
        queue = None
        if self.options.consumer_group:
            queue = f"{self.options.consumer_group}_{topic.replace('.', '-')}"

        _callback = cast(Optional[Callable[[Msg], Awaitable[None]]], callback)
        await self.stream.subscribe(subject=topic, queue=queue, cb=_callback, **kwargs)

    async def _nak_on_failure(self, message: Msg) -> None:
        await message.nak(self.options.nack_delay)
        self.log.error(
            "nack sent on reply %s and delayed for %ss", message.reply, self.options.nack_delay
        )

    async def _ack_on_success(self, message: Msg) -> None:
        await message.ack()
        self.log.debug("ack sent on reply %s", message.reply)
