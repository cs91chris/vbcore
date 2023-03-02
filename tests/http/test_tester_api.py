from vbcore.http import httpcode
from vbcore.tester.asserter import Asserter
from vbcore.tester.http import TestHttpApi


def test_http_api():
    client = TestHttpApi("http://httpbin.org")
    response = client.perform(
        request={
            "url": "/anything",
            "params": {"k": "v"},
        },
        response={
            "status": {"code": httpcode.SUCCESS},
            "headers": {"Content-Type": {"is_in": True, "value": "json"}},
        },
    )
    Asserter.assert_equals(response.json()["args"]["k"], "v")
