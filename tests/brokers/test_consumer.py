from unittest.mock import AsyncMock, MagicMock

import pytest

from vbcore.brokers.consumer import BaseCallback, Consumer, Dispatcher
from vbcore.brokers.data import Message
from vbcore.brokers.publisher import EventModel
from vbcore.tester.helpers import MockHelper


class SampleEvent(EventModel):
    TOPIC = "foo"
    message: str


class SampleCallback(BaseCallback[SampleEvent]):
    def __init__(self):
        super().__init__(SampleEvent)
        self.handler = MagicMock()

    async def perform(self, message) -> None:
        self.handler(message)


@pytest.mark.asyncio
async def test_dispatcher_dispatch() -> None:
    callback = SampleCallback()
    message = Message(topic=SampleEvent.TOPIC)
    dispatcher = Dispatcher([callback])
    await dispatcher.dispatch(message)
    callback.handler.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_consumer_run() -> None:
    mock_heartbeat = AsyncMock()
    mock_client = AsyncMock()
    mock_broker = AsyncMock()
    mock_broker.connect = MockHelper.mock_async_with(mock_client)

    consumer = Consumer(mock_broker, [SampleCallback()], heartbeat=mock_heartbeat)
    await consumer.run()

    mock_broker.connect.assert_called_once_with()
    mock_client.subscribe.assert_called_once_with("foo", consumer.dispatcher.dispatch)
    mock_heartbeat.start.assert_called_once_with()
    mock_heartbeat.run_forever.assert_called_once_with()
