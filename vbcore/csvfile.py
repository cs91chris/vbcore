import csv
import typing as t

OptStr = t.Optional[str]
RecordType = t.Union[dict, t.Iterable[dict]]
WriterCoroutineType = t.Generator[None, RecordType, None]


class CustomUnixDialect(csv.unix_dialect):
    delimiter = ";"
    quoting = csv.QUOTE_MINIMAL


csv.register_dialect("custom-unix", CustomUnixDialect)


class CSVHandler:
    def __init__(
        self,
        fields: t.Set[str] = None,
        filename: OptStr = None,
        encoding: str = "utf-8",
        dialect: str = "custom-unix",
    ):
        self.fields = fields or set()
        self.filename = filename
        self.encoding = encoding
        self.dialect = dialect

    def open_file(self, filename: OptStr = None, **kwargs):
        return open(filename or self.filename, encoding=self.encoding, **kwargs)

    # noinspection PyMethodMayBeStatic
    def after_read_hook(self, record: dict) -> dict:
        return record

    # noinspection PyMethodMayBeStatic
    def pre_write_hook(self, record: dict) -> dict:
        return record

    def readlines(self, filename: OptStr = None) -> t.Generator[dict, None, None]:
        with self.open_file(filename) as file:
            reader = csv.DictReader(file, dialect=self.dialect)
            for record in reader:
                yield self.after_read_hook(record)

    def coroutine_writer(self, filename: OptStr = None) -> WriterCoroutineType:
        with self.open_file(filename, mode="w") as file:
            writer = csv.DictWriter(file, self.fields, dialect=self.dialect)
            writer.writeheader()
            while True:
                records: RecordType = yield
                _records = [records] if isinstance(records, dict) else records
                for r in _records:
                    writer.writerow(self.pre_write_hook(r))

    def open_writer(self, filename: OptStr = None) -> WriterCoroutineType:
        # pylint: disable=assignment-from-no-return
        writer = self.coroutine_writer(filename)
        writer.__next__()
        return writer

    def write_all(self, records: RecordType, filename: OptStr = None):
        writer = self.open_writer(filename)
        writer.send(records)
        writer.close()
