import enum

from vbcore.enums import IntEnum, IStrEnum, LStrEnum, StrEnum
from vbcore.tester.asserter import Asserter


class SampleIntEnum(IntEnum):
    A = 1
    B = 2
    C = 3


def test_int_enum():
    Asserter.assert_equals(SampleIntEnum.A, 1)
    Asserter.assert_equals(SampleIntEnum.A, SampleIntEnum(1))


def test_int_enum_repr():
    Asserter.assert_equals(repr(SampleIntEnum.A), "<1: A>")


def test_int_enum_str():
    Asserter.assert_equals(str(SampleIntEnum.A), "A")


def test_int_enum_to_dict():
    Asserter.assert_equals(SampleIntEnum.A.to_dict(), {"id": 1, "label": "A"})


def test_int_enum_to_list():
    Asserter.assert_equals(
        SampleIntEnum.to_list(),
        [
            {"id": 1, "label": "A"},
            {"id": 2, "label": "B"},
            {"id": 3, "label": "C"},
        ],
    )


def test_str_enum():
    class Sample(StrEnum):
        EXAMPLE = enum.auto()

    Asserter.assert_equals(Sample.EXAMPLE, "EXAMPLE")
    Asserter.assert_equals(Sample.EXAMPLE.lower(), "example")


def test_lstr_enum():
    class Sample(LStrEnum):
        EXAMPLE = enum.auto()

    Asserter.assert_equals(Sample.EXAMPLE, "example")
    Asserter.assert_equals(Sample.EXAMPLE.upper(), "EXAMPLE")


def test_istr_enum():
    class Sample(IStrEnum):
        EXAMPLE = enum.auto()

    Asserter.assert_equals(Sample("EXAMPLE"), "example")
    Asserter.assert_equals(Sample.EXAMPLE, "example")
    Asserter.assert_equals(Sample.EXAMPLE, "EXAMPLE")
