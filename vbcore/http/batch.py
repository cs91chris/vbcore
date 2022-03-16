import asyncio
import typing as t

import aiohttp

from vbcore.batch import AsyncBatchExecutor
from vbcore.datastruct import ObjectDict
from . import HttpMethod
from .client import HTTPBase, httpcode, DumpBodyType, ResponseData


class HTTPBatch(HTTPBase, AsyncBatchExecutor):
    def __init__(
        self,
        endpoint: str,
        dump_body: DumpBodyType = False,
        timeout: int = 10,
        raise_on_exc: bool = False,
        logger=None,
    ):
        HTTPBase.__init__(self, endpoint, dump_body, timeout, raise_on_exc, logger)
        AsyncBatchExecutor.__init__(self, return_exceptions=not self._raise_on_exc)

    async def http_request(
        self,
        dump_body: t.Optional[DumpBodyType] = None,
        timeout: t.Optional[int] = None,
        **kwargs,
    ) -> ResponseData:
        if dump_body is None:
            dump_body = self._dump_body
        else:
            dump_body = self._normalize_dump_flag(dump_body)

        try:
            self._logger.info(
                "%s", self.dump_request(ObjectDict(**kwargs), dump_body[0])
            )
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
                        headers=dict(**resp.headers),
                    )
                    log_resp = response
                    log_resp.text = response.body
                    log_resp = self.dump_response(log_resp, dump_body[1])
                    resp.raise_for_status()
                    self._logger.info("%s", log_resp)
                except aiohttp.ClientResponseError as exc:
                    self._logger.warning("%s", log_resp)
                    if self._raise_on_exc is True:
                        raise  # pragma: no cover
                    response.exception = exc
                return response
        except (
            aiohttp.ClientError,
            aiohttp.ServerTimeoutError,
            asyncio.TimeoutError,
        ) as exc:
            self._logger.exception(exc)
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
