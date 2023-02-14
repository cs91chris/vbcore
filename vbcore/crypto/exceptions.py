from vbcore.exceptions import VBException


class VBCryptoError(VBException):
    pass


class VBInvalidHashError(VBCryptoError):
    def __init__(self, hashed: str, *args, **kwargs) -> None:
        super().__init__("invalid hash error", *args, **kwargs)
        self.hashed = hashed
