from dataclasses import dataclass

import yaml

from vbcore.base import BaseDTO
from vbcore.types import OptAny, OptInt

from .base import DictBuilder, RecordType


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class YAMLBuilderOptions(BaseDTO):
    default_flow_style: bool = False
    indent: OptInt = None
    width: OptInt = None
    encoding: str = "utf-8"
    sort_keys: bool = True
    default_style: OptAny = None
    canonical: OptAny = None
    allow_unicode: OptAny = None
    line_break: OptAny = None
    explicit_start: OptAny = None
    explicit_end: OptAny = None
    version: OptAny = None
    tags: OptAny = None


class YAMLBuilder(DictBuilder[YAMLBuilderOptions]):
    def to_dict(self, data: str) -> RecordType:
        return yaml.safe_load(data)

    def to_self(self, data: RecordType) -> str:
        bytes_data = yaml.safe_dump(
            data,
            default_style=self.options.default_style,
            default_flow_style=self.options.default_flow_style,
            canonical=self.options.canonical,
            indent=self.options.indent,
            width=self.options.width,
            allow_unicode=self.options.allow_unicode,
            line_break=self.options.line_break,
            encoding=self.options.encoding,
            explicit_start=self.options.explicit_start,
            explicit_end=self.options.explicit_end,
            version=self.options.version,
            tags=self.options.tags,
            sort_keys=self.options.sort_keys,
        )
        return bytes_data.decode(encoding=self.options.encoding)
