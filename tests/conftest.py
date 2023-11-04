from vbcore.loggers import LoggingSettings, SetupLoggers


def pytest_configure() -> None:
    SetupLoggers(LoggingSettings(level="DEBUG"))
