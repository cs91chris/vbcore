import logging
from datetime import date, datetime
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union

OptStr = Optional[str]
OptInt = Optional[int]
OptBool = Optional[bool]
OptFloat = Optional[float]

BytesType = Union[bytes, bytearray, memoryview]
CallableDictType = Callable[[List[Tuple[str, Any]]], Any]

DateType = Union[date, datetime]
AnyDateType = Union[DateType, str]

LogClass = TypeVar("LogClass", bound=logging.Logger)
