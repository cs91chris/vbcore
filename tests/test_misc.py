import string

import pytest

from vbcore import misc
from vbcore.misc import CommonRegex, split_kwargs
from vbcore.tester.mixins import Asserter


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


def test_random_string():
    test_str = misc.random_string(4, alphabet=string.ascii_lowercase)
    Asserter.assert_equals(len(test_str), 4)
    Asserter.assert_true(all(c.islower() for c in test_str))


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
