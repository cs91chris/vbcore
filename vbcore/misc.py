import functools
import math
import re
import signal
import string
import sys
import typing as t
from random import SystemRandom
from threading import Lock


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


def random_string(length: int, alphabet: str = string.printable) -> str:
    return "".join(SystemRandom().choice(alphabet) for _ in range(length))


class Signal:
    @classmethod
    def handle_terminate(cls, signum, frame, callback: t.Callable = lambda: None):
        Printer.error(f"received signal: {signum} at frame: {frame}")
        callback()
        sys.exit(signum)

    @classmethod
    def register(cls, handler: t.Callable, *signals):
        for s in signals:
            try:
                sig = getattr(signal, s)
                signal.signal(sig, handler)
            except Exception as exc:  # pylint: disable=broad-except
                Printer.error(f"unable to register signal {s}: {exc}")


class MemoryUsage:
    @classmethod
    def sizeof_fmt(cls, num: float, units: t.Sequence[str] = ()) -> str:
        _units = units or ("B", "KB", "MB", "GB")
        for unit in _units[:-1]:
            if abs(num) < 1000.0:
                return f"{num:.2f} {unit}"
            num /= 1000.0
        return f"{num:.2f} {units[-1]}"

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
