import math
import os
import re
import signal
import string
import sys
import tempfile
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


def parse_value(v):
    """

    :param v:
    :return:
    """
    try:
        return float(v) if "." in v else int(v)
    except ValueError:
        if v.lower() in ("true", "false"):
            return v.lower() == "true"
    return v


def get_from_dict(d: dict, k, default=None):
    """
    get a value from dict without raising exceptions

    :param d: dict
    :param k: key
    :param default: default value if k is missing
    :return: d[k] or default
    """
    if isinstance(d, dict):
        return d.get(k, default)
    return default


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


def random_string(length: int, alphabet: str = string.printable) -> str:
    return "".join(SystemRandom().choice(alphabet) for _ in range(length))


def read_text_file(filename: t.Optional[str], **kwargs) -> t.Optional[str]:
    if not filename:
        return None

    encoding = kwargs.pop("encoding", "utf-8")
    with open(filename, encoding=encoding, **kwargs) as file:
        return file.read()


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


class TempFile:
    def __init__(self, data):
        self.data = data
        # pylint: disable=consider-using-with
        self.file = tempfile.NamedTemporaryFile(delete=False)

    def __enter__(self):
        self.file.write(self.data)
        self.file.close()
        return self.file

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.unlink(self.file.name)


class MemoryUsage:
    @classmethod
    def sizeof_fmt(cls, num: float) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if abs(num) < 1000.0:
                return f"{num:.2f} {unit}"
            num /= 1000.0
        return f"{num:.2f} TB"

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
