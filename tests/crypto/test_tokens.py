from unittest.mock import ANY

import pytest

from vbcore.crypto.keys import ECCKey, RSAKey, SecretKey
from vbcore.crypto.tokens import JwtECDSA, JwtHandler, JwtHMAC, JwtRSA

sample_issuer = "issuer"
sample_audience = ["aud-1", "aud-2"]


@pytest.mark.parametrize(
    "token_handler",
    [
        JwtRSA(
            RSAKey(),
            issuer=sample_issuer,
            audience=sample_audience,
        ),
        JwtHMAC(
            SecretKey(),
            issuer=sample_issuer,
            audience=sample_audience,
        ),
        JwtECDSA(
            ECCKey(),
            issuer=sample_issuer,
            audience=sample_audience,
        ),
    ],
    ids=[
        "RSA",
        "HMAC",
        "ECDSA",
    ],
)
def test_encoder_decoder(token_handler: JwtHandler) -> None:
    expected = token_handler.decode(token_handler.encode({"sub": "user-id"}, expire_after=5))
    assert expected == {
        "aud": sample_audience,
        "exp": ANY,
        "iat": ANY,
        "iss": sample_issuer,
        "typ": "JWT",
        "sub": "user-id",
    }


def test_encoder_with_audience() -> None:
    key = RSAKey()
    encoder = JwtRSA(key, issuer=sample_issuer, audience="some-audience")
    decoder = JwtRSA(key, issuer=sample_issuer, audience=None)

    expected = decoder.decode(encoder.encode({"sub": "user-id"}, expire_after=5))
    assert expected == {
        "aud": "some-audience",
        "exp": ANY,
        "iat": ANY,
        "iss": sample_issuer,
        "typ": "JWT",
        "sub": "user-id",
    }
