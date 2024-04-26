from pathlib import Path

import pytest

from vbcore.crypto.keys import ECCKey, Key, RSAKey, SecretKey
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "key",
    [
        RSAKey(),
        ECCKey(),
    ],
    ids=[
        "RSA",
        "ECC",
    ],
)
def test_dump_load(key: Key, tmp_path: Path) -> None:
    key.dump_keys(path=tmp_path)
    new_key = key.from_file(Path(tmp_path, "private.pem"))
    Asserter.assert_equals(key.public_key, new_key.public_key)
    Asserter.assert_equals(key.private_key, new_key.private_key)


def test_secret_key_compare() -> None:
    sample_key = "some-strong-key"
    key = SecretKey(value=sample_key)
    Asserter.assert_equals(key, sample_key)
