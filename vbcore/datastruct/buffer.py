import typing as t

T = t.TypeVar("T")


class BufferManager(t.Generic[T]):
    def __init__(self, max_size: int = 0) -> None:
        self._max_size = max_size
        self._buffer: t.List[T] = []

    @property
    def buffer(self) -> t.List[T]:
        return self._buffer

    @property
    def size(self) -> int:
        return len(self.buffer)

    @property
    def is_full(self) -> bool:
        return 0 < self._max_size <= self.size

    @property
    def is_empty(self) -> bool:
        return self.size == 0

    def pre_flush_hook(self) -> None:
        """Derived class can hook at flush time, so it can handle buffered data"""

    def clear(self) -> None:
        self.buffer.clear()

    def load(self, record: T) -> int:
        self._buffer.append(record)
        if self.is_full:
            self.flush()
        return self.size

    def loads(self, records: t.Iterable[T]) -> int:
        for record in records:
            self.load(record)
        return self.size

    def flush(self) -> None:
        if not self.is_empty:
            self.pre_flush_hook()
            self.clear()
