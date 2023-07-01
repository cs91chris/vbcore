from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Union

OptAny = Optional[Any]
OptStr = Optional[str]
OptInt = Optional[int]
OptBool = Optional[bool]
OptFloat = Optional[float]
OptDict = Optional[dict]
OptExc = Optional[Exception]

StrDict = Dict[str, Any]
IntDict = Dict[int, Any]
StrList = List[str]
IntList = List[int]
StrTuple = Tuple[str, ...]
IntTuple = Tuple[int, ...]

CoupleAny = Tuple[Any, Any]
TripleAny = Tuple[Any, Any, Any]
CoupleStr = Tuple[str, str]
TripleStr = Tuple[str, str, str]
CoupleInt = Tuple[int, int]
TripleInt = Tuple[int, int, int]

BytesType = Union[bytes, bytearray, memoryview]
CallableDictType = Callable[[List[Tuple[str, Any]]], Any]

RegexType = Union[str, Pattern]
DateType = Union[date, datetime]
AnyDateType = Union[DateType, str]


class MissingType:
    def __repr__(self) -> str:
        return "<MISSING>"


MISSING = MissingType()

MissingStr = Union[str, MissingType]
MissingInt = Union[int, MissingType]
MissingBool = Union[bool, MissingType]
MissingFloat = Union[float, MissingType]
