import string

import pytest
from hypothesis import given, settings, strategies as st

from vbcore import crypto
from vbcore.crypto.hashes import BuiltinHash, HashOptions
from vbcore.factory import ClassLoader
from vbcore.tester.mixins import Asserter


class HashClassLoader(ClassLoader):
    BASE_CLASS = BuiltinHash
    PACKAGE = crypto


@given(st.text(string.printable), st.text())
@settings(max_examples=30)
@pytest.mark.parametrize("hash_class", HashClassLoader.load())
def test_hash_invalid(hash_class, fake_hash, fake_password):
    hasher = hash_class(HashOptions())
    Asserter.assert_false(hasher.verify(fake_hash, fake_password))


@given(st.text())
@settings(max_examples=10, deadline=None)
@pytest.mark.parametrize("hash_class", HashClassLoader.load())
def test_hash_ok_text(hash_class, password):
    hasher = hash_class(HashOptions())
    Asserter.assert_true(hasher.verify(hasher.hash(password), password))


@given(st.binary())
@settings(max_examples=10, deadline=None)
@pytest.mark.parametrize("hash_class", HashClassLoader.load())
def test_hash_ok_binary(hash_class, password):
    hasher = hash_class(HashOptions())
    Asserter.assert_true(hasher.verify(hasher.hash(password), password))
