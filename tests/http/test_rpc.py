import pytest

from vbcore.http import rpc
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "error_class, error_code",
    [
        (rpc.RPCParseError, -32700),
        (rpc.RPCInvalidRequest, -32600),
        (rpc.RPCMethodNotFound, -32601),
        (rpc.RPCInvalidParams, -32602),
        (rpc.RPCInternalError, -32603),
    ],
    ids=[
        "parse-error",
        "invalid-request",
        "method-not-found",
        "invalid-params",
        "internal-error",
    ],
)
def test_rpc_error_as_dict(error_class, error_code):
    data = {"a": 1, "b": 2}
    error = error_class(data=data).as_dict()
    expected = {"code": error_code, "message": error.message, "data": data}
    Asserter.assert_equals(error, expected)


@pytest.mark.parametrize(
    "error_code, http_code",
    [
        (-32700, 400),
        (-32600, 400),
        (-32601, 404),
        (-32602, 422),
        (-32603, 500),
    ],
)
def test_rpc_error_to_httpcode(error_code, http_code):
    Asserter.assert_equals(rpc.rpc_error_to_httpcode(error_code), http_code)
