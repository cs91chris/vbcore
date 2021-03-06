import enum
from time import sleep
from unittest.mock import Mock, patch

from vbcore.datastruct import ExpiringCache, IStrEnum, ObjectDict, StrEnum
from vbcore.tester.mixins import Asserter


def test_object_dict_constructor():
    data = {
        "hello": "world",
        "lista": [{"a": {"b": "ab"}}],
    }
    res = ObjectDict(**data)
    Asserter.assert_equals(res.hello, "world")
    Asserter.assert_equals(res.lista[0].a.b, "ab")


def test_object_dict_normalize_dict():
    data = {
        "hello": "world",
        "lista": [{"b": "b"}],
    }
    res = ObjectDict.normalize(data)
    Asserter.assert_equals(res.hello, data["hello"])
    Asserter.assert_equals(res.lista[0].b, data["lista"][0]["b"])


def test_object_dict_normalize_list():
    data = [
        {"a": "a"},
        {"b": "b"},
    ]
    res = ObjectDict.normalize(data)
    Asserter.assert_equals(res[0].a, data[0]["a"])
    Asserter.assert_equals(res[1].b, data[1]["b"])


def test_str_enum():
    class Sample(StrEnum):
        EXAMPLE = enum.auto()

    Asserter.assert_equals(Sample.EXAMPLE, "EXAMPLE")
    Asserter.assert_equals(Sample.EXAMPLE.lower(), "example")


def test_str_enum_lower():
    class Sample(IStrEnum):
        EXAMPLE = enum.auto()

    Asserter.assert_equals(Sample.EXAMPLE, "example")
    Asserter.assert_equals(Sample.EXAMPLE.upper(), "EXAMPLE")


def test_expiring_dict_getter_setter():
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


def test_expiring_dict_pop():
    cache = ExpiringCache(max_len=3, max_age=0.01)
    cache["a"] = "x"
    Asserter.assert_equals("x", cache.pop("a"))
    sleep(0.01)
    Asserter.assert_none(cache.pop("a"))


def test_expiring_dict_iter():
    cache = ExpiringCache(max_len=10, max_age=0.01)
    Asserter.assert_is_empty_list(list(cache))
    cache["a"] = "x"
    cache["b"] = "y"
    cache["c"] = "z"
    Asserter.assert_equals(list(cache), ["a", "b", "c"])

    Asserter.assert_equals(cache.values(), ["x", "y", "z"])
    sleep(0.01)
    Asserter.assert_is_empty_list(cache.values())


def test_expiring_dict_clear():
    cache = ExpiringCache(max_len=10, max_age=10)
    cache["a"] = "x"
    Asserter.assert_len(cache, 1)
    cache.clear()
    Asserter.assert_len(cache, 0)


def test_expiring_dict_ttl():
    cache = ExpiringCache(max_len=10, max_age=10)
    cache["a"] = "x"

    Asserter.assert_range(cache.ttl("a"), (0, 10))
    Asserter.assert_none(cache.ttl("b"))

    with patch.object(ExpiringCache, "__getitem__", Mock(return_value=("x", 10**9))):
        Asserter.assert_none(cache.ttl("a"))
