from dataclasses import dataclass
from typing import Any, List, TYPE_CHECKING

from defusedxml.ElementTree import XML

from vbcore.base import BaseDTO
from vbcore.data.transformations.builders.base import DictBuilder, RecordType
from vbcore.misc import parse_value
from vbcore.types import OptStr

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element  # nosec
else:
    Element = Any


class Dict2Html:
    tag_open_table_id = '<table id="{id}">'
    tag_open_table = "<table>"
    tag_close_table = "</table>"
    tag_open_head = "<thead>"
    tag_close_head = "</thead>"
    tag_open_body = "<tbody>"
    tag_close_body = "</tbody>"
    tag_open_row = "<tr>"
    tag_close_row = "</tr>"
    tag_open_h_col = "<th>"
    tag_close_h_col = "</th>"
    tag_open_col = "<td>"
    tag_close_col = "</td>"

    def __init__(self, without_headers: bool = False, pretty: bool = False):
        self.without_headers = without_headers
        self.ident = " " * 4 if pretty else ""
        self.separator = "\n" if pretty else ""

    def prepare_header_col(self, value: str) -> str:
        return f"{self.ident}{self.tag_open_h_col}{value}{self.tag_close_h_col}"

    def prepare_row_col(self, value: str) -> str:
        return f"{self.ident}{self.tag_open_col}{value}{self.tag_close_col}"

    def prepare_headers(self, rows: List[dict]) -> List[str]:
        if self.without_headers is False and len(rows):
            return list(rows[0].keys())
        return []

    def dump_header(self, headers: List[str]) -> List[str]:
        return [
            self.tag_open_head,
            self.tag_open_row,
            *[self.prepare_header_col(hdr) for hdr in headers],
            self.tag_close_row,
            self.tag_close_head,
        ]

    def dump_row(self, row: dict) -> List[str]:
        return [
            self.tag_open_row,
            *[self.prepare_row_col(value) for value in row.values()],
            self.tag_close_row,
        ]

    def dump_body(self, rows: List[dict]) -> List[str]:
        dumped = []
        for row in rows:
            dumped.extend(self.dump_row(row))
        return [self.tag_open_body, *dumped, self.tag_close_body]

    def build(self, rows: List[dict], table_id: str | None = None) -> str:
        headers = self.prepare_headers(rows)
        tag_open_table = (
            self.tag_open_table_id.format(id=table_id)
            if table_id
            else self.tag_open_table
        )
        return f"{self.separator}".join(
            [
                tag_open_table,
                *self.dump_header(headers),
                *self.dump_body(rows),
                self.tag_close_table,
            ]
        )


class Html2Dict:
    def __init__(
        self,
        forbid_dtd: bool = False,
        forbid_entities: bool = True,
        forbid_external: bool = True,
        xpath_table: OptStr = None,
        xpath_head: OptStr = None,
        xpath_body: OptStr = None,
        xpath_head_item: OptStr = None,
        xpath_col: OptStr = None,
        xpath_row: OptStr = None,
    ):
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities
        self.forbid_external = forbid_external
        self.xpath_table = xpath_table or ".//table"
        self.xpath_head = xpath_head or ".//thead"
        self.xpath_head_item = xpath_head_item or ".//th"
        self.xpath_body = xpath_body or ".//tbody"
        self.xpath_col = xpath_col or ".//td"
        self.xpath_row = xpath_row or ".//tr"

    def parse(self, text: str) -> Element:
        return XML(
            text,
            forbid_dtd=self.forbid_dtd,
            forbid_entities=self.forbid_entities,
            forbid_external=self.forbid_external,
        )

    def prepare_table(self, text: str) -> Element:
        root = self.parse(text)
        return root.find(self.xpath_table) or root

    @classmethod
    def extract_text(cls, elem: Element) -> str:
        return parse_value("".join(elem.itertext()))

    def extract_header(self, head: Element) -> List[str]:
        headers = [
            self.extract_text(elem) for elem in head.findall(self.xpath_head_item)
        ]
        if not headers:
            raise ValueError("no headers found")
        return headers

    def extract_row(self, headers: List[str], row: Element) -> dict:
        return {
            headers[index]: self.extract_text(col)
            for index, col in enumerate(row.findall(self.xpath_col))
        }

    def build(self, text: str) -> List[dict]:
        table = self.prepare_table(text)
        headers = self.extract_header(table.find(self.xpath_head))
        body = table.find(self.xpath_body)
        return [self.extract_row(headers, row) for row in body.findall(self.xpath_row)]


@dataclass(frozen=True)
class HTMLBuilderOptions(BaseDTO):
    table_id: OptStr = None
    without_headers: bool = False
    pretty: bool = False
    xpath_table: OptStr = None
    xpath_head: OptStr = None
    xpath_body: OptStr = None
    xpath_head_item: OptStr = None
    xpath_col: OptStr = None
    xpath_row: OptStr = None


class HTMLBuilder(DictBuilder[HTMLBuilderOptions]):
    def to_dict(self, data: str) -> RecordType:
        builder = Html2Dict(
            xpath_table=self.options.xpath_table,
            xpath_head=self.options.xpath_head,
            xpath_body=self.options.xpath_body,
            xpath_head_item=self.options.xpath_head_item,
            xpath_col=self.options.xpath_col,
            xpath_row=self.options.xpath_row,
        )
        return builder.build(data)

    def to_self(self, data: RecordType) -> str:
        builder = Dict2Html(
            without_headers=self.options.without_headers,
            pretty=self.options.pretty,
        )
        _data = [data] if isinstance(data, dict) else list(data)
        return builder.build(_data, table_id=self.options.table_id)
