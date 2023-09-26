from vbcore.exceptions import ArgsDumperException
from vbcore.tester.asserter import Asserter


class SampleException(ArgsDumperException):
    message = "sample error"


def test_sample_exception() -> None:
    exc = SampleException(a=123, b="123", c=[1, 2, 3])
    Asserter.assert_equals(str(exc), "sample error: a=123, b='123', c=[1, 2, 3]")
