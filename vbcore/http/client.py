import typing as t

from requests import auth, exceptions as http_exc, request as send_request, Response

from vbcore.datastruct import ObjectDict
from vbcore.http.headers import HeaderEnum
from vbcore.misc import get_uuid
from vbcore.types import OptStr

from ..loggers import VBLoggerMixin
from . import httpcode
from .httpdumper import LazyHTTPDumper
from .methods import HttpMethod

HTTPStatusError = (http_exc.HTTPError,)
NetworkError = (http_exc.ConnectionError, http_exc.Timeout)
all_errors = (*HTTPStatusError, *NetworkError)

DumpBodyType = t.Union[bool, t.Tuple[bool, bool]]


class ResponseData(ObjectDict):
    def __init__(
        self,
        body: t.Union[ObjectDict, t.Iterable, Response],
        status: int,
        headers: t.Optional[t.Dict[str, str]] = None,
        exception: t.Optional[Exception] = None,
    ):
        super().__init__()
        self.body = body
        self.status = status
        self.headers = headers
        self.exception = exception


class HTTPTokenAuth(auth.AuthBase):
    def __init__(self, token: str, token_type: OptStr = None):
        self.token = token
        self.token_type = token_type or "Bearer"

    def __eq__(self, other):
        other_token = getattr(other, "token", None)
        other_token_type = getattr(other, "token_type", None)
        return self.token_type == other_token_type and self.token == other_token

    def __ne__(self, other):
        return not self.__eq__(other)

    def __call__(self, response):
        response.headers["Authorization"] = f"{self.token_type} {self.token}"
        return response


class HTTPBase(LazyHTTPDumper, VBLoggerMixin):
    def __init__(
        self,
        endpoint: str,
        dump_body: DumpBodyType = False,
        timeout: int = 10,
        raise_on_exc: bool = False,
    ):
        self._timeout = timeout
        self._endpoint = endpoint
        self._raise_on_exc = raise_on_exc
        self._dump_body = self.normalize_dump_flags(dump_body)

    @classmethod
    def normalize_dump_flags(
        cls,
        dump_body: t.Optional[DumpBodyType] = None,
    ) -> t.Tuple[bool, bool]:
        if isinstance(dump_body, bool):
            return dump_body, dump_body
        if not dump_body:
            return False, False
        return dump_body

    def dump_body_flags(
        self, dump_body: t.Optional[DumpBodyType] = None, **kwargs
    ) -> t.Tuple[bool, bool]:
        if dump_body is None:
            dump_body = self._dump_body
        else:
            dump_body = self.normalize_dump_flags(dump_body)
        if kwargs.get("stream") is True:  # if stream not dump response body
            dump_body = (dump_body[0], False)
        return dump_body

    def normalize_url(self, url: str) -> str:
        if url.startswith("http"):
            return url

        return f"{self._endpoint}/{url.lstrip('/')}"

    def request(
        self,
        uri: str,
        method: str = HttpMethod.GET,
        dump_body: t.Optional[DumpBodyType] = None,
        raise_on_exc: bool = False,
        **kwargs,
    ) -> ResponseData:
        """
        @param uri:
        @param method:
        @param dump_body:
        @param raise_on_exc:
        @param kwargs:
        """


class HTTPClient(HTTPBase):
    def __init__(
        self,
        endpoint: str,
        token: OptStr = None,
        username: OptStr = None,
        password: OptStr = None,
        auth_with: t.Optional[auth.AuthBase] = None,
        **kwargs,
    ):
        super().__init__(endpoint, **kwargs)
        self._token = token
        self._username = username
        self._password = password
        self._auth_with = auth_with

    def get_auth(self) -> t.Optional[auth.AuthBase]:
        if self._username and self._password:
            return auth.HTTPBasicAuth(self._username, self._password)
        if self._token:
            return HTTPTokenAuth(self._token)
        return self._auth_with

    @staticmethod
    def prepare_response(
        body: t.Optional[t.Any] = None,
        status: int = httpcode.SUCCESS,
        headers: t.Optional[t.Dict[str, str]] = None,
        exception: t.Optional[Exception] = None,
    ) -> ResponseData:
        return ResponseData(
            body=body, status=status, headers=headers or {}, exception=exception
        )

    def request(
        self,
        uri: str,
        method: str = HttpMethod.GET,
        dump_body: t.Optional[DumpBodyType] = None,
        raise_on_exc: bool = False,
        **kwargs,
    ) -> ResponseData:
        kwargs["auth"] = self.get_auth()
        dump_body = self.dump_body_flags(dump_body, **kwargs)

        try:
            url = self.normalize_url(uri)
            req = ObjectDict(method=method, url=url, **kwargs)
            self.log.info("%s", self.dump_request(req, dump_body=dump_body[0]))
            timeout = kwargs.pop("timeout", None) or self._timeout
            response = send_request(method, url, timeout=timeout, **kwargs)
        except NetworkError as exc:
            self.log.exception(exc)
            if raise_on_exc or self._raise_on_exc:
                raise  # pragma: no cover

            return self.prepare_response(
                status=httpcode.SERVICE_UNAVAILABLE, exception=exc
            )

        log_resp = self.dump_response(response, dump_body=dump_body[1])
        try:
            response.raise_for_status()
            self.log.info("%s", log_resp)
        except HTTPStatusError as exc:
            self.log.warning("%s", log_resp)
            response = exc.response
            if raise_on_exc or self._raise_on_exc:
                raise

        body: t.Any = response.text
        if kwargs.get("stream") is True:
            chunk_size = kwargs.pop("chunk_size", None)
            decode_unicode = kwargs.pop("decode_unicode", False)
            body = response.iter_content(chunk_size, decode_unicode)
        elif "json" in (response.headers.get(HeaderEnum.CONTENT_TYPE) or ""):
            body = response.json()

        return self.prepare_response(
            body=body, status=response.status_code, headers=dict(response.headers)
        )

    def get(self, uri: str, **kwargs) -> ResponseData:
        return self.request(uri, **kwargs)

    def post(self, uri: str, **kwargs) -> ResponseData:
        return self.request(uri, method=HttpMethod.POST, **kwargs)

    def put(self, uri: str, **kwargs) -> ResponseData:
        return self.request(uri, method=HttpMethod.PUT, **kwargs)

    def patch(self, uri: str, **kwargs) -> ResponseData:
        return self.request(uri, method=HttpMethod.PATCH, **kwargs)

    def delete(self, uri: str, **kwargs) -> ResponseData:
        return self.request(uri, method=HttpMethod.DELETE, **kwargs)

    def options(self, uri: str, **kwargs) -> ResponseData:
        return self.request(uri, method=HttpMethod.OPTIONS, **kwargs)

    def head(self, uri: str, **kwargs) -> ResponseData:
        return self.request(uri, method=HttpMethod.HEAD, **kwargs)


class JsonRPCClient(HTTPClient):
    def __init__(self, endpoint: str, uri: str, version: str = "2.0", **kwargs):
        super().__init__(endpoint, raise_on_exc=True, **kwargs)
        self._uri = uri
        self._version = version
        self._request_id = None

    @property
    def request_id(self):
        return self._request_id

    def request(
        self, method, request_id=None, **kwargs
    ):  # pylint: disable=arguments-differ
        self._request_id = request_id or get_uuid()
        return self._request(method, **kwargs)

    def notification(self, method, **kwargs):
        self._request_id = None
        return self._request(method, **kwargs)

    def _request(self, method, params=None, **kwargs):
        kwargs.setdefault("raise_on_exc", True)
        resp = super().request(
            self._uri,
            method=HttpMethod.POST,
            json={
                "jsonrpc": self._version,
                "method": method,
                "params": params or {},
                "id": self._request_id,
            },
            **kwargs,
        )

        return resp.body or ObjectDict()
