import typing as t
from abc import ABC, abstractmethod

from vbcore.datastruct import ObjectDict
from vbcore.http import httpcode, HttpMethod
from vbcore.http.client import HTTPBase, HTTPClient, JsonRPCClient
from vbcore.http.headers import ContentTypeEnum, HeaderEnum
from vbcore.http.rpc import rpc_error_to_httpcode
from vbcore.types import OptBool, OptStr


class Request(t.NamedTuple):
    host: str
    url: str
    method: str
    headers: dict
    params: dict
    body: t.Any


class Response(t.NamedTuple):
    status: int
    headers: dict
    body: t.Any = None
    exception: t.Optional[Exception] = None


class IncomingRequestData(ABC):  # TODO refactor this
    @classmethod
    @abstractmethod
    def url(cls) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def method(cls) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def body(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def headers(cls) -> t.Dict[str, str]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def params(cls) -> t.Dict[str, t.Any]:
        raise NotImplementedError


class ProxyRequest(ABC):
    client_class: t.Type[HTTPBase] = HTTPClient

    @property
    @abstractmethod
    def request_dto(self) -> t.Type[IncomingRequestData]:
        raise NotImplementedError

    def __init__(
        self,
        host: OptStr = None,
        url: OptStr = None,
        method: OptStr = None,
        proxy_body: bool = False,
        proxy_headers: bool = False,
        proxy_params: bool = False,
        stream: bool = True,
        **kwargs,
    ):
        self._host = host
        self._method = method
        self._url = url
        self._proxy_body = proxy_body
        self._proxy_headers = proxy_headers
        self._proxy_params = proxy_params
        self._options = kwargs
        self._stream = stream

    def perform(self, **kwargs) -> Response:
        request = self.prepare_request()
        response = self.proxy(request, **kwargs)
        return self.prepare_response(response)

    def proxy(self, data: Request, stream: OptBool = None, **kwargs) -> ObjectDict:
        options = {**self._options, **kwargs}
        client = self.client_class(data.host, **options)
        return client.request(
            data.url,
            method=data.method,
            headers=data.headers,
            params=data.params,
            data=data.body,
            stream=self._stream if stream is None else stream,
        )

    def prepare_response(self, resp: t.Optional[ObjectDict]) -> Response:
        if resp and resp.body and resp.status != httpcode.NO_CONTENT:
            return Response(
                body=resp.body,
                status=resp.status,
                headers=resp.headers,
                exception=resp.exception,
            )
        return Response(
            status=httpcode.NO_CONTENT,
            headers=resp.headers,
        )

    def prepare_request(self) -> Request:
        return Request(
            host=self.upstream_host(),
            url=self.request_url(),
            method=self.request_method(),
            headers=self.request_headers(),
            params=self.request_params(),
            body=self.request_body(),
        )

    def upstream_host(self) -> str:
        return self._host

    def request_url(self) -> str:
        return self._url or self.request_dto.url()

    def request_method(self) -> str:
        return self._method or self.request_dto.method()

    def request_body(self) -> t.Optional[t.Any]:
        return self.request_dto.body() if self._proxy_body else None

    def request_headers(self) -> t.Dict[str, str]:
        return self.request_dto.headers() if self._proxy_headers else {}

    def request_params(self) -> t.Dict[str, t.Any]:
        return self.request_dto.params() if self._proxy_params else {}


class JsonRPCProxyRequest(ProxyRequest, ABC):
    request_id_header: str = HeaderEnum.X_REQUEST_ID
    response_content_type: str = ContentTypeEnum.JSON
    client_class: t.Type[JsonRPCClient] = JsonRPCClient

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("stream", False)
        super().__init__(*args, **kwargs)

    def proxy(self, data: Request, stream: OptBool = None, **kwargs) -> ObjectDict:
        url = self.upstream_host()
        client = self.client_class(url, url, **kwargs)

        if self.request_method() == HttpMethod.GET:
            return client.request(
                self.request_method(),
                request_id=self.get_request_id(),
                params=self.request_params(),
                stream=self._stream if stream is None else stream,
                headers=self.request_headers(),
            )

        return client.notification(
            self.request_method(),
            params=self.request_params(),
            stream=self._stream if stream is None else stream,
            headers=self.request_headers(),
        )

    def prepare_response(
        self, resp: t.Optional[ObjectDict] = None, **kwargs
    ) -> Response:
        body = resp
        headers: t.Dict[str, str] = {
            HeaderEnum.CONTENT_TYPE: self.response_content_type,
            **kwargs,
        }
        status = httpcode.NO_CONTENT if resp is None else httpcode.SUCCESS

        if resp and resp.error is not None:
            status = rpc_error_to_httpcode(resp.error.code)
            body = resp.error

        return Response(
            body=body,
            status=status,
            headers=headers,
            exception=resp.exception,
        )

    def get_request_id(self) -> str:
        headers = self.request_headers()
        return headers[self.request_id_header]

    def request_method(self) -> str:
        return self.request_dto.url().split("/")[-1]

    def request_params(self) -> t.Dict[str, t.Any]:
        if self.request_dto.method() == HttpMethod.GET:
            return self.request_dto.params()
        return self.request_body()
