import typing as t
from collections import deque

T = t.TypeVar("T")


class BufferManager(t.Generic[T]):
    def __init__(self, max_size: int = 0) -> None:
        self.max_size = max_size
        self._buffer: t.Deque[T] = deque(maxlen=max_size or None)

    @property
    def size(self) -> int:
        return len(self._buffer)

    @property
    def is_full(self) -> bool:
        return 0 < self.max_size <= self.size

    @property
    def is_empty(self) -> bool:
        return self.size == 0

    def pre_flush_hook(self) -> None:
        """Derived class can hook at flush time, so it can handle buffered data"""

    def clear(self) -> None:
        self._buffer.clear()

    def load(self, record: T) -> None:
        self._buffer.append(record)
        if self.is_full:
            self.flush()

    def loads(self, records: t.Iterable[T]) -> None:
        for record in records:
            self.load(record)

    def flush(self) -> None:
        if not self.is_empty:
            self.pre_flush_hook()
            self.clear()
