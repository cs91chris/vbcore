import dataclasses
import functools
import typing as t

from vbcore.types import CallableDictType

if t.TYPE_CHECKING:
    # prevent mypy issue

    # noinspection PyPep8Naming
    from dataclasses import dataclass as Data
else:
    # TODO at the moment this is not used because pycharm issue
    Data = dataclasses.dataclass(frozen=True, kw_only=True)


# noinspection PyDataclass
class BaseDTO:
    """
    Use this class as mixin for dataclasses

    >>> from dataclasses import dataclass

    >>> @Data
    ... class MyDTO(BaseDTO):
    ...     name: str
    ...     age: int
    ...
    >>> data = {"name": "pippo", "age": 12}
    >>> instance = MyDTO(name="pippo", age=12)

    >>> instance == MyDTO.from_dict(**data)
    True
    >>> instance.to_dict() == data
    True
    """

    def __call__(self, *_, **kwargs):
        """implements prototype pattern"""
        return self.__class__.from_dict(**{**self.to_dict(), **kwargs})

    @classmethod
    def field_names(cls) -> t.Tuple[str, ...]:
        return tuple(f.name for f in dataclasses.fields(cls))

    @classmethod
    def field_types(cls) -> dict:
        # noinspection PyDataclass
        return {item.name: item.type.__name__ for item in dataclasses.fields(cls)}

    def to_dict(self, *_, factory: CallableDictType = dict, **__) -> dict:
        return dataclasses.asdict(self, dict_factory=factory)

    @classmethod
    def from_dict(cls, *_, **kwargs):
        # noinspection PyArgumentList
        return cls(**{k: v for k, v in kwargs.items() if k in cls.field_names()})


class Singleton(type):
    """
    Makes classes singleton, use this as metaclass, i.e.:

    >>> class MyClass:
    ...     pass
    ...
    >>> class MySingletonClass(MyClass, metaclass=Singleton):
    ...     pass
    ...
    >>> MyClass() is MyClass()
    False
    >>> MySingletonClass() is MySingletonClass()
    True
    """

    # private map of instances
    __instances: t.Dict[t.Type, t.Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]


class Static(type):
    """
    Makes classes static, use this as metaclass, i.e.:

    >>> class MyStaticClass(metaclass=Static):
    ...     pass
    ...
    >>> MyStaticClass()
    Traceback (most recent call last):
        ...
    TypeError: can not instantiate Static class MyStaticClass
    """

    def __call__(cls):
        raise TypeError(f"can not instantiate Static class {cls.__name__}")


class Decorator:
    def __call__(self, function: t.Callable) -> t.Any:
        @functools.wraps(function)
        def decorated(*args, **kwargs):
            return self.perform(function, *args, **kwargs)

        return decorated

    def perform(self, function: t.Callable, *args, **kwargs) -> t.Any:
        self.before_call_hook()
        result = function(*args, **kwargs)
        self.after_call_hook()
        return result

    def before_call_hook(self, *_, **__) -> t.Any:
        """hook called before decorated function execution"""

    def after_call_hook(self, *_, **__) -> t.Any:
        """hook called after decorated function execution"""
