import pytest
import responses

from vbcore.datastruct import ObjectDict

from vbcore.http import httpcode, useragent
from vbcore.http.client import HTTPClient
from vbcore.tester.mixins import Asserter


def test_http_status():
    Asserter.assert_true(httpcode.is_informational(httpcode.PROCESSING))
    Asserter.assert_true(httpcode.is_success(httpcode.CREATED))
    Asserter.assert_false(httpcode.is_success(httpcode.MULTIPLE_CHOICES))
    Asserter.assert_true(httpcode.is_redirection(httpcode.SEE_OTHER))
    Asserter.assert_false(httpcode.is_redirection(httpcode.BAD_REQUEST))
    Asserter.assert_true(httpcode.is_client_error(httpcode.UNAUTHORIZED))
    Asserter.assert_false(httpcode.is_client_error(httpcode.INTERNAL_SERVER_ERROR))
    Asserter.assert_true(httpcode.is_server_error(httpcode.NOT_IMPLEMENTED))
    Asserter.assert_false(httpcode.is_server_error(httpcode.NOT_MODIFIED))
    Asserter.assert_true(httpcode.is_ok(httpcode.FOUND))
    Asserter.assert_false(httpcode.is_ko(httpcode.SUCCESS))
    Asserter.assert_status_code(
        ObjectDict(status=201), code=(201, 202, 203), is_in=True
    )
    Asserter.assert_status_code(ObjectDict(status=201), code=(200, 299), in_range=True)
    Asserter.assert_status_code(ObjectDict(status=400), code=300, greater=True)
    Asserter.assert_status_code(ObjectDict(status=200), code=300, less=True)


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
def test_http_client(method, match_method):
    responses.add(
        match_method,
        match_querystring=True,
        url="http://fake.endpoint/url?a=1&b=1",
        status=httpcode.BAD_REQUEST,
        json={},
        headers={"hdr": "value"},
    )
    client = HTTPClient(endpoint="http://fake.endpoint")
    client_method = getattr(client, method)
    response = client_method("/url", params={"a": 1, "b": 1})
    Asserter.assert_status_code(response, httpcode.BAD_REQUEST)
    Asserter.assert_equals(response.body, {})
    Asserter.assert_header(response, "hdr", "value")


def test_user_agent_parser():
    ua_string = """
        Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
        Chrome/70.0.3538.77 Safari/537.36
    """
    res = useragent.UserAgentParser().parse(ua_string)
    Asserter.assert_equals(res.raw, ua_string)
    Asserter.assert_equals(res.browser.family, "Chrome")
    Asserter.assert_equals(res.browser.version.string, "70.0.3538")
    Asserter.assert_equals(res.os.family, "Windows")
    Asserter.assert_equals(res.os.version.string, "10")
    Asserter.assert_true(res.device.type.pc)
    Asserter.assert_false(res.device.type.mobile)
