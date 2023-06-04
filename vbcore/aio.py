import asyncio
import sys
import typing as t

try:
    import nest_asyncio
except ImportError:  # pragma: no cover
    nest_asyncio = None


def is_async(fun: t.Callable) -> bool:
    return asyncio.iscoroutinefunction(fun)


async def async_wrapper(fun: t.Callable, **kwargs) -> t.Any:
    return fun(**kwargs)


async def collect(*args, return_exc: bool = True) -> t.Any:
    return await asyncio.gather(*args, return_exceptions=return_exc)


def get_event_loop(*, nested: bool = False) -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_running_loop()
        if loop and nest_asyncio is not None and nested is True:
            nest_asyncio.apply(loop)
    except RuntimeError:
        loop = None

    if sys.version_info.major == 3 and sys.version_info.minor < 10:
        return asyncio.get_event_loop()

    loop = loop or asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def execute(
    main: t.Coroutine,
    *,
    debug: bool = False,
    loop_factory: t.Optional[t.Callable[[], asyncio.AbstractEventLoop]] = None,
    signals_handler: t.Optional[t.Callable[[asyncio.AbstractEventLoop], None]] = None,
) -> t.Any:
    """
    It should be used as a main entry point for asyncio programs
    and should ideally only be called once
    """
    if sys.version_info < (3, 11):
        return asyncio.run(main, debug=debug or None)

    _loop_factory = loop_factory or get_event_loop
    # only for py3.10
    # pylint: disable=no-member
    with asyncio.Runner(loop_factory=_loop_factory, debug=debug) as service:
        if signals_handler is not None:
            signals_handler(service.get_loop())
        return service.run(main)
