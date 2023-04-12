import typing as t
from base64 import b64encode
from unittest.mock import AsyncMock, MagicMock

from vbcore.datastruct import ObjectDict
from vbcore.tester.fetchmail import FetchMail


def fetch_emails(
    subject: str, recipient: t.Optional[str] = None, **kwargs
) -> t.List[ObjectDict]:
    return FetchMail(**kwargs).perform(recipient=recipient, subject=subject)


def basic_auth_header(username: str, password: str) -> t.Dict[str, str]:
    token = b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def build_url(url: str, **params) -> t.Tuple[str, str]:
    args = "&".join([f"{k}={v}" for k, v in params.items()])
    if args:
        return f"{url}?{args}", args
    return url, ""


def do_not_dump_long_string(field: str, limit: int = 20) -> str:
    if field and len(field) < limit:
        return field
    return "None" if not field else field[:limit]


class WithAsyncContextManager:
    def __init__(self, instance: t.Any):
        self.instance = instance

    async def __aenter__(self, *_, **__):
        return self.instance

    async def __aexit__(self, *_, **__):
        pass


class MockHelper:
    @classmethod
    def mock_instance(cls, **kwargs) -> t.Tuple[MagicMock, MagicMock]:
        mock_instance = MagicMock(**kwargs)
        mock_class = MagicMock(return_value=mock_instance)
        return mock_class, mock_instance

    @classmethod
    def async_mock_instance(cls, **kwargs) -> t.Tuple[MagicMock, AsyncMock]:
        mock_instance = AsyncMock(**kwargs)
        mock_class = MagicMock(return_value=mock_instance)
        return mock_class, mock_instance

    @classmethod
    def mock_async_for(cls, data: t.Any) -> AsyncMock:
        mock_instance = AsyncMock()
        mock_instance.__aiter__.return_value = data
        return mock_instance

    @classmethod
    def mock_async_with(cls, data: t.Any) -> AsyncMock:
        return AsyncMock(WithAsyncContextManager(data))
