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
    drain: bool = True


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
        servers = self.options.servers
        if isinstance(self.options.servers, (tuple, set)):
            # force to list because nats-py raises error
            servers = list(self.options.servers)

        await self.client.connect(
            servers,
            connect_timeout=int(self.options.timeout),
            disconnected_cb=self.callback_disconnected,
            closed_cb=self.callback_closed,
            discovered_server_cb=self.callback_discovered,
            reconnected_cb=self.callback_reconnected,
        )
        try:
            yield self
        finally:
            if self.options.drain:
                await self.client.drain()
            else:
                await self.client.close()

    async def callback_disconnected(self) -> None:
        self.log.info("[nats-client=%s] disconnected", self.client.client_id)

    async def callback_closed(self) -> None:
        self.log.info("[nats-client=%s] closed", self.client.client_id)

    async def callback_discovered(self) -> None:
        self.log.info("[nats-client=%s] discovered server", self.client.client_id)

    async def callback_reconnected(self) -> None:
        self.log.info("[nats-client=%s] reconnected", self.client.client_id)

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
            "[nats-client=%s] nack sent on reply %s and delayed for %ss",
            self.client.client_id,
            message.reply,
            self.options.nack_delay,
        )

    async def _ack_on_success(self, message: Msg) -> None:
        await message.ack()
        self.log.debug(
            "[nats-client=%s] ack sent on reply %s",
            self.client.client_id,
            message.reply,
        )
