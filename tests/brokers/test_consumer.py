from unittest.mock import AsyncMock, call, MagicMock

import pytest

from vbcore.brokers.consumer import BaseCallback, Consumer
from vbcore.brokers.publisher import EventModel
from vbcore.tester.helpers import MockHelper


class SampleEvent(EventModel):
    TOPIC = "foo"
    message: str


class SampleCallback(BaseCallback):
    def __init__(self):
        super().__init__(SampleEvent)
        self.handler = MagicMock()

    async def perform(self, message) -> None:
        self.handler(message)


@pytest.mark.asyncio
async def test_consumer_run() -> None:
    mock_heartbeat = AsyncMock()
    mock_client = AsyncMock()
    mock_broker = AsyncMock()
    mock_broker.connect = MockHelper.mock_async_with(mock_client)

    callback_1 = SampleCallback()
    callback_2 = SampleCallback()

    consumer = Consumer(
        broker=mock_broker,
        heartbeat=mock_heartbeat,
        callbacks=[callback_2, callback_1],
    )
    await consumer.run()

    mock_broker.connect.assert_called_once_with()
    mock_client.subscribe.has_calls(
        [
            call("foo", callback_1.perform),
            call("foo", callback_2.perform),
        ]
    )
    mock_heartbeat.start.assert_called_once_with()
    mock_heartbeat.run_forever.assert_called_once_with()
