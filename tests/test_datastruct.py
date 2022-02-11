import enum

from vbcore.datastruct import ObjectDict, StrEnum, IStrEnum
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
