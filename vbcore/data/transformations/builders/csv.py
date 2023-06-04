import csv
import io
from dataclasses import dataclass
from enum import Enum

from vbcore.base import BaseDTO
from vbcore.types import OptStr, StrTuple

from .base import DictBuilder, RecordType


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
    escape_char: OptStr = None
    double_quote: bool = True
    skip_initial_space: bool = False
    line_terminator: str = "\n"
    quoting: CSVQuoting = CSVQuoting.MINIMAL


class CSVBuilder(DictBuilder[CSVBuilderOptions]):
    def to_dict(self, data: str) -> RecordType:
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
        return list(reader)

    def to_self(self, data: RecordType) -> str:
        _data = [data] if isinstance(data, dict) else data
        field_names = self.options.columns or _data[0].keys()
        output = io.StringIO()

        writer = csv.DictWriter(
            output,
            fieldnames=field_names,
            delimiter=self.options.delimiter,
            quotechar=self.options.quote_char,
            quoting=self.options.quoting.value,
            escapechar=self.options.escape_char,
            doublequote=self.options.double_quote,
            skipinitialspace=self.options.skip_initial_space,
            lineterminator=self.options.line_terminator,
        )

        writer.writeheader()
        writer.writerows(_data)
        return output.getvalue()
