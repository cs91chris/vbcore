import functools
import math
import re
import signal
import sys
import typing as t
import uuid
from threading import Lock

from vbcore.types import OptStr


class Printer:
    function = print
    thread_lock = Lock()

    @classmethod
    def safe(cls, *args, **kwargs):
        with cls.thread_lock:
            cls.function(*args, **kwargs)

    @classmethod
    def error(cls, *args, **kwargs):
        kwargs.setdefault("file", sys.stderr)
        cls.function(*args, **kwargs)

    @classmethod
    def safe_error(cls, *args, **kwargs):
        kwargs.setdefault("file", sys.stderr)
        cls.error(*args, **kwargs)


def parse_value(value: t.Any):
    """

    :param value:
    :return:
    """
    if value == "":
        return None
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        if value.lower() in ("y", "n"):
            return value.lower() == "y"
    return value


def to_int(n) -> t.Optional[int]:
    """
    cast input to int if an error occurred returns None

    :param n: input
    :return: int or None
    """
    try:
        return int(n)
    except (TypeError, ValueError):
        return None


def to_float(n) -> t.Optional[float]:
    """
    cast input to float if an error occurred returns None

    :param n: input
    :return: float or None
    """
    try:
        return float(n)
    except (TypeError, ValueError):
        return None


def split_kwargs(
    options: t.Iterable[str], **kwargs
) -> t.Tuple[t.Dict[str, t.Any], t.Dict[str, t.Any]]:
    """
    split kwargs into 2 dict:
        one with only `options` keys and another with the others

    :param options: wanted keys
    :param kwargs: all params
    :return: 2 dict: wanted and unwanted
    """
    wanted = {}

    for opt in options:
        try:
            wanted[opt] = kwargs.pop(opt)
        except KeyError:
            pass

    return wanted, kwargs


def static_attr(name: str, value):
    def wrapper(func):
        setattr(func, name, value)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        return inner

    return wrapper


class Signal:
    @classmethod
    def handle_terminate(cls, signum, frame, callback: t.Callable = lambda: None):
        Printer.error(f"received signal: {signum} at frame: {frame}")
        callback()
        sys.exit(signum)

    @classmethod
    def register(cls, handler: t.Callable, *signals: int):
        for s in signals:
            try:
                signal.signal(s, handler)
            except Exception as exc:  # pylint: disable=broad-except
                Printer.error(f"unable to register signal {s}: {exc}")


class MemoryUsage:
    @classmethod
    def sizeof_fmt(cls, num: float, units: t.Sequence[str] = ()) -> str:
        _units = units or ("B", "KB", "MB", "GB")

        if abs(num) < 1000.0:
            return f"{num} {_units[0]}"

        num /= 1000.0
        for unit in _units[1:-1]:
            if abs(num) < 1000.0:
                return f"{num:.2f} {unit}"
            num /= 1000.0

        return f"{num:.2f} {_units[-1]}"

    @classmethod
    def sizeof(cls, value: float) -> float:
        return sys.int_info.bits_per_digit * math.ceil(
            sys.getsizeof(value) / sys.int_info.sizeof_digit
        )

    @classmethod
    def get_variables(cls) -> t.Dict[str, t.Any]:
        return {**locals(), **globals()}

    @classmethod
    def view(cls, max_items: int = 10) -> t.Generator[t.Tuple[str, float], None, None]:
        items = sorted(
            ((n, cls.sizeof(v)) for n, v in cls.get_variables().items()),
            key=lambda x: -x[1],
        )
        return (item for item in items[:max_items])

    @classmethod
    def dump(cls, max_items: int = 10):
        for name, size in cls.view(max_items):
            print(f"{name:>30}: {cls.sizeof_fmt(size):>8}")


class CommonRegex:
    EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    @classmethod
    def is_valid_email(cls, email: str) -> bool:
        return bool(re.fullmatch(cls.EMAIL_REGEX, email))


def get_uuid(
    ver: int = 4,
    hex_: bool = True,
    name: OptStr = None,
    ns: t.Optional[uuid.UUID] = None,
) -> t.Union[str, uuid.UUID]:
    if ver == 1:
        _uuid = uuid.uuid1()
    elif ver == 3:
        _uuid = uuid.uuid3(ns or uuid.NAMESPACE_DNS, name)
    elif ver == 4:
        _uuid = uuid.uuid4()
    elif ver == 5:
        _uuid = uuid.uuid5(ns or uuid.NAMESPACE_DNS, name)
    else:
        raise TypeError(f"invalid uuid version {ver}")

    return _uuid.hex if hex_ else _uuid


def check_uuid(
    u: t.Union[str, uuid.UUID],
    ver: int = 4,
    raise_exc: bool = False,
) -> bool:
    try:
        if isinstance(u, uuid.UUID):
            return True

        _uuid = uuid.UUID(u, version=ver)
        return u == (str(_uuid) if "-" in u else _uuid.hex)
    except (ValueError, TypeError, AttributeError) as exc:
        if raise_exc:
            raise ValueError(f"'{u}' is an invalid UUID{ver}") from exc
        return False
