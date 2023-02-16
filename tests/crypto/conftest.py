import pytest

from vbcore.crypto import CryptoFactory


@pytest.fixture(scope="session")
def argon2_instance():
    return CryptoFactory.instance("ARGON2")


@pytest.fixture(scope="session")
def bcrypt_instance():
    return CryptoFactory.instance("BCRYPT")
