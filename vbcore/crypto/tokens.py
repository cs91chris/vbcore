from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Type, Union

import jwt

from vbcore.types import OptInt, OptStr

from .exceptions import VBMissingKey
from .keys import ECCKey, RSAKey, SecretKey

AudienceType = Optional[Union[List[str], str]]


class JwtHandler:
    def __init__(
        self,
        *,
        algorithm: str,
        encode_key: OptStr = None,
        decode_key: OptStr = None,
        issuer: OptStr = None,
        audience: AudienceType = None,
    ) -> None:
        self.issuer = issuer
        self.audience = audience
        self.algorithm = algorithm
        self._encode_key = encode_key
        self._decode_key = decode_key

    @property
    def encode_key(self) -> str:
        if not self._encode_key:
            raise VBMissingKey("encode_key")
        return self._encode_key

    @property
    def decode_key(self) -> str:
        if not self._decode_key:
            raise VBMissingKey("decode_key")
        return self._decode_key

    @classmethod
    def decode_error(cls, error: jwt.PyJWTError) -> str:
        decoder: Dict[Type[jwt.PyJWTError], str] = {
            jwt.ExpiredSignatureError: "Token expired",
            jwt.ImmatureSignatureError: "Invalid token immature signature",
            jwt.InvalidAlgorithmError: "Invalid token algorithm",
            jwt.InvalidAudienceError: "Invalid token audience",
            jwt.InvalidIssuedAtError: "Invalid token issued at",
            jwt.InvalidIssuerError: "Invalid token issuer",
            jwt.InvalidKeyError: "Invalid key format",
            jwt.MissingRequiredClaimError: "Invalid token claim",
            jwt.InvalidSignatureError: "Token signature validation failed",
            jwt.InvalidTokenError: "Invalid token format",
        }
        return decoder.get(error.__class__, "Token validation error")

    def encode(self, data: dict, *, expire_after: OptInt = None) -> str:
        payload = data.copy()
        payload["typ"] = "JWT"
        payload["iat"] = datetime.now(tz=timezone.utc)

        if expire_after:
            payload["exp"] = payload["iat"] + timedelta(seconds=expire_after)
        if self.issuer:
            payload["iss"] = self.issuer
        if self.audience:
            payload["aud"] = self.audience

        return jwt.encode(payload, self.encode_key, algorithm=self.algorithm)

    def decode(self, token: str, **kwargs: Any) -> dict:
        kwargs["verify_iat"] = True
        kwargs["verify_iss"] = bool(self.issuer)
        kwargs["verify_aud"] = bool(self.audience)

        return jwt.decode(
            token,
            self.decode_key,
            algorithms=[self.algorithm],
            audience=self.audience,
            issuer=self.issuer,
            options=kwargs,
        )


class JwtHMAC(JwtHandler):
    def __init__(self, secret_key: SecretKey, *, issuer: OptStr = None, audience: AudienceType):
        super().__init__(
            algorithm="HS256",
            encode_key=secret_key.value,
            decode_key=secret_key.value,
            issuer=issuer,
            audience=audience,
        )


class JwtRSA(JwtHandler):
    def __init__(self, key: RSAKey, *, issuer: OptStr = None, audience: AudienceType = None):
        super().__init__(
            algorithm="RS256",
            encode_key=key.private_key,
            decode_key=key.public_key,
            issuer=issuer,
            audience=audience,
        )


class JwtECDSA(JwtHandler):
    def __init__(self, key: ECCKey, *, issuer: OptStr = None, audience: AudienceType = None):
        super().__init__(
            algorithm="ES256",
            encode_key=key.private_key,
            decode_key=key.public_key,
            issuer=issuer,
            audience=audience,
        )
