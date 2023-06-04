import csv
import io
import typing as t
from dataclasses import dataclass
from enum import Enum

from vbcore.base import BaseDTO
from vbcore.types import OptStr, StrTuple

from .base import DictBuilder


class CSVQuoting(Enum):
    ALL = csv.QUOTE_ALL
    NONE = csv.QUOTE_NONE
    MINIMAL = csv.QUOTE_MINIMAL
    NON_NUMERIC = csv.QUOTE_NONNUMERIC


@dataclass(frozen=True)
class CSVBuilderOptions(BaseDTO):
    delimiter: str = "|"
    quote_char: str = '"'
    columns: StrTuple = ()
    quoting: CSVQuoting = CSVQuoting.ALL
    escape_char: OptStr = None
    double_quote: bool = True
    skip_initial_space: bool = False
    line_terminator: str = "\n"


class CSVBuilder(DictBuilder[CSVBuilderOptions]):
    def to_dict(self, data: str) -> t.Union[dict, t.List[dict]]:
        reader = csv.DictReader(
            io.StringIO(data),
            fieldnames=self.options.columns or None,
            delimiter=self.options.delimiter,
            quotechar=self.options.quote_char,
            quoting=self.options.quoting.value,
            escapechar=self.options.escape_char,
            doublequote=self.options.double_quote,
            skipinitialspace=self.options.skip_initial_space,
            lineterminator=self.options.line_terminator,
        )
        records = list(reader)
        return records[0] if len(records) == 1 else records

    def to_self(self, data: dict) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=self.options.columns or data[0].keys(),
            delimiter=self.options.delimiter,
            quotechar=self.options.quote_char,
            quoting=self.options.quoting.value,
            escapechar=self.options.escape_char,
            doublequote=self.options.double_quote,
            skipinitialspace=self.options.skip_initial_space,
            lineterminator=self.options.line_terminator,
        )
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
