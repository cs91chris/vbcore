import pytest

from vbcore.lambdas import Op
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "closed, left, right, value",
    [
        (False, False, False, 3),
        (True, False, False, 1),
        (True, False, False, 5),
        (False, True, False, 1),
        (False, False, True, 5),
    ],
)
def test_op_in_range_true(closed, left, right, value):
    expected = Op.in_range(value, [1, 5], closed=closed, left=left, right=right)
    Asserter.assert_true(expected)


@pytest.mark.parametrize(
    "closed, left, right, value",
    [
        (False, False, False, 6),
        (False, False, False, 5),
        (False, False, False, 1),
        (False, True, False, 5),
        (False, False, True, 1),
    ],
)
def test_op_in_range_false(closed, left, right, value):
    expected = Op.in_range(value, [1, 5], closed=closed, left=left, right=right)
    Asserter.assert_false(expected)
