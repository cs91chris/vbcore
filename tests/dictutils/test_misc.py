from vbcore.dictutils.misc import map_keys
from vbcore.tester.asserter import Asserter


def test_map_keys_explicit():
    data = {"a": 1, "b": 2}
    mapped = map_keys(data, a="z", b="v")
    Asserter.assert_equals(mapped, {"z": 1, "v": 2})


def test_map_keys_with_mapper():
    data = {"a": 1, "b": 2}
    mapped = map_keys(data, mapper=lambda x: x.upper())
    Asserter.assert_equals(mapped, {"A": 1, "B": 2})


def test_map_keys_hybrid():
    data = {"a": 1, "b": 2}
    mapped = map_keys(data, mapper=lambda x: x.upper(), a="Z", c="U")
    Asserter.assert_equals(mapped, {"Z": 1, "B": 2})
