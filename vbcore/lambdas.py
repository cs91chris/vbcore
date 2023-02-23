import operator as op
import typing as t
from decimal import Decimal

from vbcore.types import CoupleAny

T = t.TypeVar("T")


def op_in(a, b) -> bool:
    return a in b


def op_not_in(a, b) -> bool:
    return a not in b


def op_in_range(
    value: t.Any,
    range_: CoupleAny,
    *,
    closed: bool = False,
    left: bool = False,
    right: bool = False,
) -> bool:
    low, high = range_
    opg, opl = op.gt, op.lt

    if op.or_(op.truth(closed), op.and_(left, right)):
        opg, opl = op.ge, op.le
    elif op.truth(left):
        opg, opl = op.ge, op.lt
    elif op.truth(right):
        opg, opl = op.gt, op.le

    return op.and_(opg(value, low), opl(value, high))


class OpMeta(type):
    def __getattr__(cls, item):
        return getattr(op, item)


class Op(metaclass=OpMeta):
    @classmethod
    def in_(cls, a, b) -> bool:
        return op_in(a, b)

    @classmethod
    def not_in(cls, a, b) -> bool:
        return op_not_in(a, b)

    @classmethod
    def in_range(
        cls,
        value: t.Any,
        range_: CoupleAny,
        *,
        closed: bool = False,
        left: bool = False,
        right: bool = False,
    ) -> bool:
        return op_in_range(value, range_, closed=closed, left=left, right=right)


def chunk_iterator(
    iterable: t.Iterable[T], chunk_size: int
) -> t.Generator[t.List[T], None, None]:
    _iterable = iter(iterable)

    while True:
        chunk = []
        try:
            for _ in range(chunk_size):
                chunk.append(next(_iterable))
            yield chunk
        except StopIteration:
            if chunk:
                yield chunk
            break


def format_decimal(value: Decimal, precision: int = 8) -> str:
    if value.is_zero():
        return "0"

    str_fmt = f"{{:.{precision}f}}"
    return str_fmt.format(value).rstrip("0").rstrip(".")
