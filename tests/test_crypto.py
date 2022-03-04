import string

from hypothesis import given, strategies as st, settings

from vbcore.crypto.argon import Argon2
from vbcore.tester.mixins import Asserter


@given(st.text(string.printable), st.text(string.printable))
def test_argon2_invalid(fake_hash, fake_password):
    hasher = Argon2()
    Asserter.assert_false(hasher.verify(fake_hash, fake_password))


@given(st.text())
@settings(max_examples=20, deadline=500)
def test_argon2_ok(password):
    hasher = Argon2()
    Asserter.assert_true(hasher.verify(hasher.hash(password), password))
