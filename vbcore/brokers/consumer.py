import abc
from collections.abc import Sequence
from typing import Generic, List, Optional, Type, TypeVar

from vbcore.heartbeat import Heartbeat
from vbcore.loggers import VBLoggerMixin

from .base import BrokerClient
from .data import Message
from .publisher import EventModel

E = TypeVar("E", bound=EventModel)


class BaseCallback(abc.ABC, Generic[E]):
    def __init__(self, schema: Type[E]):
        self.schema = schema

    def prepare_data(self, data: bytes) -> E:
        return self.schema.model_validate_json(data)

    @abc.abstractmethod
    async def perform(self, message: Message) -> None:
        raise NotImplementedError


class Dispatcher(VBLoggerMixin):
    def __init__(self, callbacks: Sequence[BaseCallback]) -> None:
        self.callbacks: dict[str, BaseCallback] = {}
        self.register(*callbacks)

    @property
    def topics(self) -> List[str]:
        return list(self.callbacks)

    def register(self, *callbacks: BaseCallback) -> None:
        for callback in callbacks:
            self.callbacks[callback.schema.TOPIC] = callback
            self.log.info(
                "registered: topic=%s callback=<%s>",
                self.class_dumper(callback),
                callback.schema.TOPIC,
            )

    async def dispatch(self, message: Message) -> None:
        callback = self.callbacks[message.topic]
        self.log.debug("dispatch message: callback=<%s>", self.class_dumper(callback))
        await callback.perform(message)


class Consumer(VBLoggerMixin):
    def __init__(
        self,
        broker: BrokerClient,
        callbacks: Sequence[BaseCallback],
        heartbeat: Optional[Heartbeat] = None,
    ):
        self.broker = broker
        self.dispatcher = Dispatcher(callbacks)
        self.heartbeat = heartbeat or Heartbeat()

    async def run(self):
        self.log.info(
            "start: consumer=<%s> broker=<%s>",
            self.class_dumper(self),
            self.class_dumper(self.broker),
        )
        self.heartbeat.start()

        async with self.broker.connect() as client:
            for topic in self.dispatcher.topics:
                await client.subscribe(topic, self.dispatcher.dispatch)
            await self.heartbeat.run_forever()

        self.log.info("shutdown: consumer=<%s>", self.class_dumper(self))
