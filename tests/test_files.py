import pytest

from vbcore.files import FileHandler, VBEncodingError
from vbcore.tester.asserter import Asserter


def test_count_lines(tmpdir):
    file = tmpdir.join("test_count_lines.csv")
    file.write("AAA\nBBB\nCCC\nDDD".encode())
    handler = FileHandler(file.strpath)

    Asserter.assert_equals(handler.num_lines(), 4)


def test_detect_encoding_utf_8(tmpdir):
    file = tmpdir.join("test_detect_encoding_utf_8.txt")
    file.write("\xe0\xe0")

    reader = FileHandler()
    result = reader.detect_encoding(file.strpath)

    Asserter.assert_equals(result.encoding, "utf-8")
    Asserter.assert_greater(result.confidence, 0.70)
    Asserter.assert_equals(result.language, "")


def test_detect_encoding_ascii(tmpdir):
    file = tmpdir.join("test_detect_encoding_ascii.txt")
    file.write("TEST")

    reader = FileHandler()
    result = reader.detect_encoding(file.strpath)

    Asserter.assert_equals(result.encoding, "ascii")
    Asserter.assert_greater(result.confidence, 0.70)
    Asserter.assert_equals(result.language, "")


def test_check_encoding(tmpdir):
    file = tmpdir.join("test_check_encoding.txt")
    file.write("TEST")

    reader = FileHandler()
    with pytest.raises(VBEncodingError) as error:
        reader.check_encoding(file.strpath)

    Asserter.assert_equals(error.value.filename, file.strpath)
    Asserter.assert_equals(error.value.encoding, "ascii")
    Asserter.assert_greater(error.value.confidence, 0.70)
    Asserter.assert_equals(error.value.language, "")
    Asserter.assert_equals(error.value.supported, ["utf-8"])
