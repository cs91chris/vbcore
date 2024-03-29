import pytest
from hypothesis import given, settings
from hypothesis.provisional import urls

from vbcore.net.helpers import Url
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "query, expected",
    [
        ("a=1", {"a": "1"}),
        ("a=1&b=1", {"a": "1", "b": "1"}),
        ("a=&b", {"a": None, "b": None}),
        ("a=1&a=2&b", {"a": ["1", "2"], "b": None}),
    ],
    ids=[
        "one-param",
        "two-params",
        "empty-params",
        "multi-params",
    ],
)
def test_parse_query_string(query, expected):
    Asserter.assert_equals(Url.parse_query(query), expected)


def test_url_encoder_decoder():
    url = "http://user:pass@example.com/path?a=1&b=2&a=3#fragment"
    expected = Url(
        protocol="http",
        hostname="example.com",
        username="user",
        password="pass",
        path="/path",
        fragment="fragment",
        query="a=1&b=2&a=3",
        params={"a": ["1", "3"], "b": "2"},
    )
    decoded = Url.from_raw(url)
    Asserter.assert_equals(decoded, expected)
    Asserter.assert_equals(url, decoded.encode())


def test_url_encoder_decoder_file():
    url = "file:///home/data/file.txt"
    expected = Url(protocol="file", path="/home/data/file.txt")
    decoded = Url.from_raw(url)
    Asserter.assert_equals(decoded, expected)
    Asserter.assert_equals(url, decoded.encode())


@pytest.mark.parametrize(
    "url",
    [
        "/home/data/file.txt",
        "file.txt",
        "file",
    ],
)
def test_url_encoder_decoder_file_simple(url):
    decoded = Url.from_raw(url)
    Asserter.assert_equals(decoded, Url(path=url))
    Asserter.assert_equals(url, decoded.encode())


@given(urls())
@settings(max_examples=30)
def test_url_parse(url):
    _url = url.lower()
    decoded = Url.from_raw(_url)
    Asserter.assert_equals(_url, decoded.encode())
