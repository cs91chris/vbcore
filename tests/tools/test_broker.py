from unittest.mock import ANY, AsyncMock, patch

from vbcore.tester.asserter import Asserter
from vbcore.tools.entrypoint import main


@patch("vbcore.tools.broker.Publisher")
def test_publish(mock_publisher, runner):
    mock_instance = AsyncMock()
    mock_publisher.return_value = mock_instance

    result = runner.invoke(
        main,
        [
            "broker",
            "publish",
            "--broker",
            "DUMMY",
            "--server",
            "nats://localhost:4222",
            "--topic",
            "topic",
            "--message",
            "message",
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_publisher.assert_called_once_with(ANY)
    mock_instance.raw_publish.assert_called_once_with("topic", "message", ANY)


@patch("vbcore.tools.broker.Consumer")
def test_subscribe(mock_consumer, runner):
    mock_instance = AsyncMock()
    mock_consumer.return_value = mock_instance

    result = runner.invoke(
        main,
        [
            "broker",
            "subscribe",
            "--broker",
            "DUMMY",
            "--server",
            "nats://localhost:4222",
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_consumer.assert_called_once_with(ANY, callbacks=[])
    mock_instance.run.assert_called_once_with()
