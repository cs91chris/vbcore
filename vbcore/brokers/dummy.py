from typing import Any, Optional

from .base import BrokerClient, Callback
from .data import BrokerOptions, Header, Message


class DummyClient:
    def __call__(self, *_, **__):
        return self

    def __getattr__(self, *_, **__):
        return self


class DummyBrokerAdapter(BrokerClient[DummyClient, BrokerOptions]):
    def instance(self) -> DummyClient:
        return DummyClient()

    def _wrap_message(self, message: Any) -> Message:
        return Message(topic="", data=message)

    async def _publish(
        self, topic: str, message: Any, headers: Optional[Header] = None, **kwargs
    ) -> None:
        self.client.publish(topic, message, **kwargs)

    async def _subscribe(self, topic: str, callback: Callback, **kwargs) -> None:
        self.client.subscribe(topic, callback, **kwargs)
