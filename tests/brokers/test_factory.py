import pytest

from vbcore.brokers.base import BrokerClientAdapter
from vbcore.brokers.data import BrokerOptions
from vbcore.brokers.dummy import DummyBrokerAdapter
from vbcore.brokers.factory import BrokerFactory
from vbcore.brokers.nats import NatsBrokerAdapter, NatsOptions
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "broker_name, broker_class, options_class",
    [
        ("DUMMY", DummyBrokerAdapter, BrokerOptions),
        ("NATS", NatsBrokerAdapter, NatsOptions),
    ],
    ids=[
        "dummy",
        "nats",
    ],
)
def test_broker_factory(
    broker_name: str,
    broker_class: DummyBrokerAdapter,
    options_class: BrokerOptions,
) -> None:
    broker = BrokerFactory.instance(broker_name, servers="localhost")
    Asserter.assert_isinstance(broker, BrokerClientAdapter)
    Asserter.assert_is(type(broker), broker_class)
    Asserter.assert_is(type(broker.options), options_class)
