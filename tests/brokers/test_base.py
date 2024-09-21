import pytest
from pytest import LogCaptureFixture

from vbcore.brokers.base import BrokerClient
from vbcore.brokers.data import Message
from vbcore.tester.asserter import Asserter


@pytest.mark.asyncio
async def test_publish(dummy_broker: BrokerClient, caplog: LogCaptureFixture) -> None:
    with caplog.at_level("DEBUG"):
        async with dummy_broker.connect() as client:
            await client.publish("TOPIC", b"MESSAGE")

    Asserter.assert_len(caplog.records, 1)
    Asserter.assert_equals(caplog.records[0].levelname, "DEBUG")
    Asserter.assert_true(
        caplog.records[0].message.startswith("successfully published: topic=TOPIC header=")
    )
    Asserter.assert_true(caplog.records[0].message.endswith("message=b'MESSAGE'"))


@pytest.mark.asyncio
async def test_subscribe(dummy_broker: BrokerClient, caplog: LogCaptureFixture) -> None:
    with caplog.at_level("INFO"):
        async with dummy_broker.connect() as client:
            await client.subscribe("TOPIC", lambda x: None)

    Asserter.assert_len(caplog.records, 1)
    Asserter.assert_equals(caplog.records[0].levelname, "INFO")
    Asserter.assert_true(
        caplog.records[0].message.startswith(
            "successfully subscribed: consumer_group=None, topic=TOPIC callback="
        )
    )


@pytest.mark.asyncio
async def test_nack_on_failure(dummy_broker: BrokerClient, caplog: LogCaptureFixture) -> None:
    @dummy_broker.acknowledge
    async def raise_error(message: Message) -> None:
        raise ValueError(message.topic)

    with caplog.at_level("DEBUG"):
        await raise_error(Message(topic="NACKED"))

    Asserter.assert_len(caplog.records, 2)
    Asserter.assert_equals(caplog.records[0].levelname, "ERROR")
    Asserter.assert_in("ValueError: NACKED", str(caplog.records[0].exc_text))

    Asserter.assert_equals(caplog.records[1].levelname, "DEBUG")
    Asserter.assert_equals(caplog.records[1].message, "an error occurred while processing event")
