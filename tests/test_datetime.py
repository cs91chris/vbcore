from vbcore import datetime

from vbcore.tester.mixins import Asserter

DateHelper = datetime.DateHelper


def test_date_conversion():
    exc = False
    fmt = "%d %B %Y %I:%M %p"
    iso_date = "2020-12-28T19:53:00"
    pretty_date = not_iso_date = "28 December 2020 07:53 PM"
    invalid_date = "invalid_date"
    datetime_iso = DateHelper.str_to_date(iso_date, is_iso=True)

    res = datetime.from_iso_format(iso_date, fmt, exc=exc)
    Asserter.assert_true(res)
    Asserter.assert_equals(not_iso_date, res)

    res = datetime.to_iso_format(not_iso_date, fmt, exc=exc)
    Asserter.assert_true(res)
    Asserter.assert_equals(iso_date, res)
    res = datetime.to_iso_format(not_iso_date, exc=exc)
    Asserter.assert_true(res)
    Asserter.assert_equals(iso_date, res)

    Asserter.assert_none(datetime.from_iso_format(invalid_date, fmt, exc=exc))
    Asserter.assert_none(datetime.to_iso_format(invalid_date, fmt, exc=exc))

    Asserter.assert_true(DateHelper.is_weekend("5 September 2021"))
    Asserter.assert_false(DateHelper.is_weekend("2 September 2021"))

    Asserter.assert_equals(DateHelper.pretty_date(iso_date), pretty_date)
    Asserter.assert_equals(DateHelper.pretty_date(datetime_iso), pretty_date)
