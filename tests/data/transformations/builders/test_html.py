import pytest

from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            "<table><thead><tr><th>a</th><th>b</th></tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table>",
            [{"a": 1, "b": 2}],
        ),
    ],
    ids=[
        "list-dict",
    ],
)
def test_build_to_dict(html_builder, data, expected):
    Asserter.assert_equals(html_builder.build(data), expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            [{"a": 1, "b": 2}],
            "<table><thead><tr><th>a</th><th>b</th></tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table>",
        ),
    ],
    ids=[
        "list-dict",
    ],
)
def test_to_self(html_builder, data, expected):
    Asserter.assert_equals(html_builder.to_self(data), expected)
