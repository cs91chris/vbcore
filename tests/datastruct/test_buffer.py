from unittest.mock import MagicMock

from vbcore.datastruct import BufferManager
from vbcore.tester.asserter import Asserter


class MyBuffer(BufferManager[int]):
    def __init__(self):
        super().__init__()
        self.mock_hook = MagicMock()

    def pre_flush_hook(self) -> None:
        # using list because flush clears the buffer
        self.mock_hook(data=list(self._buffer))


def test_buffer_manager():
    sample = [1, 2, 3]
    buffer = MyBuffer()

    Asserter.assert_true(buffer.is_empty)

    buffer.loads(sample)
    Asserter.assert_false(buffer.is_full)
    Asserter.assert_false(buffer.is_empty)

    buffer.flush()
    Asserter.assert_true(buffer.is_empty)
    buffer.mock_hook.assert_called_once_with(data=sample)
