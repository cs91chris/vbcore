from vbcore.http import httpcode
from vbcore.tester.http import TestHttpApi
from vbcore.tester.mixins import Asserter


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
