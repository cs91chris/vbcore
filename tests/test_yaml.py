import os
from io import StringIO

import pytest

from vbcore import yaml
from vbcore.datastruct import ObjectDict
from vbcore.misc import TempFile
from vbcore.tester.mixins import Asserter

USER_ENV = "USER_ENV"

YAML_DATA = """
envvar: ${NOT_FOUND:notfound}
test:
    hello: world
    user: ${user_env_key}
opt_file: !opt_include nofile.nowhere
""".replace(
    "user_env_key", USER_ENV
)

EXPECTED = {
    "envvar": "notfound",
    "test": {
        "hello": "world",
        "user": USER_ENV,
    },
    "opt_file": {},
}


@pytest.fixture(scope="function")
def mock_envvar(monkeypatch):
    monkeypatch.setitem(os.environ, USER_ENV, USER_ENV)


def test_yaml_loads(
    mock_envvar,
):  # pylint: disable=redefined-outer-name,unused-argument
    loaded = yaml.loads(StringIO(YAML_DATA))
    Asserter.assert_equals(loaded, ObjectDict(**EXPECTED))


def test_yaml_load_file(
    mock_envvar,
):  # pylint: disable=redefined-outer-name,unused-argument
    with TempFile(YAML_DATA.encode()) as file:
        loaded = yaml.load_yaml_file(file.name)
        Asserter.assert_equals(loaded, ObjectDict(**EXPECTED))
