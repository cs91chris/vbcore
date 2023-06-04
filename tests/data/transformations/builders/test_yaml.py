import pytest

from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "data, expected",
    [
        ("a: 1\nb: 2", {"a": 1, "b": 2}),
        ("- a: 1\n  b: 2", [{"a": 1, "b": 2}]),
    ],
    ids=[
        "dict",
        "list-dict",
    ],
)
def test_build_to_dict(yaml_builder, data, expected):
    Asserter.assert_equals(yaml_builder.build(data), expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        ({"a": 1, "b": 2}, "a: 1\nb: 2\n"),
        ([{"a": 1, "b": 2}], "- a: 1\n  b: 2\n"),
    ],
    ids=[
        "dict",
        "list-dict",
    ],
)
def test_to_self(yaml_builder, data, expected):
    Asserter.assert_equals(yaml_builder.to_self(data), expected)
