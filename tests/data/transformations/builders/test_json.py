import pytest

from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "data, expected",
    [
        ('{"a": 1, "b": 2}', {"a": 1, "b": 2}),
        ('[{"a": 1, "b": 2}]', [{"a": 1, "b": 2}]),
    ],
    ids=[
        "dict",
        "list-dict",
    ],
)
def test_build_to_dict(json_builder, data, expected):
    Asserter.assert_equals(json_builder.build(data), expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        ({"a": 1, "b": 2}, '{"a": 1, "b": 2}'),
        ([{"a": 1, "b": 2}], '[{"a": 1, "b": 2}]'),
    ],
    ids=[
        "dict",
        "list-dict",
    ],
)
def test_to_self(json_builder, data, expected):
    Asserter.assert_equals(json_builder.to_self(data), expected)
