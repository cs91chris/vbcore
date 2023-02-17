from dataclasses import dataclass, field

import bcrypt

from vbcore.crypto.base import HashableType, Hasher, HashOptions
from vbcore.crypto.exceptions import VBInvalidHashError


@dataclass(frozen=True)
class BcryptOptions(HashOptions):
    rounds: int = field(default=12)


class Bcrypt(Hasher[BcryptOptions]):
    def salt(self) -> bytes:
        return bcrypt.gensalt(rounds=self.options.rounds)

    def prepare_data(self, data: HashableType) -> bytes:
        return self.to_bytes(data) if isinstance(data, str) else data

    def hash(self, data: HashableType) -> str:
        hashed = bcrypt.hashpw(self.prepare_data(data), self.salt())
        return self.to_string(hashed)

    def verify(
        self, given_hash: str, data: HashableType, raise_exc: bool = False
    ) -> bool:
        try:
            return bcrypt.checkpw(
                self.prepare_data(data),
                self.to_bytes(given_hash),
            )
        except ValueError as exc:
            if raise_exc:
                raise VBInvalidHashError(given_hash, orig=exc) from exc
            return False
