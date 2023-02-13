import enum

from vbcore.base import BaseDTO
from vbcore.crypto.base import Crypto
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


class CryptoFactory(ItemFactory[CryptoEnum, Crypto]):
    products = CryptoEnum
