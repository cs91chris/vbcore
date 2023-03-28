import json
import logging
import typing as t

from requests import request as http_client

from vbcore.datastruct import ObjectDict
from vbcore.http import httpcode, HttpMethod
from vbcore.http.headers import ContentTypeEnum, HeaderEnum
from vbcore.http.httpdumper import BaseHTTPDumper as HTTPDumper
from vbcore.jsonschema.schemas.jsonrpc import JSONRPC

from .asserter import Asserter
from .helpers import basic_auth_header


class TestHttpCall(HTTPDumper):
    __test__ = False
    default_status_code = (httpcode.SUCCESS, 299)
    default_content_type = ContentTypeEnum.HTML

    def __init__(self, endpoint=None, auth=None, **__):
        self.auth = None
        self.response = None
        self.endpoint = endpoint
        self.log = logging.getLogger()

        if auth:
            self.set_auth(auth)

    def set_url(self, url):
        if not url.startswith("http"):
            self.endpoint = "/".join([self.endpoint.rstrip("/"), url.lstrip("/")])
        else:
            self.endpoint = url

    def set_auth(self, config):
        config = config or {}
        auth_type = config.get("type")
        if auth_type == "basic" and config.get("username"):
            password = config.get("password") or config["username"]
            self.auth = basic_auth_header(config.get("username"), password)

    def assert_status_code(
        self, code: int, in_range: bool = False, is_in: bool = False
    ):
        status_code = self.response.status_code
        if type(code) in (list, tuple):
            if in_range:
                Asserter.assert_range(status_code, code)
            if is_in:
                Asserter.assert_in(status_code, code)
        else:
            Asserter.assert_equals(status_code, code)

    def assert_header(
        self, name: str, value: str, is_in: bool = False, regex: bool = False
    ):
        header = self.response.headers.get(name)
        if is_in:
            Asserter.assert_in(value, header)
        elif regex:
            Asserter.assert_match(value, header)
        else:
            Asserter.assert_equals(header, value)

    def assert_response(self, **kwargs):
        code = kwargs.get("status") or {
            "code": self.default_status_code,
            "in_range": True,
        }
        headers = kwargs.get("headers") or {}
        if HeaderEnum.CONTENT_TYPE not in headers:
            headers[HeaderEnum.CONTENT_TYPE] = {
                "value": rf"{self.default_content_type}*",
                "regex": True,
            }

        self.assert_status_code(**code)
        for k, v in headers.items():
            if v is not None:
                self.assert_header(name=k, **v)

    def request_implementation(self, method, url, **kwargs):
        _ = self
        # pylint: disable=missing-timeout
        return http_client(method, url, **kwargs)

    def request(self, method=HttpMethod.GET, url=None, **kwargs):
        url = url or self.endpoint
        if not url.startswith("http"):
            url = f"{self.endpoint}{url}"

        self.set_auth(kwargs.pop("auth", None))
        if self.auth is not None:
            kwargs["auth"] = self.auth

        request = ObjectDict(method=method, url=url, **kwargs)
        self.response = self.request_implementation(**request)

    def perform(self, request, response=None, **__):
        self.request(**request)
        self.assert_response(**(response or {}))
        return self.response


class TestHttpApi(TestHttpCall):
    default_content_type = ContentTypeEnum.JSON

    @property
    def json(self):
        try:
            if self.response.status_code != httpcode.NO_CONTENT and "json" in (
                self.response.headers.get(HeaderEnum.CONTENT_TYPE) or ""
            ):
                return self.response.get_json()
        except json.decoder.JSONDecodeError as exc:
            raise AssertionError(f"Test that json is valid failed, got: {exc}") from exc
        return None

    def assert_response(self, **kwargs):
        super().assert_response(**kwargs)
        if kwargs.get("schema") is not None:
            Asserter.assert_json_schema(self.json, kwargs.get("schema"))


class TestJsonRPC(TestHttpApi):
    version = "2.0"
    default_schema = JSONRPC.RESPONSE

    # noinspection PyShadowingBuiltins
    @classmethod
    def prepare_payload(
        cls,
        id=False,  # pylint: disable=redefined-builtin
        method: t.Optional[str] = None,
        params: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> t.Dict[str, t.Any]:
        data: t.Dict[str, t.Any] = {"jsonrpc": cls.version, "method": method}

        if id is not False:
            data["id"] = id
        if params:
            data["params"] = params

        return data

    def perform(self, request, response=None, **__):
        req = {"method": HttpMethod.POST}
        res = response or {}
        res.setdefault("schema", self.default_schema)

        if type(request) in (list, tuple):
            req["json"] = [self.prepare_payload(*a) for a in request]
        else:
            req["json"] = self.prepare_payload(**request)

        super().perform(request=req, response=res)


class TestRestApi(TestHttpApi):
    def __init__(
        self,
        *args,
        resource: t.Optional[str] = None,
        res_id: t.Optional[str] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.res_id = res_id or "id"
        self.set_resource(resource)

    def set_resource(
        self,
        resource: t.Optional[str] = None,
        res_id: t.Optional[str] = None,
    ):
        """

        :param resource: resource name
        :param res_id: resource id key
        """
        self.res_id = res_id or self.res_id
        if resource:
            self.endpoint = f"{self.endpoint}/{resource}"

    def resource_url(self, res_id) -> str:
        return f"{self.endpoint}/{res_id}"

    def _normalize(self, request, response, method=HttpMethod.GET, url=None):
        request = request or {}
        response = response or {}
        request["method"] = method
        request["url"] = url or self.endpoint
        return request, response

    def test_collection(self, request=None, response=None):
        req, res = self._normalize(request, response)
        res.setdefault(
            "status",
            {"code": (httpcode.SUCCESS, httpcode.PARTIAL_CONTENT), "is_in": True},
        )
        self.perform(req, res)

    def test_post(self, request=None, response=None):
        req, res = self._normalize(request, response, HttpMethod.POST)
        res.setdefault("status", {"code": httpcode.CREATED})
        self.perform(req, res)

    def test_get(self, res_id, request=None, response=None):
        req, res = self._normalize(request, response, url=self.resource_url(res_id))
        self.perform(req, res)

    def test_put(self, res_id, request=None, response=None):
        req, res = self._normalize(
            request, response, HttpMethod.PUT, self.resource_url(res_id)
        )
        self.perform(req, res)

    def test_delete(self, res_id, request=None, response=None):
        req, res = self._normalize(
            request, response, HttpMethod.DELETE, self.resource_url(res_id)
        )
        res.setdefault("status", {"code": httpcode.NO_CONTENT})
        res.setdefault("headers", {})
        res["headers"][HeaderEnum.CONTENT_TYPE] = None
        self.perform(req, res)
