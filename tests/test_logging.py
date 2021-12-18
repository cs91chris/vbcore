import json
import tempfile
import time
from unittest import TestCase

from vbcore.logging import Loggers, LoggingSettings

LOGGER_NAME = "performance"

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
        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(json.dumps(log_config).encode())

        loggers = Loggers(LoggingSettings(config_file=file.name))
        with self.assertLogs(LOGGER_NAME, "INFO") as captured:
            with loggers.execution_time("TIME: %.3fs"):
                time.sleep(0.01)

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].message, "TIME: 0.010s")

    def test_reload(self):
        loggers = Loggers(LoggingSettings(listen_for_reload=True))

        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(json.dumps(log_config).encode())

        loggers.reload(file.name)

        with self.assertLogs(LOGGER_NAME, "DEBUG") as captured:
            loggers(LOGGER_NAME).debug("TEST")

        self.assertEqual(len(captured.records), 1)
