import pytest

from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "data, expected",
    [
        ("a|b\n1|2", [{"a": "1", "b": "2"}]),
    ],
    ids=[
        "list-dict",
    ],
)
def test_build_to_dict(csv_builder, data, expected):
    Asserter.assert_equals(csv_builder.build(data), expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        ([{"a": "1", "b": "2"}], "a|b\n1|2\n"),
    ],
    ids=[
        "list-dict",
    ],
)
def test_to_self(csv_builder, data, expected):
    Asserter.assert_equals(csv_builder.to_self(data), expected)
