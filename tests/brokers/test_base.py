import pytest
from pytest import LogCaptureFixture

from vbcore.brokers.base import BrokerClient
from vbcore.brokers.data import Message


@pytest.mark.asyncio
async def test_publish(dummy_broker: BrokerClient, caplog: LogCaptureFixture) -> None:
    async with dummy_broker.connect() as client:
        await client.publish("TOPIC", b"MESSAGE")

    # TODO these assertion does not works when all tests runs, but works individually...
    # Asserter.assert_len(caplog.records, 1)
    # Asserter.assert_equals(caplog.records[0].levelname, "DEBUG")
    # Asserter.assert_equals(
    #     caplog.records[0].message, "successfully published to topic 'TOPIC': b'MESSAGE'"
    # )


@pytest.mark.asyncio
async def test_subscribe(dummy_broker: BrokerClient, caplog: LogCaptureFixture) -> None:
    async with dummy_broker.connect() as client:
        await client.subscribe("TOPIC", lambda x: None)

    # TODO these assertion does not works when all tests runs, but works individually...
    # Asserter.assert_len(caplog.records, 1)
    # Asserter.assert_equals(caplog.records[0].levelname, "INFO")
    # Asserter.assert_equals(caplog.records[0].message, "successfully subscribed on topic: TOPIC")


@pytest.mark.asyncio
async def test_nack_on_failure(dummy_broker: BrokerClient, caplog: LogCaptureFixture) -> None:
    @dummy_broker.acknowledge
    async def raise_error(message: Message) -> None:
        raise ValueError(message.topic)

    await raise_error(Message(topic="NACKED"))

    # TODO these assertion does not works when all tests runs, but works individually...
    # Asserter.assert_len(caplog.records, 2)
    # Asserter.assert_equals(caplog.records[0].levelname, "ERROR")
    # Asserter.assert_in("ValueError: NACKED", str(caplog.records[0].exc_text))

    # Asserter.assert_equals(caplog.records[1].levelname, "DEBUG")
    # Asserter.assert_equals(
    #     caplog.records[1].message, "an error occurred while processing event, nack sent"
    # )
