import pytest

from vbcore import misc
from vbcore.misc import CommonRegex, split_kwargs
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", 1.0),
        ("1.1", 1.1),
        ("1,1", None),
        ("aaa", None),
    ],
)
def test_to_float(value, expected):
    Asserter.assert_equals(misc.to_float(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", 1),
        ("1.1", None),
        ("1,1", None),
        ("aaa", None),
    ],
)
def test_to_int(value, expected):
    Asserter.assert_equals(misc.to_int(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", 1),
        ("1.1", 1.1),
        ("true", True),
        ("test", "test"),
    ],
    ids=[
        "int",
        "float",
        "bool",
        "string",
    ],
)
def test_parse_value(value, expected):
    Asserter.assert_equals(misc.parse_value(value), expected)


@pytest.mark.parametrize(
    "email, expected",
    [
        ("pippo@example.fake", True),
        ("p.pippo@example.fake", True),
        ("p-pippo@example.fake", True),
        ("123pippo@example.fake", True),
        ("pippo.example.com", False),
        ("pippo@example", False),
        ("pippo@example.é", False),
        ("p$pippo@example.fake", False),
    ],
)
def test_common_regex_valid_email(email, expected):
    assert_that = Asserter.assert_true if expected else Asserter.assert_false
    assert_that(CommonRegex.is_valid_email(email))


def test_split_kwargs():
    wanted, unwanted = split_kwargs(("a", "b"), a=1, b=2, c=3)
    Asserter.assert_equals(wanted, {"a": 1, "b": 2})
    Asserter.assert_equals(unwanted, {"c": 3})


@pytest.mark.skip("implement me")
def test_static_attr_decorator():
    pass


@pytest.mark.skip("implement me")
def test_memory_usage_dump():
    pass


@pytest.mark.skip("implement me")
def test_signal_register():
    pass


@pytest.mark.skip("implement me")
def test_signal_handle_terminate():
    pass
