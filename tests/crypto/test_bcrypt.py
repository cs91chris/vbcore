import string

from hypothesis import given, settings, strategies as st

from vbcore.crypto.bcrypt import BcryptOptions
from vbcore.tester.mixins import Asserter


def test_options(bcrypt_instance):
    options = BcryptOptions(rounds=12, encoding="utf-8")
    Asserter.assert_equals(bcrypt_instance.options, options)


@given(st.text(string.printable), st.text(string.printable))
@settings(max_examples=25, deadline=1000)
def test_bcrypt_invalid(bcrypt_instance, fake_hash, fake_password):
    hasher = bcrypt_instance
    Asserter.assert_false(hasher.verify(fake_hash, fake_password))


@given(st.text())
@settings(max_examples=25, deadline=1000)
def test_bcrypt_ok(bcrypt_instance, password):
    hasher = bcrypt_instance
    Asserter.assert_true(hasher.verify(hasher.hash(password), password))
