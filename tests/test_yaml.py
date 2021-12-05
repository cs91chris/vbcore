import os
from io import StringIO

from vbcore import yaml
from vbcore.datastruct import ObjectDict
from vbcore.misc import TempFile
from vbcore.tester.mixins import Asserter

YAML_DATA = """
envvar: ${NOT_FOUND:notfound}
test:
    hello: world
    user: ${USER}
opt_file: !opt_include nofile.nowhere
"""

EXPECTED = {
    "envvar": "notfound",
    "test": {
        "hello": "world",
        "user": os.environ["USER"],
    },
    "opt_file": {},
}


def test_yaml_loads():
    loaded = yaml.loads(StringIO(YAML_DATA))
    Asserter.assert_equals(loaded, ObjectDict(**EXPECTED))


def test_yaml_load_file():
    with TempFile(YAML_DATA.encode()) as file:
        loaded = yaml.load_yaml_file(file.name)
        Asserter.assert_equals(loaded, ObjectDict(**EXPECTED))
