import os

import pytest

from vbcore.configurator import config, load_dotenv
from vbcore.tester.mixins import Asserter

TEST_ENV_BOOL = "TEST_ENV_BOOL"
TEST_ENV_FLOAT = "TEST_ENV_FLOAT"
SAMPLE_ENVVAR = "sample-env"


@pytest.fixture(scope="function")
def mock_envvar(monkeypatch):
    monkeypatch.setitem(os.environ, TEST_ENV_BOOL, "1")
    monkeypatch.setitem(os.environ, TEST_ENV_FLOAT, "1.234")
    monkeypatch.setitem(os.environ, "SAMPLE", SAMPLE_ENVVAR)


def test_load_dot_env():
    Asserter.assert_true(load_dotenv)


@pytest.mark.parametrize(
    "envvar, default, cast, expected",
    [
        ("SAMPLE", None, str, SAMPLE_ENVVAR),
        ("SAMPLE", None, lambda x: x.upper(), SAMPLE_ENVVAR.upper()),
        ("NOENV", "none", str, "none"),
        (TEST_ENV_BOOL, None, bool, True),
        (TEST_ENV_FLOAT, None, float, 1.234),
    ],
    ids=[
        "envvar_exists",
        "cast_envvar",
        "no_envvar_use_default",
        "envvar_bool",
        "envvar_float",
    ],
)
def test_from_environ_ok(
    envvar, default, cast, expected, mock_envvar
):  # pylint: disable=redefined-outer-name,unused-argument
    assert config.from_environ(envvar, default, cast=cast) == expected


@pytest.mark.parametrize(
    "envvar, required, cast, expected_exc, error_message",
    [
        (
            "NOT_FOUND",
            True,
            str,
            EnvironmentError,
            "envvar 'NOT_FOUND' required or provide a default",
        ),
        (
            "SAMPLE",
            False,
            int,
            ValueError,
            "unable to cast config key 'SAMPLE' to type: <class 'int'>",
        ),
    ],
    ids=["envvar_required", "envvar_cast_failed"],
)
def test_from_environ_exceptions(
    envvar, required, cast, expected_exc, error_message, mock_envvar
):  # pylint: disable=redefined-outer-name,too-many-arguments,unused-argument
    with pytest.raises(expected_exc) as error:
        config.from_environ(envvar, required=required, cast=cast)

    assert str(error.value) == error_message
