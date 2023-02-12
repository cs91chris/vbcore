import string

import pytest

from vbcore import misc, uuid
from vbcore.misc import CommonRegex, split_kwargs
from vbcore.tester.mixins import Asserter


def test_all_uuid_versions():
    Asserter.assert_false(uuid.check_uuid("fake uuid"))
    Asserter.assert_true(uuid.check_uuid(uuid.get_uuid(hexify=False)))
    Asserter.assert_true(uuid.check_uuid(uuid.get_uuid()))
    Asserter.assert_true(uuid.check_uuid(uuid.get_uuid(1), ver=1))
    Asserter.assert_true(uuid.check_uuid(uuid.get_uuid(3, name="test"), ver=3))
    Asserter.assert_true(uuid.check_uuid(uuid.get_uuid(5, name="test"), ver=5))


def test_misc():
    Asserter.assert_less(1, 2)
    Asserter.assert_greater(2, 1)
    Asserter.assert_range(2, (1, 3))
    Asserter.assert_occurrence("abacca", r"a", 3)
    Asserter.assert_occurrence("abacca", r"a", 4, less=True)
    Asserter.assert_occurrence("abacca", r"a", 2, greater=True)
    Asserter.assert_true(misc.to_float("1.1"))
    Asserter.assert_none(misc.to_float("1,1"))
    Asserter.assert_true(misc.to_int("1"))
    Asserter.assert_none(misc.to_int("1,1"))
    Asserter.assert_true(misc.parse_value("true"))
    Asserter.assert_equals("test", misc.parse_value("test"))


def test_assert_range():
    Asserter.assert_range(3, [1, 5])
    Asserter.assert_range(1, [1, 5], closed=True)
    Asserter.assert_range(5, [1, 5], closed=True)
    Asserter.assert_range(1, [1, 5], left=True)
    Asserter.assert_range(5, [1, 5], right=True)

    with pytest.raises(AssertionError):
        Asserter.assert_range(6, [1, 5])
    with pytest.raises(AssertionError):
        Asserter.assert_range(5, [1, 5])
    with pytest.raises(AssertionError):
        Asserter.assert_range(1, [1, 5])
    with pytest.raises(AssertionError):
        Asserter.assert_range(5, [1, 5], left=True)
    with pytest.raises(AssertionError):
        Asserter.assert_range(1, [1, 5], right=True)


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
