import abc


class Hasher(abc.ABC):
    @abc.abstractmethod
    def hash(self, data: str) -> str:
        pass

    @abc.abstractmethod
    def verify(self, given_hash: str, data: str, exc: bool = False) -> bool:
        pass
