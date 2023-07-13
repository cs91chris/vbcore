from time import sleep
from unittest.mock import MagicMock, Mock, patch

from vbcore.datastruct.cache import ExpiringCache, LRUCache, TimedLRUCache
from vbcore.tester.asserter import Asserter


def test_lru_cache():
    cache = LRUCache(maxsize=3)

    cache.set(1, 1)
    cache.set(2, 2)
    cache.set(3, 3)

    cache.get(1)
    cache.set(4, 4)

    Asserter.assert_equals(dict(cache), {3: 3, 1: 1, 4: 4})


def test_timed_lru_cache_decorator():
    mock = MagicMock()
    cache = TimedLRUCache(milliseconds=10)

    @cache
    def sample(data: int):
        return mock(data)

    sample(1)
    mock.assert_called_once_with(1)
    mock.reset_mock()
    sample(1)
    mock.assert_not_called()
    sleep(0.02)
    sample(1)
    mock.assert_called_once_with(1)


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
