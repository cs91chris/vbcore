from abc import ABC
from typing import Callable, ClassVar, List, Optional, Type

import backoff
from pydantic import BaseModel

from vbcore.loggers import VBLoggerMixin

from .base import BrokerClientAdapter
from .data import Header


class EventModel(ABC, BaseModel):
    TOPIC: ClassVar[str]


class Publisher(VBLoggerMixin):
    def __init__(
        self,
        broker: BrokerClientAdapter,
        backoff_enabled: bool = True,
        retryable_errors: Optional[List[Type[Exception]]] = None,
        max_tries: int = 3,
    ):
        self.broker = broker
        self.backoff_enabled = backoff_enabled
        self.retryable_errors = retryable_errors or [Exception]
        self.max_tries = max_tries

    def backoff_wrapper(self, func: Callable) -> Callable:
        decorator = backoff.on_exception(
            backoff.expo,
            logger=self.log,
            exception=self.retryable_errors,
            max_tries=self.max_tries,
        )
        return decorator(func)

    async def publish(
        self, message: EventModel, headers: Optional[Header] = None, **kwargs
    ) -> None:
        async def _publish() -> None:
            async with self.broker.connect() as client:
                data = message.model_dump_json().encode()
                await client.publish(
                    topic=message.TOPIC, message=data, headers=headers or Header(), **kwargs
                )

        wrapper = self.backoff_wrapper(_publish) if self.backoff_enabled else _publish
        await wrapper()  # type: ignore
