from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Callable, Optional, TYPE_CHECKING, Union

from gql import Client, gql
from gql.transport import AsyncTransport, Transport
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from gql.transport.requests import RequestsHTTPTransport
from graphql import ExecutionResult

from vbcore.datastruct.lazy import LazyImporter
from vbcore.types import StrDict

if TYPE_CHECKING:
    from gql.transport.websockets import WebsocketsTransport
else:
    WebsocketsTransport = LazyImporter.do_import(
        "gql.transport.websockets:WebsocketsTransport",
        message="you must install 'websockets'",
    )


class GQLClientBase(ABC):
    def __init__(self, endpoint: str, raise_if_error: bool = False, **kwargs):
        self.endpoint = endpoint
        self.raise_if_error = raise_if_error
        self.transport = self.prepare_transport(**kwargs)
        self.client = Client(transport=self.transport)

    @abstractmethod
    def prepare_transport(self, **kwargs) -> Union[Transport, AsyncTransport]:
        raise NotImplementedError

    def result_from_error(self, error: TransportQueryError) -> ExecutionResult:
        if self.raise_if_error is True:
            raise error

        return ExecutionResult(
            data=error.data,
            errors=error.errors,
            extensions=error.extensions,
        )

    @classmethod
    def execution_wrapper(
        cls,
        function: Callable,
        statement: str,
        headers: Optional[StrDict] = None,
        **kwargs,
    ) -> Any:
        return function(
            gql(statement),
            get_execution_result=True,
            variable_values=kwargs,
            extra_args={"headers": headers},
        )


class GQLClient(GQLClientBase):
    def prepare_transport(self, **kwargs) -> RequestsHTTPTransport:
        return RequestsHTTPTransport(url=self.endpoint, **kwargs)

    def perform(
        self, statement: str, headers: Optional[StrDict] = None, **kwargs
    ) -> ExecutionResult:
        try:
            func = self.client.execute_sync
            return self.execution_wrapper(func, statement, headers, **kwargs)
        except TransportQueryError as exc:
            return self.result_from_error(exc)


class GQLClientAIO(GQLClientBase):
    def prepare_transport(self, **kwargs) -> AIOHTTPTransport:
        return AIOHTTPTransport(url=self.endpoint, **kwargs)

    async def perform(
        self, statement: str, headers: Optional[StrDict] = None, **kwargs
    ) -> ExecutionResult:
        try:
            func = self.client.execute_async
            return await self.execution_wrapper(func, statement, headers, **kwargs)
        except TransportQueryError as exc:
            return self.result_from_error(exc)


class GQLClientWS(GQLClientBase):
    def prepare_transport(self, **kwargs) -> WebsocketsTransport:
        return WebsocketsTransport(url=self.endpoint, **kwargs)

    async def perform(
        self, statement: str, headers: Optional[StrDict] = None, **kwargs
    ) -> ExecutionResult:
        try:
            func = self.client.execute_async
            return await self.execution_wrapper(func, statement, headers, **kwargs)
        except TransportQueryError as exc:
            return self.result_from_error(exc)

    async def subscribe(
        self, statement: str, headers: Optional[StrDict] = None, **kwargs
    ) -> AsyncGenerator[ExecutionResult, None]:
        async with self.client as session:
            try:
                func = session.subscribe
                listener = self.execution_wrapper(func, statement, headers, **kwargs)
                async for result in listener:
                    yield result
            except TransportQueryError as exc:
                yield self.result_from_error(exc)
