import string

from hypothesis import given, settings, strategies as st

from vbcore.crypto.argon import Argon2Options
from vbcore.tester.mixins import Asserter


def test_options(argon2_instance):
    options = Argon2Options(
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        salt_len=16,
    )
    Asserter.assert_equals(argon2_instance.options, options)


@given(st.text(string.printable), st.text(string.printable))
@settings(max_examples=25, deadline=1000)
def test_argon2_invalid(argon2_instance, fake_hash, fake_password):
    hasher = argon2_instance
    Asserter.assert_false(hasher.verify(fake_hash, fake_password))


@given(st.text())
@settings(max_examples=25, deadline=1000)
def test_argon2_ok(argon2_instance, password):
    hasher = argon2_instance
    Asserter.assert_true(hasher.verify(hasher.hash(password), password))
