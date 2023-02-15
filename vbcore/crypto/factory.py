import enum

from vbcore.base import BaseDTO
from vbcore.crypto import hashes
from vbcore.crypto.base import Crypto
from vbcore.crypto.bcrypt import Bcrypt, BcryptOptions
from vbcore.datastruct.lazy import LazyException
from vbcore.factory import ItemEnumMeta, ItemEnumMixin, ItemFactory

# TODO test me
try:
    from vbcore.crypto.argon import Argon2, Argon2Options
except ImportError:
    Error = ImportError("you must install argon2")
    Argon2 = Argon2Options = LazyException(Error)  # type: ignore


class CryptoEnum(
    ItemEnumMixin[BaseDTO],
    enum.Enum,
    metaclass=ItemEnumMeta,
):
    ARGON2 = Argon2, Argon2Options
    BCRYPT = Bcrypt, BcryptOptions
    MD5 = hashes.MD5, hashes.HashOptions
    SHA1 = hashes.SHA1, hashes.HashOptions
    SHA256 = hashes.SHA256, hashes.HashOptions
    SHA512 = hashes.SHA512, hashes.HashOptions
    SHA3_256 = hashes.SHA3_256, hashes.HashOptions
    SHA3_512 = hashes.SHA3_512, hashes.HashOptions
    BLAKE2B = hashes.BLAKE2B, hashes.HashOptions
    BLAKE2S = hashes.BLAKE2S, hashes.HashOptions


class CryptoFactory(ItemFactory[CryptoEnum, Crypto]):
    products = CryptoEnum
