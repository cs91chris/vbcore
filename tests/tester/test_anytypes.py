from dataclasses import dataclass

import pytest

from vbcore.tester import anytypes


@dataclass
class SampleDTO:
    a: int
    b: str


def test_equals() -> None:
    dto = SampleDTO(a=1, b="aaa")
    assert dto == anytypes.AnyType(SampleDTO)
    assert dto == SampleDTO(a=anytypes.ANY_INT, b=anytypes.ANY_STR)
    assert dto != SampleDTO(a=anytypes.ANY_INT, b=anytypes.ANY_INT)


@pytest.mark.parametrize(
    "any_type, expected",
    [
        (anytypes.ANY_STR, "<AnyType=str>"),
        (anytypes.ANY_BYTES, "<AnyType=bytes>"),
        (anytypes.ANY_INT, "<AnyType=int>"),
        (anytypes.ANY_FLOAT, "<AnyType=float>"),
        (anytypes.ANY_TUPLE, "<AnyType=tuple>"),
        (anytypes.ANY_LIST, "<AnyType=list>"),
        (anytypes.ANY_SET, "<AnyType=set>"),
        (anytypes.ANY_DICT, "<AnyType=dict>"),
        (anytypes.ANY_UUID, "<AnyType=UUID>"),
        (anytypes.ANY_DECIMAL, "<AnyType=Decimal>"),
        (anytypes.ANY_DATE, "<AnyType=date>"),
        (anytypes.ANY_DATETIME, "<AnyType=datetime>"),
    ],
)
def test_repr(any_type: anytypes.AnyType, expected: str) -> None:
    assert repr(any_type) == expected
