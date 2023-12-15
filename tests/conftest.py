from vbcore.loggers import LogContextFilter, LoggingSettings, SetupLoggers


def pytest_configure() -> None:
    SetupLoggers(
        LoggingSettings(level="DEBUG"),
        context_filter=LogContextFilter(),
    )
