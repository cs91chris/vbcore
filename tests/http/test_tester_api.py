import responses

from vbcore.http import httpcode
from vbcore.tester.asserter import Asserter
from vbcore.tester.http import TestHttpApi


@responses.activate
def test_http_api():
    responses.add(
        responses.GET,
        match=(responses.matchers.query_param_matcher({"k": "v"}),),
        url="http://fake.endpoint/url/anything",
        status=httpcode.BAD_REQUEST,
        json={"args": {"k": "v"}},
    )

    client = TestHttpApi("http://fake.endpoint/url")
    response = client.perform(
        request={
            "url": "/anything",
            "params": {"k": "v"},
        },
        response={
            "status": {"code": httpcode.BAD_REQUEST},
            "headers": {"Content-Type": {"is_in": True, "value": "json"}},
        },
    )
    Asserter.assert_equals(response.json()["args"]["k"], "v")
