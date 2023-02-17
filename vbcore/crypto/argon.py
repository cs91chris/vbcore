from dataclasses import dataclass, field
from functools import cached_property

import argon2
from argon2.exceptions import Argon2Error, InvalidHash

from vbcore.crypto.base import HashableType, Hasher, HashOptions
from vbcore.crypto.exceptions import VBInvalidHashError


@dataclass(frozen=True)
class Argon2Options(HashOptions):
    time_cost: int = field(default=argon2.DEFAULT_TIME_COST)
    memory_cost: int = field(default=argon2.DEFAULT_MEMORY_COST)
    parallelism: int = field(default=argon2.DEFAULT_PARALLELISM)
    hash_len: int = field(default=argon2.DEFAULT_HASH_LENGTH)
    salt_len: int = field(default=argon2.DEFAULT_RANDOM_SALT_LENGTH)


class Argon2(Hasher[Argon2Options]):
    @cached_property
    def hasher(self) -> argon2.PasswordHasher:
        return argon2.PasswordHasher(**self.options.to_dict())

    def hash(self, data: HashableType) -> str:
        return self.hasher.hash(data)

    def verify(
        self, given_hash: str, data: HashableType, raise_exc: bool = False
    ) -> bool:
        try:
            return self.hasher.verify(given_hash, data)
        except (Argon2Error, InvalidHash) as exc:
            if raise_exc is True:
                raise VBInvalidHashError(given_hash, orig=exc) from exc
            return False
