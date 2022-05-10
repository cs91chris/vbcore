import os
from unittest.mock import patch

from click.testing import CliRunner

from vbcore.tester.mixins import Asserter
from vbcore.tools.entrypoint import main
from vbcore.tools.initializer.init import init_app


@patch("vbcore.tools.initializer.init.init_app")
def test_init_app_entrypoint(mock_init_app):
    _ = mock_init_app

    runner = CliRunner()
    result = runner.invoke(main, ["init", "testapp"])

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)


def test_init_app(tmpdir):
    home = tmpdir.strpath
    new_app_name = "testapp"
    new_package = os.path.join(home, new_app_name)

    os.chdir(home)
    init_app(new_app_name)

    for base_dir, directory in ((home, new_app_name),):
        Asserter.assert_true(os.path.isdir(os.path.join(base_dir, directory)))

    for base_dir, file in (
        (new_package, "__init__.py"),
        (new_package, "version.py"),
    ):
        Asserter.assert_true(os.path.isfile(os.path.join(base_dir, file)))
