from dataclasses import dataclass

import xmltodict

from vbcore.base import BaseDTO

from .base import DictBuilder
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
    process_namespaces: bool = False
    namespace_separator: str = ":"
    disable_entities: bool = True
    process_comments: bool = False


class XMLBuilder(DictBuilder[XMLBuilderOptions]):
    def to_dict(self, data: str) -> dict:
        return xmltodict.parse(
            data,
            encoding=self.options.encoding,
            process_namespaces=self.options.process_namespaces,
            namespace_separator=self.options.namespace_separator,
            disable_entities=self.options.disable_entities,
            process_comments=self.options.process_comments,
        )

    def to_self(self, data: dict) -> str:
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
