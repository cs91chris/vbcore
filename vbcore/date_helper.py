import typing as t
from datetime import datetime, date as datetime_date

from dateutil.parser import parse as date_parse


class Millis:
    seconds: int = 1000
    minute: int = seconds * 60
    hour: int = minute * 60
    day: int = hour * 24


class Seconds:
    millis: int = 1000
    minute: int = 60
    hour: int = minute * 60
    day: int = hour * 24


class Minutes:
    seconds: int = 60
    hour: int = 60
    day: int = hour * 24


class Day:
    hours: int = 24
    minutes: int = hours * 60
    seconds: int = minutes * 60


DateType = t.Union[datetime_date, datetime]
AnyDateType = t.Union[DateType, str]


class DateHelper:
    DATE_PRETTY_FORMAT = "%d %B %Y %I:%M %p"
    DATE_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"

    @classmethod
    def is_weekend(cls, curr_date: AnyDateType, **kwargs) -> bool:
        """

        :param curr_date: date instance or string date
        :param kwargs: passed to dateutil.parser.parse
        :return: boolean, True if is weekend
        """
        if isinstance(curr_date, str):
            curr_date = date_parse(curr_date, **kwargs)

        return curr_date.weekday() > 4

    @classmethod
    def change_format(
        cls,
        str_date: str,
        out_fmt: str,
        in_fmt: t.Optional[str] = None,
        raise_exc: bool = True,
    ) -> t.Optional[str]:
        """

        :param str_date: input string date
        :param out_fmt: format output date
        :param in_fmt: format input date (optional: could be detected from string)
        :param raise_exc: raise or not exception (default True)
        :return: return formatted date
        """
        if not (raise_exc or str_date):
            return None  # pragma: no cover

        try:
            date_time = cls.str_to_date(str_date, in_fmt)
            return date_time.strftime(out_fmt)
        except (ValueError, TypeError):
            if raise_exc is True:
                raise  # pragma: no cover
        return None

    @classmethod
    def now_iso_string(cls, is_utc: bool = True, tz=None) -> str:
        now = datetime.utcnow() if is_utc else datetime.now()
        return cls.date_to_str(now, tz)

    @classmethod
    def date_to_str(cls, date: DateType, fmt: t.Optional[str] = None) -> str:
        return date.strftime(fmt or cls.DATE_ISO_FORMAT)

    @classmethod
    def str_to_date(
        cls, date: str, fmt: t.Optional[str] = None, is_iso: bool = False, **kwargs
    ) -> datetime:
        """

        :param date: input string date
        :param fmt: format input date (optional: could be detected from string)
        :param is_iso: flag for implicit iso format
        :param kwargs: passed to date_parse
        :return: return parsed date
        """
        if is_iso is True:
            fmt = cls.DATE_ISO_FORMAT
        if fmt is None:
            return date_parse(date, **kwargs)

        date_obj = datetime.strptime(date, fmt)
        if date != cls.date_to_str(date_obj, fmt):
            raise ValueError(f"invalid date: {date}. Allowed format is {fmt}")
        return date_obj

    @classmethod
    def pretty_date(cls, date: AnyDateType):
        if isinstance(date, str):
            return cls.change_format(
                date, out_fmt=cls.DATE_PRETTY_FORMAT, raise_exc=True
            )
        return cls.date_to_str(date, fmt=cls.DATE_PRETTY_FORMAT)


def from_iso_format(str_date, fmt, exc=True):
    return DateHelper.change_format(
        str_date, in_fmt=DateHelper.DATE_ISO_FORMAT, out_fmt=fmt, raise_exc=exc
    )


def to_iso_format(str_date, fmt=None, exc=True):
    return DateHelper.change_format(
        str_date, in_fmt=fmt, out_fmt=DateHelper.DATE_ISO_FORMAT, raise_exc=exc
    )
