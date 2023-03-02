import string

from hypothesis import given, settings, strategies as st

from vbcore.crypto.argon import Argon2Options
from vbcore.tester.asserter import Asserter


def test_options(argon2_instance):
    options = Argon2Options(
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        salt_len=16,
    )
    Asserter.assert_equals(argon2_instance.options, options)


@given(st.text(string.printable), st.text())
@settings(max_examples=10)
def test_argon2_invalid(argon2_instance, fake_hash, fake_password):
    hasher = argon2_instance
    Asserter.assert_false(hasher.verify(fake_hash, fake_password))


@given(st.text())
@settings(max_examples=10, deadline=None)
def test_argon2_ok_text(argon2_instance, password):
    hasher = argon2_instance
    Asserter.assert_true(hasher.verify(hasher.hash(password), password))


@given(st.binary())
@settings(max_examples=10, deadline=None)
def test_argon2_ok_binary(argon2_instance, password):
    hasher = argon2_instance
    Asserter.assert_true(hasher.verify(hasher.hash(password), password))
