from vbcore import json
from vbcore.datastruct.lazy import Dumper


class BaseHTTPDumper:
    @classmethod
    def dump_headers(cls, hdr, only=()):
        """
        dumps http headers: useful for logging

        @param hdr: headers' dictionary
        @param only: list of headers key to dump
        @return: string representation of headers
                k1: v1
                k2: v2
        """
        hdr = hdr or {}
        if only:
            hdr = {k: hdr[k] for k in only if k in hdr}

        headers = "\n\t".join(f"{k}: {v}" for k, v in hdr.items())
        return headers.strip()

    @classmethod
    def response_filename(cls, headers):
        """
        get filename from Content-Disposition header.
        i.e.: attachment; filename="<file name.ext>"

        @param headers: http headers dict
        @return: only the file name
        """
        headers = headers or {}
        hdr = headers.get("Content-Disposition")
        if not hdr:
            return None  # pragma: no cover

        tmp = hdr.split(";")
        hdr = tmp[1] if len(tmp) > 1 else tmp[0]
        tmp = hdr.split("=")

        if len(tmp) > 1:
            return tmp[1].strip('"').lstrip("<").rstrip(">")
        return None

    @classmethod
    def dump_body(cls, resp):
        """
        @param resp: Response instance
        @return:
        """
        return (
            getattr(resp, "text", None)
            or getattr(resp, "data", None)
            or getattr(resp, "body", None)
        )

    @classmethod
    def dump_status(cls, resp):
        """
        @param resp: Response instance
        @return:
        """
        return getattr(resp, "status_code", None) or getattr(resp, "status", None)

    @classmethod
    def dump_request(cls, req, dump_body=None, only_hdr=()):
        """
        dump http request: useful for logging

        @param req: Request instance
        @param dump_body: flag to enable or disable dump of request's body (overrides default)
        @param only_hdr: dump only a subset of headers
        @return: prettified representation of input as string
        """
        body = ""
        if dump_body is True:
            body = getattr(req, "json", None)
            if body:
                body = json.dumps(body)
            else:
                body = getattr(req, "body", getattr(req, "data", None))
                if isinstance(body, (bytes, bytearray)):
                    body = "Binary body not dumped"
            body = f"\nbody:\n{body}" if body else ""

        headers = cls.dump_headers(req.headers, only=only_hdr)
        headers = f"\nheaders:\n\t{headers}" if headers else ""
        return f"requested {req.method} {req.url}{headers}{body}"

    @classmethod
    def dump_response(cls, resp, dump_body=None, only_hdr=()):
        """
        dump http response: useful for logging

        @param resp: Response instance
        @param dump_body: flag to enable or disable dump of response's body (overrides default)
        @param only_hdr: dump only a subset of headers
        @return: prettified representation of input as string
        """
        body = ""
        if dump_body is True:
            body = cls.response_filename(resp.headers) or cls.dump_body(resp)
            body = f"\nbody:\n{body}" if body else ""

        try:
            seconds = resp.elapsed.total_seconds()
        except AttributeError:
            seconds = "N/A"

        headers = cls.dump_headers(resp.headers, only=only_hdr)
        headers = f"\nheaders:\n\t{headers}" if headers else ""
        status = cls.dump_status(resp)

        return f"response time: {seconds} - status code: {status}{headers}{body}"


class LazyHTTPDumper(BaseHTTPDumper):
    @classmethod
    def dump_request(cls, req, *args, **kwargs):
        return Dumper(req, *args, callback=super().dump_request, **kwargs)

    @classmethod
    def dump_response(cls, resp, *args, **kwargs):
        return Dumper(resp, *args, callback=super().dump_response, **kwargs)
