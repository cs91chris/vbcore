import pytest

from vbcore.datastruct.lazy import (
    BytesWrap,
    ClassDumper,
    Dumper,
    JsonDumper,
    LazyException,
    SignalDumper,
)
from vbcore.tester.asserter import Asserter


def test_lazy_exception():
    message = "VALUE ERROR"
    exc = LazyException(ValueError(message))

    with pytest.raises(ValueError) as error:
        _ = exc.get_attribute

    Asserter.assert_equals(str(exc), message)
    Asserter.assert_equals(error.value.args, (message,))


def test_dumper():
    data = "string"
    dumper = Dumper(data)

    Asserter.assert_different(dumper, data)
    Asserter.assert_equals(str(dumper), data)


def test_bytes_wrap():
    data = b"bytes"
    dumper = BytesWrap(data)

    Asserter.assert_different(dumper, data)
    Asserter.assert_equals(str(dumper), data.decode())


def test_class_dumper():
    class Sample:
        pass

    expected = "tests.datastruct.test_lazy:Sample"
    cls = ClassDumper(Sample)
    obj = ClassDumper(Sample())

    Asserter.assert_equals(str(cls), expected)
    Asserter.assert_equals(str(obj), expected)


def test_signal_dumper():
    data = 2
    dumper = SignalDumper(data)
    Asserter.assert_equals(str(dumper), "<SIGINT-2-Interrupt>")


def test_json_dumper():
    data = {"a": 1, "b": 1}
    dumper = JsonDumper(data)

    Asserter.assert_different(str(dumper), str(data))
    Asserter.assert_equals(str(dumper), '{"a": 1, "b": 1}')
