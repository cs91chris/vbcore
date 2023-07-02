import pytest

from vbcore.datastruct.dictionaries import BDict, IDict, ObjectDict
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "lowercase, trim, expected",
    [
        (True, True, {"a": 11, "b": 12}),
        (True, False, {"a_a": 11, "a_b": 12}),
        (False, True, {"A": 11, "B": 12}),
        (False, False, {"A_A": 11, "A_B": 12}),
    ],
    ids=[
        "lower_trim",
        "lower_no-trim",
        "no-lower_trim",
        "no-lower_no-trim",
    ],
)
def test_idict_get_namespace(lowercase, trim, expected):
    data = IDict(A_A=11, A_B=12, B_A=21, B_B=22)
    namespace = data.get_namespace("A", lowercase=lowercase, trim=trim)
    Asserter.assert_equals(namespace, expected)


def test_idict_patch():
    data = IDict(a=1)
    Asserter.assert_equals(data.patch(b=2), IDict(a=1, b=2))
    Asserter.assert_equals(data.patch({"c": 3}), IDict(a=1, b=2, c=3))


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
    _hello = res.hello  # pylint: disable=no-member
    _list_b = res.lista[0].b  # pylint: disable=no-member
    Asserter.assert_equals(_hello, data["hello"])
    Asserter.assert_equals(_list_b, data["lista"][0]["b"])


def test_object_dict_normalize_list():
    data = [
        {"a": "a"},
        {"b": "b"},
    ]
    res = ObjectDict.normalize(data)
    Asserter.assert_equals(res[0].a, data[0]["a"])
    Asserter.assert_equals(res[1].b, data[1]["b"])


def test_bdict():
    data = BDict(a="z", b="v")

    Asserter.assert_equals(dict(data), {"a": "z", "b": "v"})
    Asserter.assert_equals(dict(data.T), {"z": "a", "v": "b"})

    Asserter.assert_equals("a", data.T[data["a"]])
    Asserter.assert_equals("b", data.T[data["b"]])
    Asserter.assert_equals("z", data[data.T["z"]])
    Asserter.assert_equals("v", data[data.T["v"]])
