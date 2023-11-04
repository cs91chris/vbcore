from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vbcore.brokers.base import BrokerClientAdapter
from vbcore.brokers.factory import BrokerEnum, BrokerFactory
from vbcore.brokers.nats import NatsBrokerAdapter, NatsOptions


@pytest.fixture
def dummy_broker() -> BrokerClientAdapter:
    return BrokerFactory.instance(BrokerEnum.DUMMY, servers="localhost")


@pytest.fixture
def nats_broker() -> Generator[NatsBrokerAdapter, None, None]:
    nats_client = AsyncMock()
    nats_client.jetstream = MagicMock()
    nats_client.jetstream.return_value = AsyncMock()
    nats_instance = MagicMock(return_value=nats_client)

    with patch("vbcore.brokers.nats.NATS", new=nats_instance):
        yield NatsBrokerAdapter(NatsOptions(servers="localhost", consumer_group="CONSUMER"))


@pytest.fixture(scope="session")
def correlation_id() -> str:
    return "12346789"


@pytest.fixture(scope="session")
def timestamp() -> float:
    return 12345.6789
