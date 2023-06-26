import pytest
import responses

from vbcore.http import httpcode
from vbcore.http.client import HTTPClient
from vbcore.tester.asserter import Asserter


@pytest.mark.skip("implement me")
def test_token_auth_call():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_token_auth_equals():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_normalize_dump_flags():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_dump_body_flags():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_normalize_url():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_get_auth():
    """TODO implement me"""


@responses.activate
@pytest.mark.parametrize(
    "method, match_method",
    [
        ("get", responses.GET),
        ("post", responses.POST),
        ("put", responses.PUT),
        ("patch", responses.PATCH),
        ("delete", responses.DELETE),
        ("head", responses.HEAD),
        ("options", responses.OPTIONS),
    ],
)
def test_http_client_request(method, match_method):
    params = {"a": "1", "b": "1"}
    responses.add(
        match_method,
        match=(responses.matchers.query_param_matcher(params),),
        url="http://fake.endpoint/url",
        status=httpcode.BAD_REQUEST,
        json={},
        headers={"hdr": "value"},
    )
    client = HTTPClient(endpoint="http://fake.endpoint")
    client_method = getattr(client, method)
    response = client_method("/url", params=params)
    Asserter.assert_status_code(response, httpcode.BAD_REQUEST)
    Asserter.assert_equals(response.body, {})
    Asserter.assert_header(response, "hdr", "value")


@pytest.mark.skip("implement me")
def test_jsonrpc_request():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_jsonrpc_notification():
    """TODO implement me"""
