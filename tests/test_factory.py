import enum
from dataclasses import dataclass

from vbcore.base import BaseDTO
from vbcore.factory import DummyItem, Item, ItemEnumMeta, ItemEnumMixin, ItemFactory
from vbcore.tester.mixins import Asserter


@dataclass
class Options(BaseDTO):
    integer: int
    string: str


class MyItem(Item[Options]):
    """
    concrete implementation of an item
    """


class MyItemEnum(
    ItemEnumMixin[Options],
    enum.Enum,
    metaclass=ItemEnumMeta,
):
    DUMMY = DummyItem, Options
    ITEM = MyItem, Options


class MyItemFactory(ItemFactory[MyItemEnum, MyItem]):
    products = MyItemEnum


def test_products_list():
    Asserter.assert_equals(MyItemEnum.products(), ["DUMMY", "ITEM"])


def test_instance():
    instance = MyItemFactory.instance("DUMMY", integer=1, string="string")
    Asserter.assert_true(isinstance(instance, Item))
    Asserter.assert_true(isinstance(instance, DummyItem))
    Asserter.assert_equals(instance.options, Options(integer=1, string="string"))

    instance = MyItemFactory.instance("ITEM", integer=1, string="string")
    Asserter.assert_true(isinstance(instance, Item))
    Asserter.assert_true(isinstance(instance, MyItem))
    Asserter.assert_equals(instance.options, Options(integer=1, string="string"))
