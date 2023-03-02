from vbcore.datastruct import ObjectDict
from vbcore.http import httpcode, HttpMethod
from vbcore.http.batch import HTTPBatch
from vbcore.tester.asserter import Asserter

HOSTS = ObjectDict(
    apitester="http://httpbin.org",
    fake="http://localhost",
)


def test_http_client_batch():
    client = HTTPBatch(dump_body=(True, False))
    responses = client.request(
        [
            dict(
                url=f"{HOSTS.apitester}/anything",
                method=HttpMethod.GET,
                headers={"HDR1": "HDR1"},
            ),
            dict(
                url=f"{HOSTS.apitester}/status/{httpcode.NOT_FOUND}",
                method=HttpMethod.GET,
            ),
            dict(url=HOSTS.fake, method=HttpMethod.GET, timeout=0.1),
        ]
    )
    Asserter.assert_equals(responses[0].body.headers.Hdr1, "HDR1")
    Asserter.assert_equals(responses[1].status, httpcode.NOT_FOUND)
    Asserter.assert_equals(responses[2].status, httpcode.SERVICE_UNAVAILABLE)
