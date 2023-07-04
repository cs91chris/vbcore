import typing as t
from datetime import datetime

from dateutil.parser import parse as date_parse

from vbcore.base import Static
from vbcore.types import AnyDateType, DateType, OptStr


class Millis(metaclass=Static):
    seconds: t.ClassVar[int] = 1000
    minute: t.ClassVar[int] = seconds * 60
    hour: t.ClassVar[int] = minute * 60
    day: t.ClassVar[int] = hour * 24


class Seconds(metaclass=Static):
    millis: t.ClassVar[int] = 1000
    minute: t.ClassVar[int] = 60
    hour: t.ClassVar[int] = minute * 60
    day: t.ClassVar[int] = hour * 24


class Minutes(metaclass=Static):
    seconds: t.ClassVar[int] = 60
    hour: t.ClassVar[int] = 60
    day: t.ClassVar[int] = hour * 24


class Day(metaclass=Static):
    hours: t.ClassVar[int] = 24
    minutes: t.ClassVar[int] = hours * 60
    seconds: t.ClassVar[int] = minutes * 60


class DateTimeFmt(metaclass=Static):
    PRETTY: t.ClassVar[str] = "%d %B %Y %I:%M %p"
    ISO: t.ClassVar[str] = "%Y-%m-%dT%H:%M:%S"
    AS_NUM: t.ClassVar[str] = "%Y%m%d%H%M%S"


class DateFmt(metaclass=Static):
    PRETTY: t.ClassVar[str] = "%d %B %Y"
    ISO: t.ClassVar[str] = "%Y-%m-%d"
    AS_NUM: t.ClassVar[str] = "%Y%m%d"


class DateHelper:
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
        in_fmt: OptStr = None,
        raise_exc: bool = True,
    ) -> OptStr:
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
    def str_now(cls, is_utc: bool = True, tz=None, fmt: OptStr = None) -> str:
        """

        :param is_utc:
        :param tz:
        :param fmt:
        :return:
        """
        now = datetime.utcnow() if is_utc else datetime.now(tz)
        return cls.date_to_str(now, fmt)

    @classmethod
    def date_to_str(cls, date: DateType, fmt: OptStr = None) -> str:
        return date.strftime(fmt or DateTimeFmt.ISO)

    @classmethod
    def str_to_date(
        cls, date: str, fmt: OptStr = None, is_iso: bool = False, **kwargs
    ) -> datetime:
        """

        :param date: input string date
        :param fmt: format input date (optional: could be detected from string)
        :param is_iso: flag for implicit iso format
        :param kwargs: passed to date_parse
        :return: return parsed date
        """
        if is_iso is True:
            fmt = DateTimeFmt.ISO
        if fmt is None:
            return date_parse(date, **kwargs)

        date_obj = datetime.strptime(date, fmt)
        if date != cls.date_to_str(date_obj, fmt):
            raise ValueError(f"invalid date: {date}. Allowed format is {fmt}")
        return date_obj

    @classmethod
    def pretty_date(cls, date: AnyDateType) -> str:
        if isinstance(date, str):
            return cls.change_format(date, out_fmt=DateTimeFmt.PRETTY, raise_exc=True)
        return cls.date_to_str(date, fmt=DateTimeFmt.PRETTY)

    @classmethod
    def from_iso_format(
        cls, str_date: str, fmt: str, exc: bool = True
    ) -> t.Optional[str]:
        return DateHelper.change_format(
            str_date, in_fmt=DateTimeFmt.ISO, out_fmt=fmt, raise_exc=exc
        )

    @classmethod
    def to_iso_format(
        cls, str_date: str, fmt: OptStr = None, exc: bool = True
    ) -> t.Optional[str]:
        return DateHelper.change_format(
            str_date, in_fmt=fmt, out_fmt=DateTimeFmt.ISO, raise_exc=exc
        )
