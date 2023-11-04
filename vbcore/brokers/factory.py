from enum import Enum

from vbcore.factory import ItemEnumMeta, ItemEnumMixin, ItemFactory

from .base import BrokerClientAdapter
from .data import BrokerOptions
from .dummy import DummyBrokerAdapter
from .nats import NatsBrokerAdapter, NatsOptions


class BrokerEnum(ItemEnumMixin[BrokerOptions], Enum, metaclass=ItemEnumMeta):
    NATS = NatsBrokerAdapter, NatsOptions
    DUMMY = DummyBrokerAdapter, BrokerOptions


class BrokerFactory(ItemFactory[BrokerEnum, BrokerClientAdapter]):
    items = BrokerEnum
