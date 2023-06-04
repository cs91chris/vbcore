from dataclasses import dataclass

import xmltodict

from vbcore.base import BaseDTO
from vbcore.misc import parse_value
from vbcore.types import StrTuple

from .base import DictBuilder, RecordType
from .dicttoxml import dicttoxml


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class XMLBuilderOptions(BaseDTO):
    root: bool = True
    custom_root: str = "ROOT"
    xml_declaration: bool = True
    attr_type: bool = True
    default_item_name: str = "ROW"
    cdata: bool = False
    encoding: str = "utf-8"
    force_list: StrTuple = ()
    attributes: bool = False
    process_namespaces: bool = False
    namespace_separator: str = ":"
    disable_entities: bool = True
    process_comments: bool = False


class XMLBuilder(DictBuilder[XMLBuilderOptions]):
    def post_processor(self, path, key, value):
        _, name = path, self.options.default_item_name
        if isinstance(value, dict) and name in value:
            return key, value[name]
        if isinstance(value, str):
            return key, parse_value(value)
        return key, value

    def to_dict(self, data: str) -> RecordType:
        parsed = xmltodict.parse(
            data,
            encoding=self.options.encoding,
            process_namespaces=self.options.process_namespaces,
            namespace_separator=self.options.namespace_separator,
            disable_entities=self.options.disable_entities,
            process_comments=self.options.process_comments,
            force_list=self.options.force_list or (self.options.default_item_name,),
            xml_attribs=self.options.attributes,
            postprocessor=self.post_processor,
        )
        if self.options.custom_root in parsed:
            return parsed[self.options.custom_root]
        return parsed

    def to_self(self, data: RecordType) -> str:
        return dicttoxml(
            data,
            root=self.options.root,
            custom_root=self.options.custom_root,
            xml_declaration=self.options.xml_declaration,
            attr_type=self.options.attr_type,
            default_item_name=self.options.default_item_name,
            cdata=self.options.cdata,
            encoding=self.options.encoding,
        )
