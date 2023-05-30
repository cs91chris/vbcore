from decimal import Decimal

import pytest

from vbcore.stringutils.misc import (
    format_decimal,
    random_str_ascii_lowercase,
    random_string,
    random_string_alpha,
    random_string_ascii,
    random_string_ascii_uppercase,
    random_string_numeric,
)
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "random_function",
    [
        random_string,
        random_str_ascii_lowercase,
        random_string_ascii_uppercase,
        random_string_ascii,
        random_string_alpha,
        random_string_numeric,
    ],
    ids=lambda x: x.__name__,
)
def test_random_string(random_function):
    test_str = random_function(10)
    Asserter.assert_isinstance(test_str, str)
    Asserter.assert_len(test_str, 10)


@pytest.mark.parametrize(
    "value, expected",
    [
        (Decimal("0"), "0"),
        (Decimal("-0"), "0"),
        (Decimal("-0.0001"), "0"),
        (Decimal("123.12345"), "123.123"),
        (Decimal("123.00045"), "123"),
    ],
    ids=lambda x: f"({x})",
)
def test_format_decimal(value, expected):
    Asserter.assert_equals(format_decimal(value, precision=3), expected)
