import logging
from dataclasses import dataclass

from vbcore.context import ContextMetadata, ContextCorrelationId
from vbcore.loggers import SetupLoggers, Log, LogContextFilter


@dataclass(frozen=True, kw_only=True)
class ContextUserId(ContextMetadata):
    user_id: str


@dataclass(frozen=True, kw_only=True)
class Context(ContextCorrelationId, ContextUserId):
    pass


class CustomLogContextFilter(LogContextFilter):
    _metadata = Context


def prepare_context():
    return Context(
        user_id="user-id",
        correlation_id=Context.generate_correlation_id(),
    )


if __name__ == "__main__":
    logger = Log.get(__name__)
    handler = logging.StreamHandler()
    handler.addFilter(CustomLogContextFilter())

    SetupLoggers(
        level="DEBUG",
        handlers=[handler],
        format=(
            "%(asctime)s.%(msecs)03d | %(levelname)-8s | "
            "%(correlation_id)s | %(user_id)s | %(name)s | %(message)s"
        ),
    )

    with Log.execution_time(__name__):
        Context.set(prepare_context())

        Log.get().alert("root logger")
        logger.debug("sample debug message")
        logger.info("sample info message")
        logger.warning("sample warning message")
        logger.alert("sample alert message")
        logger.error("sample error message")
        logger.critical("sample critical message")
