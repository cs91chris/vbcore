from dataclasses import dataclass, field

import bcrypt

from vbcore.base import BaseDTO
from vbcore.crypto.base import Crypto
from vbcore.crypto.exceptions import VBInvalidHashError


@dataclass(frozen=True)
class BcryptOptions(BaseDTO):
    rounds: int = field(default=12)
    encoding: str = field(default="utf-8")


class Bcrypt(Crypto[BcryptOptions]):
    def to_bytes(self, data: str) -> bytes:
        return data.encode(encoding=self.options.encoding)

    def to_string(self, data: bytes) -> str:
        return data.decode(encoding=self.options.encoding)

    def salt(self) -> bytes:
        return bcrypt.gensalt(rounds=self.options.rounds)

    def hash(self, data: str) -> str:
        hashed = bcrypt.hashpw(self.to_bytes(data), self.salt())
        return self.to_string(hashed)

    def verify(self, given_hash: str, data: str, raise_exc: bool = False) -> bool:
        try:
            return bcrypt.checkpw(
                self.to_bytes(data),
                self.to_bytes(given_hash),
            )
        except ValueError as exc:
            if raise_exc:
                raise VBInvalidHashError(given_hash, orig=exc) from exc
            return False
