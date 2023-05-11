import pytest

from vbcore.datastruct.orderer_set import OrderedSet
from vbcore.tester.asserter import Asserter


def test_ordered_set_add():
    data = OrderedSet(())
    Asserter.assert_len(data, 0)

    data.add(0)
    Asserter.assert_len(data, 1)
    Asserter.assert_equals(list(data), [0])
    data.add(1)
    Asserter.assert_len(data, 2)
    Asserter.assert_equals(list(data), [0, 1])


def test_ordered_set_clear():
    data = OrderedSet([1, 2, 3])
    Asserter.assert_len(data, 3)
    data.clear()
    Asserter.assert_len(data, 0)


def test_ordered_set_discard():
    data = OrderedSet([1, 2, 3])
    data.discard(2)
    Asserter.assert_equals(list(data), [1, 3])
    data.discard(2)
    Asserter.assert_equals(list(data), [1, 3])


def test_ordered_set_remove():
    data = OrderedSet([1, 2, 3])
    data.remove(2)
    Asserter.assert_equals(list(data), [1, 3])

    with pytest.raises(KeyError):
        data.remove(2)

    Asserter.assert_equals(list(data), [1, 3])


def test_ordered_set_getitem():
    data = OrderedSet([1, 2, 3])
    Asserter.assert_equals(data[0], 1)
    Asserter.assert_equals(data[1], 2)
    Asserter.assert_equals(data[2], 3)
    with pytest.raises(IndexError):
        _ = data[3]


def test_ordered_set_iter():
    data = OrderedSet([1, 2, 3])
    for index, item in enumerate(data):
        # pylint: disable=unnecessary-list-index-lookup
        Asserter.assert_equals(data[index], item)


def test_ordered_set_str_repr():
    Asserter.assert_equals(str(OrderedSet([1, 2, 3])), "{1, 2, 3}")
    Asserter.assert_equals(repr(OrderedSet([1, 2, 3])), "<OrderedSet {1, 2, 3}>")


def test_ordered_set_equals():
    data = OrderedSet([1, 2, 3])
    other = OrderedSet([1, 2, 3])
    Asserter.assert_equals(data, other)
    assert data is not other
