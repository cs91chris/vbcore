import asyncio
import sys
import typing as t

try:
    import nest_asyncio
except ImportError:
    nest_asyncio = None


def is_async(fun: t.Callable) -> bool:
    return asyncio.iscoroutinefunction(fun)


async def wrap_callable(fun: t.Callable, **kwargs) -> t.Any:
    return fun(**kwargs)


async def collect(*args, return_exc: bool = True):
    return await asyncio.gather(*args, return_exceptions=return_exc)


def get_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_running_loop()
        if nest_asyncio is not None:
            nest_asyncio.apply(loop)
    except RuntimeError:
        loop = None

    if sys.version_info.major == 3 and sys.version_info.minor < 10:
        return asyncio.get_event_loop()

    loop = loop or asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop
