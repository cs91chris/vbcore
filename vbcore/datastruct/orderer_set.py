import itertools
import typing as t

T = t.TypeVar("T")


class OrderedSet(t.MutableSet[T]):
    __slots__ = ("_data",)

    def __init__(self, iterable: t.Optional[t.Iterable[T]] = None):
        self._data = dict.fromkeys(iterable) if iterable else {}

    def add(self, value: T) -> None:
        self._data[value] = None

    def clear(self) -> None:
        self._data.clear()

    def discard(self, value: T) -> None:
        self._data.pop(value, None)

    def remove(self, value: T) -> None:
        self._data.pop(value)

    def __getitem__(self, index) -> T:
        try:
            return next(itertools.islice(self._data, index, index + 1))
        except StopIteration as exc:
            raise IndexError(f"index {index} out of range") from exc

    def __contains__(self, x: object) -> bool:
        return self._data.__contains__(x)

    def __len__(self) -> int:
        return self._data.__len__()

    def __iter__(self) -> t.Iterator[T]:
        return self._data.__iter__()

    def __str__(self):
        return f"{{{', '.join(str(i) for i in self)}}}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self}>"
