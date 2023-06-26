from unittest.mock import call, MagicMock, patch

import pytest

from vbcore.batch import BatchSize, PCTask, ProducerConsumerBatchExecutor
from vbcore.tester.asserter import Asserter


class FakeTask(PCTask):
    def perform(self, item):
        return item


@pytest.mark.skip("implement me")
def test_batch_executor():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_async_batch_executor():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_thread_batch_executor():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_linear_executor():
    """TODO implement me"""


@patch("vbcore.batch.Thread")
def test_producer_consumer_batch_executor_startup(mock_thread):
    workers = 4
    executor = ProducerConsumerBatchExecutor(
        producer=FakeTask(),
        consumer=FakeTask(),
        batch_size=BatchSize(pool_workers=workers),
        thread_class=mock_thread,
    )
    executor.startup()

    mock_thread.return_value.start.assert_called()
    assert mock_thread.return_value.start.call_count == workers + 1


def test_producer_consumer_batch_load():
    producer_task = MagicMock()
    consumer_task = MagicMock()
    # pylint: disable=unnecessary-lambda
    producer_task.perform.side_effect = lambda x: str(x)

    executor = ProducerConsumerBatchExecutor(
        producer=producer_task,
        consumer=consumer_task,
        batch_size=BatchSize(),
    )

    executor.run_on((1, 2, 3))

    Asserter.assert_equals(producer_task.perform.call_count, 3)
    Asserter.assert_equals(consumer_task.perform.call_count, 3)
    producer_task.perform.assert_has_calls((call(1), call(2), call(3)))
    consumer_task.perform.assert_has_calls((call("1"), call("2"), call("3")))
