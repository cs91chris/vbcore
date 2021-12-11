import os

import pytest

from vbcore.configurator import load_dotenv, config
from vbcore.tester.mixins import Asserter

SAMPLE_ENVVAR = os.environ["USER"].lower()
TEST_ENV_BOOL = "TEST_ENV_BOOL"
os.environ[TEST_ENV_BOOL] = "1"


def test_load_dot_env():
    Asserter.assert_true(load_dotenv)


@pytest.mark.parametrize(
    "envvar, default, cast, expected",
    [
        ("USER", None, str, SAMPLE_ENVVAR),
        ("USER", None, lambda x: x.upper(), SAMPLE_ENVVAR.upper()),
        ("NOENV", "none", str, "none"),
        (TEST_ENV_BOOL, None, bool, True),
    ],
    ids=["envvar_exists", "cast_envvar", "no_envvar_use_default", "envvar_bool"],
)
def test_from_environ(envvar, default, cast, expected):
    Asserter.assert_equals(config.from_environ(envvar, default, cast), expected)
