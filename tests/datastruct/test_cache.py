from time import sleep
from unittest.mock import Mock, patch

import pytest

from vbcore.datastruct.cache import ExpiringCache
from vbcore.tester.asserter import Asserter


@pytest.mark.skip("implement me")
def test_lru_cache():
    pass


@pytest.mark.skip("implement me")
def test_timed_lru_cache_decorator():
    pass


def test_expiring_cache_getter_setter():
    cache = ExpiringCache(max_len=3, max_age=0.01)

    Asserter.assert_none(cache.get("a"))
    cache["a"] = "x"
    Asserter.assert_equals(cache.get("a"), "x")

    sleep(0.01)
    Asserter.assert_none(cache.get("a"))

    cache["a"] = "y"
    Asserter.assert_equals(cache.get("a"), "y")

    Asserter.assert_not_in("b", cache)
    cache["b"] = "y"
    Asserter.assert_in("b", cache)

    sleep(0.01)
    Asserter.assert_not_in("b", cache)

    cache.set("c", "x")
    cache.set("d", "y")
    cache.set("e", "z")

    Asserter.assert_in("c", cache)
    Asserter.assert_in("d", cache)

    cache["f"] = "1"
    Asserter.assert_not_in("c", cache)

    del cache["e"]
    Asserter.assert_not_in("e", cache)


def test_expiring_cache_pop():
    cache = ExpiringCache(max_len=3, max_age=0.01)
    cache["a"] = "x"
    Asserter.assert_equals("x", cache.pop("a"))
    sleep(0.01)
    Asserter.assert_none(cache.pop("a"))


def test_expiring_cache_iter():
    cache = ExpiringCache(max_len=10, max_age=0.01)
    Asserter.assert_is_empty_list(list(cache))
    cache["a"] = "x"
    cache["b"] = "y"
    cache["c"] = "z"
    Asserter.assert_equals(list(cache), ["a", "b", "c"])

    Asserter.assert_equals(cache.values(), ["x", "y", "z"])
    sleep(0.01)
    Asserter.assert_is_empty_list(cache.values())


def test_expiring_cache_clear():
    cache = ExpiringCache(max_len=10, max_age=10)
    cache["a"] = "x"
    Asserter.assert_len(cache, 1)
    cache.clear()
    Asserter.assert_len(cache, 0)


def test_expiring_cache_ttl():
    cache = ExpiringCache(max_len=10, max_age=10)
    cache["a"] = "x"

    Asserter.assert_range(cache.ttl("a"), (0, 10))
    Asserter.assert_none(cache.ttl("b"))

    with patch.object(ExpiringCache, "__getitem__", Mock(return_value=("x", 10**9))):
        Asserter.assert_none(cache.ttl("a"))
