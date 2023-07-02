import time
from collections import OrderedDict
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from threading import RLock
from typing import Any, Callable

from vbcore.types import OptInt


class LRUCache(OrderedDict):
    """
    Limit size, evicting the least recently looked-up key when full
    """

    def __init__(self, maxsize: int = 128, **kwargs):
        self.maxsize = maxsize
        super().__init__(**kwargs)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]

    def set(self, key, value):
        # pylint: disable=unnecessary-dunder-call
        self[key] = value
        return self[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except AttributeError:
            return default


# based on: https://github.com/mailgun/expiringdict
class ExpiringCache(OrderedDict):
    """
    Dictionary with auto-expiring values for caching purposes.
    Expiration happens on any access, object is locked during cleanup from expired
    values. Can not store more than max_len elements - the oldest will be deleted.
    The values stored in the following way:
    {
        key1: (value1, created_time1),
        key2: (value2, created_time2)
    }
    NOTE: iteration over dict and also keys() do not remove expired values!
    """

    def __init__(self, max_len: int = 128, max_age: float = 0):
        super().__init__(self)
        self._lock = RLock()
        self.max_len = max_len
        self.max_age = max_age

    @staticmethod
    def _item_age(item) -> float:
        return time.time() - item[1]

    def __contains__(self, key):
        try:
            with self._lock:
                item = super().__getitem__(key)
                if self._item_age(item) < self.max_age:
                    return True
                del self[key]
        except KeyError:
            pass
        return False

    def __getitem__(self, key, with_age: bool = False):
        with self._lock:
            item = super().__getitem__(key)
            item_age = self._item_age(item)
            if item_age < self.max_age:
                if with_age:
                    return item[0], item_age
                return item[0]
            del self[key]
            raise KeyError(key)

    def __setitem__(self, key, value, set_time=None):
        with self._lock:
            if len(self) == self.max_len:
                if key in self:
                    del self[key]
                else:
                    try:
                        self.popitem(last=False)
                    except KeyError:
                        pass
            super().__setitem__(key, (value, set_time or time.time()))

    def items(self):
        values = []
        for key in list(self.keys()):  # pylint: disable=consider-using-dict-items
            try:
                values.append((key, self[key]))
            except KeyError:
                pass
        return values

    def items_with_age(self):
        values = []
        for key in list(self.keys()):
            try:
                values.append((key, super().__getitem__(key)))
            except KeyError:
                pass
        return values

    def values(self):
        values = []
        for key in list(self.keys()):  # pylint: disable=consider-using-dict-items
            try:
                values.append(self[key])
            except KeyError:
                pass
        return values

    def pop(self, key, default=None):
        with self._lock:
            try:
                item = super().__getitem__(key)
                del self[key]
                return item[0]
            except KeyError:
                return default

    def ttl(self, key):
        _, key_age = self.get(key, with_age=True)
        if key_age:
            key_ttl = self.max_age - (key_age or 0)
            return key_ttl if key_ttl > 0 else None
        return None

    def get(self, key, default=None, with_age: bool = False):
        try:
            # pylint: disable=unnecessary-dunder-call
            return self.__getitem__(key, with_age)
        except KeyError:
            if with_age:
                return default, None
            return default

    def set(self, key, value, set_time=None):
        # pylint: disable=unnecessary-dunder-call
        self.__setitem__(key, value, set_time=set_time)

    def delete(self, key):
        try:
            with self._lock:
                del self[key]
        except KeyError:
            pass


class TimedLRUCache:
    """
    LRU cache with expiring values to decorate the functions
    Example:

    >>> cache = TimedLRUCache(seconds=1)
    >>>
    >>> @cache
    ... def sample(data: str):
    ...     return data.upper()
    ...
    >>>
    """

    def __init__(
        self,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        milliseconds: int = 0,
        maxsize: OptInt = 128,
        typed: bool = False,
    ):
        self.maxsize = maxsize
        self.typed = typed
        self.lifetime = timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
        )

    def expire_at(self) -> datetime:
        return datetime.utcnow() + self.lifetime

    def prepare(self, func: Callable):
        decorator = lru_cache(self.maxsize, self.typed)
        _func: Any = decorator(func)
        _func.lifetime = self.lifetime
        _func.expiration = self.expire_at()
        return _func

    def __call__(self, func: Callable) -> Callable:
        _func = self.prepare(func)

        @wraps(_func)
        def wrapped(*args, **kwargs) -> Callable:
            if datetime.utcnow() >= _func.expiration:
                _func.cache_clear()
                _func.expiration = self.expire_at()
            return _func(*args, **kwargs)

        return wrapped
