from enum import Enum

from vbcore.datastruct.lazy import LazyImporter
from vbcore.factory import ItemEnumMeta, ItemEnumMixin, ItemFactory

from .base import BrokerClient
from .data import BrokerOptions
from .dummy import DummyBrokerAdapter

NatsBrokerAdapter, NatsOptions = LazyImporter.import_many(
    "vbcore.brokers.nats:NatsBrokerAdapter",
    "vbcore.brokers.nats:NatsOptions",
    message="you must install 'nats-py'",
)


class BrokerEnum(ItemEnumMixin[BrokerOptions], Enum, metaclass=ItemEnumMeta):
    NATS = NatsBrokerAdapter, NatsOptions
    DUMMY = DummyBrokerAdapter, BrokerOptions


class BrokerFactory(ItemFactory[BrokerEnum, BrokerClient]):
    items = BrokerEnum
