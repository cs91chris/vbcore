from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error, InvalidHash

from vbcore.crypto.base import Hasher


class Argon2(Hasher):
    def __init__(self, **kwargs):
        self._ph = PasswordHasher(**kwargs)

    def hash(self, data: str) -> str:
        return self._ph.hash(data)

    def verify(self, given_hash: str, data: str, exc: bool = False) -> bool:
        try:
            return self._ph.verify(given_hash, data)
        except (Argon2Error, InvalidHash):
            if exc is True:
                raise  # pragma: no cover
            return False
