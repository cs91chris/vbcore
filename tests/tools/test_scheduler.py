from unittest.mock import MagicMock, patch

from vbcore import json
from vbcore.tester.asserter import Asserter
from vbcore.tools.entrypoint import main


@patch("vbcore.tools.scheduler.APScheduler")
def test_scheduler_standalone(mock_scheduler, runner, tmpdir):
    config_data = {
        "LOGGING": {
            "version": 1,
            "disable_existing_loggers": False,
            "loggers": {"": {"level": "INFO"}},
        },
        "SCHEDULER": {},
        "JOBS": [],
    }
    config_file = tmpdir.join("config.yaml")
    config_path = f"{config_file.dirname}/{config_file.basename}"
    config_file.write(json.dumps(config_data))

    mock_instance = MagicMock()
    mock_scheduler.factory.return_value = mock_instance

    result = runner.invoke(main, ["scheduler", "standalone", "-c", config_path])

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_scheduler.factory.assert_called_once_with(config_data)
    mock_instance.scheduler.start.assert_called_once_with()
