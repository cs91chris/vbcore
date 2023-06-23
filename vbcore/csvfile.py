import csv
import typing as t
from contextlib import contextmanager
from dataclasses import dataclass, field

from vbcore.exceptions import VBEmptyFileError
from vbcore.files import FileHandler, OptStr
from vbcore.types import OptInt, StrList

RecordType = t.Union[dict, t.Iterable[dict]]
WriterCoroutineType = t.Generator[None, RecordType, None]


@dataclass(frozen=True, kw_only=True)
class CSVParams:
    new_line: str = ""
    encoding: str = "utf-8"
    delimiter: str = "|"
    dialect: str = "unix"
    encoding_errors: str = "replace"
    quoting: int = csv.QUOTE_NONE
    escape_char: str = "\\"
    allow_extra_fields: bool = True
    supported_encodings: t.List[str] = field(
        default_factory=lambda: ["ascii", "ISO-8859-1"]
    )


class CSVHandler(FileHandler):
    def __init__(
        self,
        filename: OptStr = None,
        fields: t.Optional[StrList] = None,
        params: t.Optional[CSVParams] = None,
    ):
        self.fields = fields or []
        self.params = params or CSVParams()
        super().__init__(
            filename, self.params.encoding, self.params.supported_encodings
        )

    def open(self, filename: OptStr = None, **kwargs) -> t.IO:
        return super().open(
            filename,
            newline=self.params.new_line,
            encoding=self.params.encoding,
            errors=self.params.encoding_errors,
            **kwargs,
        )

    def raise_for_empty(self, filename: OptStr = None, lines: OptInt = None):
        lines = lines or self.num_lines(filename or self.filename)
        if lines <= 0:
            raise VBEmptyFileError(
                filename,
                "no record found in the file" if lines == 0 else "header is missing",
            )

    @contextmanager
    def reader(
        self, filename: OptStr = None
    ) -> t.Generator[csv.DictReader, None, None]:
        with self.open(filename) as file:
            reader = csv.DictReader(
                file,
                delimiter=self.params.delimiter,
                quoting=self.params.quoting,
                escapechar=self.params.escape_char,
            )
            self.fields = list(reader.fieldnames)
            yield reader

    @contextmanager
    def writer(
        self,
        filename: OptStr = None,
        fields: t.Optional[StrList] = None,
        **kwargs,
    ) -> t.Generator[csv.DictWriter, None, None]:
        with self.open(filename, mode="w", **kwargs) as file:
            yield csv.DictWriter(
                file,
                fields or self.fields,
                delimiter=self.params.delimiter,
                dialect=self.params.dialect,
                quoting=self.params.quoting,
                escapechar=self.params.escape_char,
            )

    # noinspection PyMethodMayBeStatic
    def after_read_hook(self, record: dict) -> t.Any:
        return record

    def pre_write_hook(self, record: dict) -> t.Any:
        return {k: v for k, v in record.items() if k in self.fields}

    def readlines(self, filename: OptStr = None) -> t.Generator[dict, None, None]:
        with self.reader(filename) as reader:
            for record in reader:
                yield self.after_read_hook(record)

    def coroutine_writer(
        self, filename: OptStr = None, **kwargs
    ) -> WriterCoroutineType:
        with self.writer(filename, **kwargs) as writer:
            writer.writeheader()
            while True:
                records: RecordType = (yield)  # noqa: E275
                _records = [records] if isinstance(records, dict) else records
                for r in _records:
                    writer.writerow(self.pre_write_hook(r))

    @contextmanager
    def open_writer(
        self, filename: OptStr = None, **kwargs
    ) -> t.Generator[WriterCoroutineType, None, None]:
        # pylint: disable=assignment-from-no-return
        writer = self.coroutine_writer(filename, **kwargs)
        # pylint: disable=unnecessary-dunder-call
        writer.__next__()
        yield writer
        writer.close()

    def write_all(self, records: RecordType, filename: OptStr = None, **kwargs):
        with self.open_writer(filename, **kwargs) as writer:
            writer.send(records)

    def sort(
        self,
        columns: StrList,
        filename: OptStr = None,
        output_file: OptStr = None,
        **kwargs,
    ):
        with self.reader(filename) as reader:
            sortedlist = sorted(reader, key=lambda r: tuple(r[c] for c in columns))

        with self.open_writer(output_file, **kwargs) as writer:
            writer.send(self.pre_write_hook(r) for r in sortedlist)
