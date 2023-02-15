import hashlib
import typing as t
from dataclasses import dataclass, field
from functools import cached_property

from vbcore.base import BaseDTO
from vbcore.crypto.base import Crypto
from vbcore.crypto.exceptions import VBInvalidHashError


@dataclass(frozen=True)
class HashOptions(BaseDTO):
    encoding: str = field(default="utf-8")


class Hash(Crypto[HashOptions]):
    ALGO: t.ClassVar[str]

    @cached_property
    def instance(self):
        return hashlib.new(self.ALGO)

    def hash(self, data: str) -> str:
        self.instance.update(data.encode())
        return self.instance.hexdigest()

    def verify(self, given_hash: str, data: str, raise_exc: bool = False) -> bool:
        if given_hash == self.hash(data):
            return True

        if raise_exc:
            raise VBInvalidHashError(given_hash)

        return False


class MD5(Hash):
    ALGO = "md5"


class SHA1(Hash):
    ALGO = "sha1"


class SHA256(Hash):
    ALGO = "sha256"


class SHA512(Hash):
    ALGO = "sha512"


# pylint: disable=invalid-name
# noinspection PyPep8Naming
class SHA3_256(Hash):
    ALGO = "sha3_256"


# pylint: disable=invalid-name
# noinspection PyPep8Naming
class SHA3_512(Hash):
    ALGO = "sha3_512"


class BLAKE2B(Hash):
    ALGO = "blake2b"


class BLAKE2S(Hash):
    ALGO = "blake2s"
