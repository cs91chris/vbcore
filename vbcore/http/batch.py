import asyncio
import typing as t

import aiohttp

from vbcore.batch import AsyncBatchExecutor
from vbcore.datastruct import ObjectDict

from ..types import OptInt, OptStr
from . import HttpMethod
from .client import DumpBodyType, HTTPBase, httpcode, ResponseData


class HTTPBatch(HTTPBase, AsyncBatchExecutor):
    def __init__(
        self,
        endpoint: OptStr = None,
        dump_body: DumpBodyType = False,
        timeout: int = 10,
        raise_on_exc: bool = False,
    ):
        HTTPBase.__init__(self, endpoint, dump_body, timeout, raise_on_exc)
        AsyncBatchExecutor.__init__(self, return_exceptions=not self._raise_on_exc)

    async def http_request(
        self,
        dump_body: t.Optional[DumpBodyType] = None,
        timeout: OptInt = None,
        **kwargs,
    ) -> ResponseData:
        dump_body = self.dump_body_flags(dump_body, **kwargs)

        try:
            self.log.info("%s", self.dump_request(ObjectDict(**kwargs), dump_body[0]))
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(
                    sock_read=timeout or self._timeout,
                    sock_connect=timeout or self._timeout,
                )
            ) as session, session.request(**kwargs) as resp:
                try:
                    body = await resp.json()
                except (aiohttp.ContentTypeError, ValueError, TypeError):
                    body = await resp.text()

                try:
                    response = ResponseData(
                        body=body,
                        status=resp.status,
                        headers={**resp.headers},
                    )
                    log_resp = response
                    log_resp.text = response.body
                    log_resp = self.dump_response(log_resp, dump_body[1])
                    resp.raise_for_status()
                    self.log.info("%s", log_resp)
                except aiohttp.ClientResponseError as exc:
                    self.log.warning("%s", log_resp)
                    if self._raise_on_exc is True:
                        raise  # pragma: no cover
                    response.exception = exc
                return response
        except (
            aiohttp.ClientError,
            aiohttp.ServerTimeoutError,
            asyncio.TimeoutError,
        ) as exc:
            self.log.exception(exc)
            if self._raise_on_exc is True:
                raise  # pragma: no cover

            return ResponseData(
                body={}, status=httpcode.SERVICE_UNAVAILABLE, headers={}, exception=exc
            )

    def request(self, requests, **kwargs):  # pylint: disable=arguments-differ
        for req in requests:
            req.setdefault("method", HttpMethod.GET)
            self._tasks.append((self.http_request, req))

        return self.run()
