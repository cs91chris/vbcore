import asyncio
import sys
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from vbcore import aio
from vbcore.aio import AsyncExecutor
from vbcore.tester.asserter import Asserter


def sample_func():
    return None


async def sample_aio_func():
    return None


@pytest.mark.parametrize(
    "func, expected",
    [
        (sample_func, False),
        (sample_aio_func, True),
    ],
    ids=[
        "not-async",
        "is-async",
    ],
)
def test_is_async(func, expected):
    Asserter.assert_is(aio.is_async(func), expected)


def test_async_wrapper():
    wrapped = aio.async_wrapper(sample_func)

    Asserter.assert_none(sample_func())
    Asserter.assert_not_none(wrapped)
    Asserter.assert_none(asyncio.run(wrapped))


@patch("vbcore.aio.asyncio")
def test_collect(mock_asyncio):
    mock_asyncio.gather = AsyncMock()

    coro1 = sample_aio_func()
    coro2 = sample_aio_func()
    coro3 = sample_aio_func()

    async def run_collect():
        await aio.collect(coro1, coro2, coro3)

    asyncio.run(run_collect())

    mock_asyncio.gather.assert_called_once_with(
        coro1,
        coro2,
        coro3,
        return_exceptions=True,
    )


@patch("vbcore.aio.asyncio")
@patch("vbcore.aio.nest_asyncio")
def test_get_new_event_loop(
    mock_nest_asyncio,
    mock_asyncio,
):
    mock_asyncio.get_running_loop.return_value = None

    aio.get_event_loop()

    mock_asyncio.get_running_loop.assert_called_once()
    mock_nest_asyncio.apply.assert_not_called()
    mock_asyncio.new_event_loop.assert_called_once()
    mock_asyncio.set_event_loop.assert_called_once()


@patch("vbcore.aio.asyncio")
@patch("vbcore.aio.nest_asyncio")
def test_get_running_loop(
    mock_nest_asyncio,
    mock_asyncio,
):
    aio.get_event_loop()

    mock_asyncio.get_running_loop.assert_called_once()
    mock_nest_asyncio.apply.assert_not_called()
    mock_asyncio.new_event_loop.assert_not_called()
    mock_asyncio.set_event_loop.assert_called_once()


@patch("vbcore.aio.asyncio")
@patch("vbcore.aio.nest_asyncio")
def test_get_running_loop_nested(
    mock_nest_asyncio,
    mock_asyncio,
):
    loop = aio.get_event_loop(nested=True)

    mock_asyncio.get_running_loop.assert_called_once()
    mock_nest_asyncio.apply.assert_called_once_with(loop)
    mock_asyncio.new_event_loop.assert_not_called()
    mock_asyncio.set_event_loop.assert_called_once()


@patch("vbcore.aio.asyncio")
@pytest.mark.parametrize(
    "debug, expected",
    [
        (False, None),
        (True, True),
    ],
    ids=[
        "debug-false",
        "debug-true",
    ],
)
def test_execute(mock_asyncio, debug, expected):
    coro = sample_aio_func()
    mock_value = MagicMock()
    mock_asyncio.run.return_value = mock_value
    mock_asyncio.Runner.return_value = mock_value

    return_value = aio.execute(coro, debug=debug)

    if sys.version_info < (3, 11):
        Asserter.assert_is(return_value, mock_value)
        mock_asyncio.run.assert_called_once_with(coro, debug=expected)
    else:
        mock_asyncio.Runner.assert_called_once_with(loop_factory=ANY, debug=debug)
        # TODO assert the context manager


def test_async_executor() -> None:
    async def coroutine(p):
        return p

    expected = "expected"
    executor = AsyncExecutor()
    result = executor.execute(coroutine(expected))
    Asserter.assert_equals(result, expected)
