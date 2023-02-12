import enum

from vbcore.enums import IStrEnum, StrEnum
from vbcore.tester.mixins import Asserter


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
