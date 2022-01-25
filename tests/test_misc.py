import string

from vbcore import uuid, misc
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


def test_random_string():
    test_str = misc.random_string(4, alphabet=string.ascii_lowercase)
    Asserter.assert_equals(len(test_str), 4)
    Asserter.assert_true(all(c.islower() for c in test_str))
