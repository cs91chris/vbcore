from dataclasses import dataclass
from typing import Optional, Type

from vbcore import json
from vbcore.base import BaseDTO
from vbcore.json import JsonDecoder, JsonEncoder, OptCallableHook
from vbcore.types import CoupleStr, OptInt

from .base import DictBuilder, RecordType


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class JSONBuilderOptions(BaseDTO):
    skip_keys: bool = False
    ensure_ascii: bool = True
    check_circular: bool = True
    allow_nan: bool = True
    sort_keys: bool = False
    indent: OptInt = None
    separators: Optional[CoupleStr] = None
    default: OptCallableHook = None
    encoder: Type[JsonEncoder] = JsonEncoder
    decoder: Type[JsonDecoder] = JsonDecoder
    object_hook: OptCallableHook = None
    parse_float: OptCallableHook = None
    parse_int: OptCallableHook = None
    parse_constant: OptCallableHook = None
    object_pairs_hook: OptCallableHook = None


class JSONBuilder(DictBuilder[JSONBuilderOptions]):
    def to_dict(self, data: str) -> RecordType:
        return json.loads(
            data,
            cls=self.options.decoder,
            object_hook=self.options.object_hook,
            parse_float=self.options.parse_float,
            parse_int=self.options.parse_int,
            parse_constant=self.options.parse_constant,
            object_pairs_hook=self.options.object_pairs_hook,
        )

    def to_self(self, data: RecordType) -> str:
        return json.dumps(
            data,
            skipkeys=self.options.skip_keys,
            ensure_ascii=self.options.ensure_ascii,
            check_circular=self.options.check_circular,
            allow_nan=self.options.allow_nan,
            cls=self.options.encoder,
            indent=self.options.indent,
            separators=self.options.separators,
            default=self.options.default,
            sort_keys=self.options.sort_keys,
        )
