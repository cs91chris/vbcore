from unittest.mock import ANY, AsyncMock, patch

import pytest

from vbcore.brokers.data import Header
from vbcore.brokers.publisher import EventModel, Publisher
from vbcore.tester.helpers import MockHelper


class SampleEvent(EventModel):
    TOPIC = "foo"
    message: str


@patch("vbcore.brokers.publisher.backoff")
def test_backoff_wrapper(mock_backoff) -> None:
    publisher = Publisher(AsyncMock(), retryable_errors=[ValueError])
    publisher.backoff_wrapper(lambda _: _)
    mock_backoff.on_exception.assert_called_once_with(
        mock_backoff.expo,
        logger=publisher.log,
        exception=[ValueError],
        max_tries=3,
    )


@pytest.mark.asyncio
async def test_publish() -> None:
    mock_client = AsyncMock()
    mock_broker = AsyncMock()
    mock_broker.connect = MockHelper.mock_async_with(mock_client)

    publisher = Publisher(mock_broker, backoff_enabled=False)
    await publisher.publish(SampleEvent(message="hello"))

    mock_broker.connect.assert_called_once()
    mock_client.publish.assert_called_once_with(
        topic="foo",
        message=b'{"message":"hello"}',
        headers=Header(correlation_id=ANY, timestamp=ANY),
    )


@pytest.mark.parametrize(
    "message",
    [
        b'{"message": "hello"}',
        '{"message": "hello"}',
        {"message": "hello"},
    ],
    ids=[
        "bytes",
        "string",
        "dict",
    ],
)
@pytest.mark.asyncio
async def test_raw_publish(message) -> None:
    mock_client = AsyncMock()
    mock_broker = AsyncMock()
    mock_broker.connect = MockHelper.mock_async_with(mock_client)

    publisher = Publisher(mock_broker)
    await publisher.raw_publish("foo", message)

    mock_broker.connect.assert_called_once()
    mock_client.publish.assert_called_once_with("foo", b'{"message": "hello"}', None)
