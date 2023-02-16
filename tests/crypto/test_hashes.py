import string

import pytest
from hypothesis import given, settings, strategies as st

from vbcore import crypto
from vbcore.crypto.hashes import Hash, HashOptions
from vbcore.factory import ClassLoader
from vbcore.tester.mixins import Asserter


class HashClassLoader(ClassLoader):
    BASE_CLASS = Hash
    PACKAGE = crypto


@given(st.text(string.printable), st.text(string.printable))
@settings(max_examples=25, deadline=1000)
@pytest.mark.parametrize("hash_class", HashClassLoader.load())
def test_hash_invalid(hash_class, fake_hash, fake_password):
    hasher = hash_class(HashOptions())
    Asserter.assert_false(hasher.verify(fake_hash, fake_password))


@given(st.text())
@settings(max_examples=25, deadline=1000)
@pytest.mark.parametrize("hash_class", HashClassLoader.load())
def test_hash_ok(hash_class, password):
    hasher = hash_class(HashOptions())
    Asserter.assert_true(hasher.verify(hasher.hash(password), password))
