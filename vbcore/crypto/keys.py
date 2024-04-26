import abc
import hmac
from functools import cached_property
from pathlib import Path
from typing import Any, Generic, Optional, Protocol, TypeVar, Union

from Crypto import Random
from Crypto.PublicKey import ECC, RSA
from typing_extensions import Self

from vbcore.stringutils.misc import random_string_ascii
from vbcore.types import OptStr


class SupportsKeys(Protocol):
    def export_key(self, *_, **__) -> Union[str, bytes]: ...
    def public_key(self) -> Self: ...


K = TypeVar("K", bound=SupportsKeys)


class Key(abc.ABC, Generic[K]):
    """Base class for ascii keys and format PEM"""

    def __init__(self) -> None:
        self.encoding = "ascii"
        self.format = "PEM"
        self._key: Optional[K] = None

    @classmethod
    def random(cls, size: int) -> bytes:
        return Random.get_random_bytes(size)

    @classmethod
    def from_key(cls, secret_key: str) -> Self:
        instance = cls()
        instance._load_key(secret_key)
        return instance

    @classmethod
    def from_file(cls, filename: Union[Path, str], **kwargs) -> Self:
        with open(filename, **kwargs) as file:
            return cls.from_key(file.read())

    def dump_keys(self, *, path: Union[Path, str] = ".", prefix: OptStr = None) -> None:
        prefix = f"{prefix}-" if prefix else ""
        with (
            open(Path(path, f"{prefix}private.pem"), "w") as secret_file,
            open(Path(path, f"{prefix}public.pem"), "w") as public_file,
        ):
            secret_file.write(self.private_key)
            public_file.write(self.public_key)

    @cached_property
    def key(self) -> K:
        if not self._key:
            self._key = self._generate()
        return self._key

    @cached_property
    def private_key(self) -> str:
        key = self.key.export_key(format=self.format)
        return key if isinstance(key, str) else key.decode(self.encoding)

    @cached_property
    def public_key(self) -> str:
        key = self.key.public_key().export_key(format=self.format)
        return key if isinstance(key, str) else key.decode(self.encoding)

    @abc.abstractmethod
    def _load_key(self, private_key: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _generate(self) -> K:
        raise NotImplementedError


class RSAKey(Key[RSA.RsaKey]):
    def __init__(self, bits: int = 2048):
        super().__init__()
        self.bits = bits

    def _generate(self) -> RSA.RsaKey:
        return RSA.generate(self.bits, randfunc=self.random)

    def _load_key(self, private_key: str) -> None:
        self._key = RSA.import_key(private_key)
        self.bits = self._key.size_in_bits()


class ECCKey(Key[ECC.EccKey]):
    def __init__(self, curve: str = "P-521"):
        super().__init__()
        self.curve = curve

    def _generate(self) -> ECC.EccKey:
        return ECC.generate(curve=self.curve, randfunc=self.random)

    def _load_key(self, private_key: str) -> None:
        self._key = ECC.import_key(private_key)
        self.curve = self._key.curve


class SecretKey:
    def __init__(self, *, value: OptStr = None, size: int = 64):
        self.size = size
        self._value = value

    @cached_property
    def value(self) -> str:
        if not self._value:
            self._value = self.generate()
        return self._value

    def __str__(self) -> str:
        """ensure that the key is never displayed"""
        return "*" * 8

    def __eq__(self, other: Any) -> bool:
        """prevent timing analysis"""
        other_value = other.value if isinstance(other, SecretKey) else str(other)
        return hmac.compare_digest(self.value, other_value)

    def generate(self) -> str:
        return random_string_ascii(self.size)
