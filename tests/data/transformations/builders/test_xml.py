import pytest

from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            '<ROOT><a type="int">1</a><b type="int">2</b></ROOT>',
            {"a": 1, "b": 2},
        ),
        (
            '<ROOT><ROW type="dict"><a type="int">1</a><b type="int">2</b></ROW></ROOT>',
            [{"a": 1, "b": 2}],
        ),
    ],
    ids=[
        "dict",
        "list-dict",
    ],
)
def test_build_to_dict(xml_builder, data, expected):
    Asserter.assert_equals(xml_builder.build(data), expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {"a": 1, "b": 2},
            '<ROOT><a type="int">1</a><b type="int">2</b></ROOT>',
        ),
        (
            [{"a": 1, "b": 2}],
            '<ROOT><ROW type="dict"><a type="int">1</a><b type="int">2</b></ROW></ROOT>',
        ),
    ],
    ids=[
        "dict",
        "list-dict",
    ],
)
def test_to_self(xml_builder, data, expected):
    preamble = '<?xml version="1.0" encoding="utf-8" ?>'
    Asserter.assert_equals(xml_builder.to_self(data), f"{preamble}{expected}")
