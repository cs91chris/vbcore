import abc
from typing import Generic, Optional, Sequence, Type, TypeVar

from vbcore.heartbeat import Heartbeat
from vbcore.loggers import Log, VBLoggerMixin

from .base import BrokerClient
from .data import Message
from .publisher import EventModel

E = TypeVar("E", bound=EventModel)


class BaseCallback(VBLoggerMixin, abc.ABC, Generic[E]):
    def __init__(self, schema: Type[E]):
        self.schema = schema

    def __str__(self) -> str:
        return self.class_dumper(self).dump()

    @property
    def topic(self) -> str:
        return self.schema.TOPIC

    def prepare_data(self, data: bytes) -> E:
        return self.schema.model_validate_json(data)

    @abc.abstractmethod
    async def perform(self, message: Message) -> None:
        raise NotImplementedError

    async def __call__(self, message: Message) -> None:
        self.log.info("[%s] start execution", self)
        with Log.execution_time(logger=__name__, message=f"[{self}] execution time"):
            await self.perform(message)


class DummyCallback(BaseCallback):
    class SampleEvent(EventModel):
        TOPIC = "TOPIC.SAMPLE"

    def __init__(self, schema: type[EventModel] | None = None):
        super().__init__(schema or DummyCallback.SampleEvent)

    async def perform(self, message: Message) -> None:
        self.log.info("received message: %s", message)


class Consumer(VBLoggerMixin):
    def __init__(
        self,
        broker: BrokerClient,
        callbacks: Sequence[BaseCallback],
        heartbeat: Optional[Heartbeat] = None,
    ):
        self.broker = broker
        self.heartbeat = heartbeat or Heartbeat()
        self._callbacks = list(sorted(callbacks, key=lambda c: c.topic))

    async def run(self) -> None:
        self.log.info(
            "start: consumer=<%s>, broker=<%s>",
            self.class_dumper(self),
            self.class_dumper(self.broker),
        )
        self.heartbeat.start()

        async with self.broker.connect() as client:
            for callback in self._callbacks:
                await client.subscribe(callback.topic, callback)
            await self.heartbeat.run_forever()

        self.log.info("shutdown: consumer=<%s>", self.class_dumper(self))
