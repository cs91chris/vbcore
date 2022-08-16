from vbcore.csvfile import CSVHandler
from vbcore.tester.mixins import Asserter

SAMPLE_CSV = """code;name
code-1;name-1
code-2;name-2
"""

UNSORTED = """A;B;C;D
2;1;3;1
1;2;1;3
3;3;2;2
2;1;1;1
1;2;3;3
"""

SAMPLE_RECORDS = [
    {"code": "code-1", "name": "name-1"},
    {"code": "code-2", "name": "name-2"},
]

UNSORTED_RECORDS = [
    dict(A="2", B="1", C="3", D="1"),
    dict(A="1", B="2", C="1", D="3"),
    dict(A="3", B="3", C="2", D="2"),
    dict(A="2", B="1", C="1", D="1"),
    dict(A="1", B="2", C="3", D="3"),
]

SORTED_RECORDS = [
    dict(A="1", B="2", C="1", D="3"),
    dict(A="1", B="2", C="3", D="3"),
    dict(A="2", B="1", C="1", D="1"),
    dict(A="2", B="1", C="3", D="1"),
    dict(A="3", B="3", C="2", D="2"),
]


def test_csv_file_reader(tmpdir):
    handler = CSVHandler()
    file = tmpdir.join("test_csv_file_reader.csv")
    file.write(SAMPLE_CSV.encode())
    Asserter.assert_equals(list(handler.readlines(file.strpath)), SAMPLE_RECORDS)


def test_csv_file_writer(tmpdir):
    file = tmpdir.join("test_csv_file_writer.csv")
    handler = CSVHandler(fields=["code", "name"])
    handler.write_all(SAMPLE_RECORDS, filename=file.strpath)
    Asserter.assert_equals(file.read_text(encoding="utf-8"), SAMPLE_CSV)


def test_csv_sort(tmpdir):
    file = tmpdir.join("test_csv_sort.csv")
    file.write(UNSORTED.encode())

    handler = CSVHandler(file.strpath)
    Asserter.assert_equals(list(handler.readlines(file.strpath)), UNSORTED_RECORDS)

    handler.sort(columns=["A", "C"])
    Asserter.assert_equals(list(handler.readlines(file.strpath)), SORTED_RECORDS)
