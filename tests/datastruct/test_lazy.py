import pytest

from vbcore.datastruct.lazy import BytesWrap, Dumper, LazyException
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
