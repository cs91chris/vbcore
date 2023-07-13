from vbcore.http import httpcode, HttpMethod
from vbcore.http.batch import HTTPBatch
from vbcore.tester.asserter import Asserter


def test_http_client_batch():
    # TODO improve mocking aioresponses
    client = HTTPBatch(dump_body=(True, False))
    results = client.request(
        [
            {
                "url": "http://localhost/anything",
                "method": HttpMethod.GET,
                "timeout": 0.001,
            },
            {
                "url": "http://fakehost/status",
                "method": HttpMethod.GET,
                "timeout": 0.001,
            },
        ]
    )
    Asserter.assert_equals(results[0].status, httpcode.SERVICE_UNAVAILABLE)
    Asserter.assert_equals(results[1].status, httpcode.SERVICE_UNAVAILABLE)
