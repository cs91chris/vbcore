import datetime

from hypothesis import given, strategies as st

from vbcore.date_helper import DateHelper, from_iso_format, to_iso_format
from vbcore.tester.mixins import Asserter

SAMPLE_FMT = "%d %B %Y %I:%M %p"
ISO_DATE = "2020-12-28T19:53:00"
NOT_ISO_DATE = "28 December 2020 07:53 PM"


@given(
    st.dates(min_value=datetime.date(year=1000, month=1, day=1)).map(
        lambda d: d.strftime(SAMPLE_FMT)
    )
)
def test_iso_format_converter(str_date):
    Asserter.assert_equals(
        from_iso_format(to_iso_format(str_date, SAMPLE_FMT), SAMPLE_FMT), str_date
    )


def test_from_iso_format():
    res = from_iso_format(ISO_DATE, SAMPLE_FMT, exc=False)
    Asserter.assert_true(res)
    Asserter.assert_equals(NOT_ISO_DATE, res)
    Asserter.assert_none(from_iso_format("invalid_date", SAMPLE_FMT, exc=False))


def test_to_iso_format():
    res = to_iso_format(NOT_ISO_DATE, SAMPLE_FMT, exc=False)
    Asserter.assert_true(res)
    Asserter.assert_equals(ISO_DATE, res)
    res = to_iso_format(NOT_ISO_DATE, exc=False)
    Asserter.assert_true(res)
    Asserter.assert_equals(ISO_DATE, res)
    Asserter.assert_none(to_iso_format("invalid_date", SAMPLE_FMT, exc=False))


def test_is_weekend():
    Asserter.assert_true(DateHelper.is_weekend("5 September 2021"))
    Asserter.assert_false(DateHelper.is_weekend("2 September 2021"))


def test_pretty_date():
    iso_date = "2020-12-28T19:53:00"
    pretty_date = "28 December 2020 07:53 PM"
    datetime_iso = DateHelper.str_to_date(iso_date, is_iso=True)

    Asserter.assert_equals(DateHelper.pretty_date(iso_date), pretty_date)
    Asserter.assert_equals(DateHelper.pretty_date(datetime_iso), pretty_date)
