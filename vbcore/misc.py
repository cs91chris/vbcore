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
    """

    :param length:
    :param alphabet:
    :return:
    """
    return "".join(SystemRandom().choice(alphabet) for _ in range(length))


class Signal:
    @classmethod
    def handle_terminate(cls, signum, frame, callback: t.Callable = lambda: None):
        Printer.error(f"received signal: {signum} at frame: {frame}")
        callback()
        sys.exit(signum)

    @classmethod
    def register(cls, handler: t.Callable, *signals):
        """

        :param handler:
        :param signals:
        """
        for s in signals:
            try:
                sig = getattr(signal, s)
                signal.signal(sig, handler)
            except Exception as exc:  # pylint: disable=broad-except
                Printer.error(f"unable to register signal {s}: {exc}")
