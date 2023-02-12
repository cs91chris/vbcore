from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

OptStr = Optional[str]
OptInt = Optional[int]
OptBool = Optional[bool]
OptFloat = Optional[float]

StrDict = Dict[str, Any]

BytesType = Union[bytes, bytearray, memoryview]
CallableDictType = Callable[[List[Tuple[str, Any]]], Any]

DateType = Union[date, datetime]
AnyDateType = Union[DateType, str]

CoupleStr = Tuple[str, str]
TripleStr = Tuple[str, str, str]
