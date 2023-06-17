import json
import time
from unittest import TestCase

from vbcore.files import TempFile
from vbcore.loggers import Log, LoggingSettings, SetupLoggers

LOGGER_NAME = "vbcore"

log_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {},
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "filters": [],
        },
    },
    "loggers": {
        LOGGER_NAME: {
            "handlers": [
                "default",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


class TestLoggers(TestCase):
    def test_execution_time(self):
        file_config_data = json.dumps(log_config).encode()
        with TempFile(file_config_data) as file:
            SetupLoggers(LoggingSettings(config_file=file.name, level="INFO"))
            with self.assertLogs(LOGGER_NAME, "INFO") as captured:
                with Log.execution_time(LOGGER_NAME, "TIME: "):
                    time.sleep(0.01)

        self.assertEqual(len(captured.records), 1)
        self.assertTrue(captured.records[0].message.startswith("TIME: 0:00:00.01"))

    def test_reload(self):
        loggers = SetupLoggers(LoggingSettings(listen_for_reload=True))
        file_config_data = json.dumps(log_config).encode()

        with TempFile(file_config_data) as file:
            attempts = 0
            while True:
                try:
                    loggers.reload(file.name)
                    break
                except ConnectionRefusedError:
                    if attempts >= 3:
                        raise
                    attempts += 1
                    time.sleep(1)

        with self.assertLogs(LOGGER_NAME, "DEBUG") as captured:
            Log.get(LOGGER_NAME).debug("TEST")

        self.assertEqual(len(captured.records), 1)
