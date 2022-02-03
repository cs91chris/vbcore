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


@pytest.mark.parametrize(
    "device_type, operating_system, browser, user_agent",
    # fmt: off
    [
        ("tablet", "Android", "Android", "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; BroadSign Xpress 1.0.15-6 B- (720) Build/JRO03H) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"),  # noqa: E501 pylint: disable=line-too-long
        ("mobile", "Android", "Chrome Mobile", "Mozilla/5.0 (Linux; Android 6.0.1; SM-G532G Build/MMB29T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.83 Mobile Safari/537.36"),  # noqa: E501 pylint: disable=line-too-long
        ("mobile", "Android", "Chrome Mobile WebView", "Mozilla/5.0 (Linux; Android 4.4.2; XMP-6250 Build/HAWK) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Safari/537.36 ADAPI/2.0 RK3188-ADAPI/1.2.84.533 (MODEL:XMP-6250)"),  # noqa: E501 pylint: disable=line-too-long
        ("mobile", "Android", "Android", "Mozilla/5.0 (Linux; U; Android 2.2; en-us; SCH-I800 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1 DMBrowser-BV"),  # noqa: E501 pylint: disable=line-too-long
        ("mobile", "iOS", "Mobile Safari", "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"),  # noqa: E501 pylint: disable=line-too-long
        ("tablet", "iOS", "Mobile Safari", "Mozilla/5.0 (iPad; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G36 Safari/601.1"),  # noqa: E501 pylint: disable=line-too-long
        ("computer", "Linux", "Chrome", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"),  # noqa: E501 pylint: disable=line-too-long
        ("computer", "Linux", "Chromium", "Mozilla/5.0 (SMART-TV; X11; Linux armv7l) AppleWebKit/537.42 (KHTML, like Gecko) Chromium/25.0.1349.2 Chrome/25.0.1349.2 Safari/537.42"),  # noqa: E501 pylint: disable=line-too-long
        ("computer", "Ubuntu", "Firefox", "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0"),  # noqa: E501 pylint: disable=line-too-long
        (None, "Tizen", "Chrome", "Mozilla/5.0 (SMART-TV; Linux; Tizen 4.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.0 Safari/537.36"),  # noqa: E501 pylint: disable=line-too-long
        ("computer", "Windows", "Chrome", "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"),  # noqa: E501 pylint: disable=line-too-long
        ("computer", "Windows", "IE", "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko MVisionPlayer/5.6.44.0"),  # noqa: E501 pylint: disable=line-too-long
        ("computer", "Windows", "Firefox", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"),  # noqa: E501 pylint: disable=line-too-long
        ("computer", "Mac OS X", "Safari", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8"),  # noqa: E501 pylint: disable=line-too-long
        ("computer", "Mac OS X", "Chrome", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"),  # noqa: E501 pylint: disable=line-too-long
        ("computer", "Mac OS X", "Firefox", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0"),  # noqa: E501 pylint: disable=line-too-long
        ("bot", "Linux", "JobboerseBot", "Mozilla/5.0 (X11; U; Linux Core i7-4980HQ; de; rv:32.0; compatible; JobboerseBot; http://www.jobboerse.com/bot.htm) Gecko/20100101 Firefox/38.0"),  # noqa: E501 pylint: disable=line-too-long
        ("bot", "Android", "Googlebot", "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"),  # noqa: E501 pylint: disable=line-too-long
        ("bot", "Other", "SeobilityBot", "SeobilityBot (SEO Tool; https://www.seobility.net/sites/bot.html)"),  # noqa: E501 pylint: disable=line-too-long
        (None, "Other", "Other", "apache-httpclient/4.5.5 (java/12.0.1)"),  # noqa: E501 pylint: disable=line-too-long
    ],
    # fmt: on
    ids=lambda x: x if (x and len(x) < 20) else ("None" if not x else ""),
)
def test_user_agent_parser(device_type, operating_system, browser, user_agent):
    res = useragent.UserAgent.parse(user_agent)
    Asserter.assert_equals(res.raw, user_agent)
    Asserter.assert_equals(res.operating_system.family, operating_system)
    Asserter.assert_equals(res.browser.family, browser)
    if device_type:
        Asserter.assert_true(getattr(res.device.type, device_type))
