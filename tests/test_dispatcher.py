import functools
import typing as t

from vbcore.aio import get_event_loop
from vbcore.dispatcher import AsyncDispatcher, Dispatcher
from vbcore.tester.asserter import Asserter


def test_dispatcher():
    def dummy(item: str) -> str:
        return item

    def upper(func):
        @functools.wraps(func)
        def inner(item: str):
            return func(item).upper()

        return inner

    class MyDispatcher(Dispatcher[t.Callable[[str], str]]):
        callbacks = {
            "dummy": dummy,
        }
        decorators = (upper,)

    Asserter.assert_equals(MyDispatcher.dispatch("dummy", "data"), "DATA")


def test_async_dispatcher():
    async def dummy(item: str) -> str:
        return item

    async def upper(func):
        @functools.wraps(func)
        async def inner(item: str):
            return (await func(item)).upper()

        return inner

    class MyDispatcher(AsyncDispatcher[t.Callable[[str], t.Awaitable[str]]]):
        callbacks = {
            "dummy": dummy,
        }
        decorators = (upper,)

    loop = get_event_loop()
    data = loop.run_until_complete(MyDispatcher.dispatch("dummy", "data"))

    Asserter.assert_equals(data, "DATA")
