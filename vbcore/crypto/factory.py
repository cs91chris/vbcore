import enum

from vbcore.base import BaseDTO
from vbcore.crypto import hashes
from vbcore.crypto.base import Hasher
from vbcore.datastruct.lazy import LazyImporter
from vbcore.factory import ItemEnumMeta, ItemEnumMixin, ItemFactory

Argon2, Argon2Options = LazyImporter.import_many(
    "vbcore.crypto.argon:Argon2",
    "vbcore.crypto.argon:Argon2Options",
    message="you must install 'argon2'",
)

Bcrypt, BcryptOptions = LazyImporter.import_many(
    "vbcore.crypto.bcrypt:Bcrypt",
    "vbcore.crypto.bcrypt:BcryptOptions",
    message="you must install 'bcrypt'",
)


class HasherEnum(
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


class CryptoFactory(ItemFactory[HasherEnum, Hasher]):
    items = HasherEnum
