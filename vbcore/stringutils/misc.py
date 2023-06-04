import string
from decimal import Decimal
from random import SystemRandom

ALPHA_CHARS = string.digits + string.ascii_letters
ALL_CHARS = ALPHA_CHARS + string.punctuation + " "


def random_string(length: int, alphabet: str = ALL_CHARS) -> str:
    return "".join(SystemRandom().choice(alphabet) for _ in range(length))


def random_str_ascii_lowercase(length: int) -> str:
    return random_string(length, alphabet=string.ascii_lowercase)


def random_string_ascii_uppercase(length: int) -> str:
    return random_string(length, alphabet=string.ascii_uppercase)


def random_string_ascii(length: int) -> str:
    return random_string(length, alphabet=string.ascii_letters)


def random_string_alpha(length: int) -> str:
    return random_string(length, alphabet=ALPHA_CHARS)


def random_string_numeric(length: int) -> str:
    return random_string(length, alphabet=string.digits)


def format_decimal(value: Decimal, precision: int = 8) -> str:
    if value.is_zero():
        return "0"

    string_format = f"{{:.{precision}f}}"
    raw_string = string_format.format(value)
    formatter_value = raw_string.rstrip("0").rstrip(".")

    if Decimal(formatter_value).is_zero():
        return "0"

    return formatter_value
