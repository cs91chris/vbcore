import inspect
from typing import Any
from unittest.mock import ANY

import pytest

from vbcore.brokers.nats import NatsBrokerAdapter
from vbcore.tester.asserter import Asserter


@pytest.mark.asyncio
async def test_nats_publish(nats_broker: NatsBrokerAdapter) -> None:
    topic = "TOPIC"
    message = b"MESSAGE"

    async with nats_broker.connect() as client:
        await client.publish(topic, message)

        mock_publish: Any = client.stream.publish
        mock_publish.assert_called_once_with(
            subject=topic,
            payload=message,
            timeout=client.options.timeout,
            headers=ANY,
        )


@pytest.mark.asyncio
async def test_nats_subscribe(nats_broker: NatsBrokerAdapter) -> None:
    topic = "TOPIC"

    async def dummy_callback(_):
        pass

    async with nats_broker.connect() as client:
        await client.subscribe(topic, dummy_callback)

        mock_subscribe: Any = client.stream.subscribe
        callback = mock_subscribe.call_args_list[0].kwargs["cb"]
        Asserter.assert_equals(
            inspect.signature(callback),
            inspect.signature(dummy_callback),
        )

        mock_subscribe.assert_called_once_with(
            subject=topic, queue="CONSUMER_TOPIC", manual_ack=True, cb=ANY
        )
