from unittest.mock import patch

from vbcore.tester.asserter import Asserter
from vbcore.tools.entrypoint import main


@patch("vbcore.tools.initializer.init.init_app")
def test_init(mock_init_app, runner):
    result = runner.invoke(main, ["init", "newapp"])

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_init_app.assert_called_once_with("newapp")
