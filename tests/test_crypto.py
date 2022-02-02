from vbcore.crypto.argon import Argon2
from vbcore.tester.mixins import Asserter


def test_argon2():
    hasher = Argon2()
    fake_password = "password"
    Asserter.assert_false(hasher.verify("fake-hash", fake_password))
    Asserter.assert_true(hasher.verify(hasher.hash(fake_password), fake_password))
