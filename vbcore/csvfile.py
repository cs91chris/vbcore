import csv
import typing as t
from contextlib import contextmanager

from vbcore.files import FileHandler

OptStr = t.Optional[str]
RecordType = t.Union[dict, t.Iterable[dict]]
WriterCoroutineType = t.Generator[None, RecordType, None]


class CustomUnixDialect(csv.unix_dialect):
    delimiter = ";"
    quoting = csv.QUOTE_MINIMAL


csv.register_dialect("custom-unix", CustomUnixDialect)


class CSVHandler(FileHandler):
    def __init__(
        self,
        filename: OptStr = None,
        fields: t.Optional[t.List[str]] = None,
        encoding: str = "utf-8",
        dialect: str = "custom-unix",
    ):
        super().__init__(filename, encoding)
        self.fields = fields or []
        self.dialect = dialect

    @contextmanager
    def reader(
        self, filename: OptStr = None
    ) -> t.Generator[csv.DictReader, None, None]:
        with self.open(filename) as file:
            reader = csv.DictReader(file, dialect=self.dialect)
            self.fields = list(reader.fieldnames)
            yield reader

    @contextmanager
    def writer(
        self,
        filename: OptStr = None,
        fields: t.Optional[t.List[str]] = None,
        **kwargs,
    ) -> t.Generator[csv.DictWriter, None, None]:
        with self.open(filename, mode="w", **kwargs) as file:
            yield csv.DictWriter(file, fields or self.fields, dialect=self.dialect)

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
        columns: t.List[str],
        filename: OptStr = None,
        output_file: OptStr = None,
        **kwargs,
    ):
        with self.reader(filename) as reader:
            sortedlist = sorted(reader, key=lambda r: tuple(r[c] for c in columns))

        with self.open_writer(output_file, **kwargs) as writer:
            writer.send(self.pre_write_hook(r) for r in sortedlist)
