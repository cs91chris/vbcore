import hashlib
import hmac
import typing as t

from vbcore.crypto.base import HashableType, Hasher, HashOptions
from vbcore.crypto.exceptions import VBInvalidHashError


class BuiltinHash(Hasher[HashOptions]):
    ALGO: t.ClassVar[str]

    def hash(self, data: HashableType) -> str:
        data = self.to_bytes(data) if isinstance(data, str) else data
        return hashlib.new(self.ALGO, data=data).hexdigest()

    def verify(
        self, given_hash: str, data: HashableType, raise_exc: bool = False
    ) -> bool:
        if hmac.compare_digest(given_hash, self.hash(data)):
            return True

        if raise_exc:
            raise VBInvalidHashError(given_hash)

        return False


class MD5(BuiltinHash):
    ALGO = "md5"


class SHA1(BuiltinHash):
    ALGO = "sha1"


class SHA256(BuiltinHash):
    ALGO = "sha256"


class SHA512(BuiltinHash):
    ALGO = "sha512"


# pylint: disable=invalid-name
# noinspection PyPep8Naming
class SHA3_256(BuiltinHash):
    ALGO = "sha3_256"


# pylint: disable=invalid-name
# noinspection PyPep8Naming
class SHA3_512(BuiltinHash):
    ALGO = "sha3_512"


class BLAKE2B(BuiltinHash):
    ALGO = "blake2b"


class BLAKE2S(BuiltinHash):
    ALGO = "blake2s"
