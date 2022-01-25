from collections import OrderedDict

from vbcore.csvfile import CSVHandler

SAMPLE_CSV = """code;name
code-1;name-1
code-2;name-2
"""


def test_csv_file_reader(tmpdir):
    handler = CSVHandler()
    file = tmpdir.join("test_csv_file_reader.csv")
    file.write(SAMPLE_CSV.encode())

    assert list(handler.readlines(file.strpath)) == [
        {"code": "code-1", "name": "name-1"},
        {"code": "code-2", "name": "name-2"},
    ]


def test_csv_file_writer(tmpdir):
    records = (
        OrderedDict(**{"code": "code-1", "name": "name-1"}),
        OrderedDict(**{"code": "code-2", "name": "name-2"}),
    )
    file = tmpdir.join("test_csv_file_writer.csv")
    handler = CSVHandler(fields={"code", "name"})
    handler.write_all(records, filename=file.strpath)
    assert file.read_text(encoding="utf-8") == SAMPLE_CSV
