import typing as t

from vbcore import aio
from vbcore.base import Static

C = t.TypeVar("C", bound=t.Callable)
A = t.TypeVar("A", bound=t.Callable[..., t.Awaitable[t.Any]])


class Dispatcher(t.Generic[C], metaclass=Static):
    callbacks: t.Dict[str, C]
    decorators: t.Tuple[C, ...] = ()

    @classmethod
    def dispatch(cls, name: str, *args, **kwargs) -> t.Any:
        callback = cls.callbacks[name]

        for decorator in cls.decorators:
            callback = decorator(callback)

        return callback(*args, **kwargs)


class AsyncDispatcher(t.Generic[A], metaclass=Static):
    callbacks: t.Dict[str, A]
    decorators: t.Tuple[A, ...] = ()

    @classmethod
    async def dispatch(cls, name: str, *args, **kwargs) -> t.Any:
        callback = cls.callbacks[name]

        for decorator in cls.decorators:
            if aio.is_async(decorator):
                callback = await decorator(callback)
            else:
                callback = decorator(callback)

        return await callback(*args, **kwargs)
