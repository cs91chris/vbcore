import signal
from unittest.mock import call, MagicMock, patch

import pytest

from vbcore import misc
from vbcore.misc import CommonRegex, MemoryUsage, Signal, split_kwargs, static_attr
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", 1.0),
        ("1.1", 1.1),
        ("1,1", None),
        ("aaa", None),
    ],
)
def test_to_float(value, expected):
    Asserter.assert_equals(misc.to_float(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", 1),
        ("1.1", None),
        ("1,1", None),
        ("aaa", None),
    ],
)
def test_to_int(value, expected):
    Asserter.assert_equals(misc.to_int(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", 1),
        ("1.1", 1.1),
        ("true", True),
        ("test", "test"),
    ],
    ids=[
        "int",
        "float",
        "bool",
        "string",
    ],
)
def test_parse_value(value, expected):
    Asserter.assert_equals(misc.parse_value(value), expected)


@pytest.mark.parametrize(
    "email, expected",
    [
        ("pippo@example.fake", True),
        ("p.pippo@example.fake", True),
        ("p-pippo@example.fake", True),
        ("123pippo@example.fake", True),
        ("pippo.example.com", False),
        ("pippo@example", False),
        ("pippo@example.é", False),
        ("p$pippo@example.fake", False),
    ],
)
def test_common_regex_valid_email(email, expected):
    assert_that = Asserter.assert_true if expected else Asserter.assert_false
    assert_that(CommonRegex.is_valid_email(email))


def test_split_kwargs():
    wanted, unwanted = split_kwargs(("a", "b"), a=1, b=2, c=3)
    Asserter.assert_equals(wanted, {"a": 1, "b": 2})
    Asserter.assert_equals(unwanted, {"c": 3})


def test_static_attr_decorator():
    @static_attr("attribute", "value")
    def sample():
        pass

    Asserter.assert_equals(sample.attribute, "value")


def test_memory_usage_dump():
    # NOTE: only for coverage
    Asserter.assert_none(MemoryUsage.dump())


@patch("vbcore.misc.signal.signal")
def test_signal_register(mock_signal: MagicMock):
    def handler():
        pass

    Signal.register(handler, signal.SIGHUP, signal.SIGINT)
    mock_signal.assert_has_calls(
        [
            call(signal.SIGHUP, handler),
            call(signal.SIGINT, handler),
        ]
    )


@patch("vbcore.misc.sys.exit")
def test_signal_handle_terminate(mock_sys_exit: MagicMock):
    signum = 255
    callback = MagicMock()
    Signal.handle_terminate(signum, MagicMock(), callback)
    callback.assert_called_once_with()
    mock_sys_exit.assert_called_once_with(signum)


def test_uuid_valid():
    Asserter.assert_true(misc.check_uuid(misc.get_uuid()))
    Asserter.assert_true(misc.check_uuid(misc.get_uuid(hex_=False)))


@pytest.mark.parametrize("version", (0, 2, 6))
def test_uuid_invalid_version(version):
    with pytest.raises(TypeError) as error:
        misc.get_uuid(ver=version)

    Asserter.assert_equals(error.value.args, (f"invalid uuid version {version}",))


@pytest.mark.parametrize("version", (1, 3, 4, 5))
def test_uuid_invalid(version):
    invalid_uuid = "fake uuid"

    Asserter.assert_false(misc.check_uuid(invalid_uuid, ver=version))

    with pytest.raises(ValueError) as error:
        misc.check_uuid(invalid_uuid, ver=version, raise_exc=True)

    Asserter.assert_equals(
        error.value.args, (f"'{invalid_uuid}' is an invalid UUID{version}",)
    )


@pytest.mark.parametrize(
    "version, name",
    [
        (1, None),
        (3, "test"),
        (4, None),
        (5, "test"),
    ],
)
def test_uuid_version(version, name):
    Asserter.assert_true(
        misc.check_uuid(misc.get_uuid(version, name=name), ver=version)
    )
