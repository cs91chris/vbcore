from vbcore.datastruct import ObjectDict
from vbcore.exceptions import VBException
from vbcore.http import httpcode


class RPCError(VBException):
    def __init__(self, code: int, message: str, data=None):
        super().__init__(message, code)
        self.code = code
        self.message = message
        self.data = data

    def as_dict(self) -> ObjectDict:
        return ObjectDict(code=self.code, message=self.message, data=self.data)


class RPCParseError(RPCError):
    def __init__(self, message=None, data=None):
        super().__init__(
            -32700, message or "Invalid JSON was received by the server", data
        )


class RPCInvalidRequest(RPCError):
    def __init__(
        self,
        message=None,
        data=None,
        req_id=None,
    ):
        super().__init__(
            -32600, message or "The JSON sent is not a valid Request object", data
        )
        self.req_id = req_id


class RPCMethodNotFound(RPCError):
    def __init__(self, message=None, data=None):
        super().__init__(
            -32601, message or "The method does not exist or is not available", data
        )


class RPCInvalidParams(RPCError):
    def __init__(self, message=None, data=None):
        super().__init__(-32602, message or "Invalid method parameter(s)", data)


class RPCInternalError(RPCError):
    def __init__(self, message=None, data=None):
        super().__init__(-32603, message or "Internal JSON-RPC error", data)


def rpc_error_to_httpcode(error_code: int) -> int:
    if error_code == RPCParseError().code:
        return httpcode.BAD_REQUEST
    if error_code == RPCInvalidRequest().code:
        return httpcode.BAD_REQUEST
    if error_code == RPCMethodNotFound().code:
        return httpcode.NOT_FOUND
    if error_code == RPCInvalidParams().code:
        return httpcode.UNPROCESSABLE_ENTITY

    return httpcode.INTERNAL_SERVER_ERROR
