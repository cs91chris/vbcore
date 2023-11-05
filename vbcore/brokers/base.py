import functools
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any, Generic, Optional, Type, TypeVar

from typing_extensions import Self

from vbcore.context import ContextCorrelationId, ContextMetadata
from vbcore.loggers import VBLoggerMixin

from ..datastruct.lazy import JsonDumper
from .data import BrokerOptions, Header, Message

C = TypeVar("C")
P = TypeVar("P", bound=BrokerOptions)
Callback = Callable[[Message], Awaitable[None]]


class BrokerClient(VBLoggerMixin, ABC, Generic[C, P]):
    def __init__(self, options: P, context: Type[ContextMetadata] = ContextCorrelationId):
        self._client: Optional[C] = None
        self.options = options
        self.context = context

    @functools.cached_property
    def client(self) -> C:
        return self.instance()

    @abstractmethod
    def instance(self) -> C:
        raise NotImplementedError  # pragma: no cover

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[Self]:
        yield self

    @abstractmethod
    def _wrap_message(self, message: Any) -> Message:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def _publish(
        self, topic: str, message: Any, headers: Optional[Header] = None, **kwargs
    ) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def _subscribe(self, topic: str, callback: Callback, **kwargs) -> None:
        raise NotImplementedError  # pragma: no cover

    async def _nak_on_failure(self, message: Any) -> None:
        pass  # pragma: no cover

    async def _ack_on_success(self, message: Any) -> None:
        pass  # pragma: no cover

    async def pre_callback_hook(self) -> None:
        pass  # pragma: no cover

    async def post_callback_hook(self) -> None:
        pass  # pragma: no cover

    async def publish(
        self, topic: str, message: Any, headers: Optional[Header] = None, **kwargs
    ) -> None:
        _headers = headers or Header()
        await self._publish(topic, message, _headers, **kwargs)
        self.log.debug(
            "successfully published: topic=%s header=%s message=%s",
            topic,
            JsonDumper(_headers),
            message,
        )

    async def subscribe(self, topic: str, callback: Callback, **kwargs) -> None:
        cb = self.acknowledge(self.wrap_message(callback))
        await self._subscribe(topic, cb, **kwargs)
        self.log.info("successfully subscribed: topic=%s callback=%s", topic, callback)

    def wrap_message(self, callback: Callback) -> Callback:
        @functools.wraps(callback)
        async def decorator(data: Any) -> None:
            self.log.debug("received event: %s", data)
            message = self._wrap_message(data)
            self.context.set(**message.headers.to_dict())
            await self.pre_callback_hook()
            await callback(message)
            await self.post_callback_hook()

        return decorator

    def acknowledge(self, callback: Callback) -> Callback:
        @functools.wraps(callback)
        async def decorator(message: Any) -> None:
            try:
                await callback(message)
                await self._ack_on_success(message)
                self.log.debug("successfully processed event")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.log.exception(exc)
                await self._nak_on_failure(message)
                self.log.debug("an error occurred while processing event")

        return decorator
