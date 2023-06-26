import enum

import pytest

from vbcore.enums import IStrEnum, StrEnum
from vbcore.tester.asserter import Asserter


@pytest.mark.skip("implement me")
def test_int_enum():
    """TODO implement me"""


def test_str_enum():
    class Sample(StrEnum):
        EXAMPLE = enum.auto()

    Asserter.assert_equals(Sample.EXAMPLE, "EXAMPLE")
    Asserter.assert_equals(Sample.EXAMPLE.lower(), "example")


def test_str_enum_lower():
    class Sample(IStrEnum):
        EXAMPLE = enum.auto()

    Asserter.assert_equals(Sample.EXAMPLE, "example")
    Asserter.assert_equals(Sample.EXAMPLE.upper(), "EXAMPLE")


@pytest.mark.skip("implement me")
def test_lstr_enum():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_istr_enum():
    """TODO implement me"""
