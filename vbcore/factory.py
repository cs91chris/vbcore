import abc
import enum
import importlib
import inspect
import pkgutil
import types
import typing as t

from vbcore.base import BaseDTO, Static

C = t.TypeVar("C")
P = t.TypeVar("P")
T = t.TypeVar("T", bound=BaseDTO)
E = t.TypeVar("E", bound="ItemEnumMixin")


class ItemEnumMeta(enum.EnumMeta):
    # pylint: disable=bad-mcs-classmethod-argument
    def __new__(mcs, cls, bases, classdict, **kwds):  # noqa: B902
        instance = super().__new__(mcs, cls, bases, classdict, **kwds)
        instance._value2member_map_ = {}
        for item in instance:
            _item = mcs.prepare(item)
            # noinspection PyProtectedMember
            instance._value2member_map_[_item._value_] = _item

        return instance

    # pylint: disable=protected-access,bad-mcs-classmethod-argument
    @classmethod
    def prepare(mcs, item: t.Any) -> t.Any:  # noqa: B902
        product, option = item.value
        item._value_ = product
        item._option_class = option
        return item


class ItemEnumMixin(t.Generic[T]):
    value: t.Any
    _option_class: T
    __members__: dict

    @property
    def option_class(self) -> T:
        return self._option_class

    @classmethod
    def _missing_(cls, value: t.Any) -> t.Optional[t.Any]:
        return getattr(cls, value, None)

    @classmethod
    def items(cls) -> t.List[str]:
        return list(cls.__members__.keys())


class Item(abc.ABC, t.Generic[T]):
    __slots__ = ("options",)

    def __init__(self, options: T, *_, **__):
        self.options = options


class DummyItem(Item[BaseDTO]):
    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "DummyItem":
        return self

    def __getattr__(self, name: t.Any) -> "DummyItem":
        return self


class ItemFactory(t.Generic[E, P], metaclass=Static):
    items: t.Type[E]

    @classmethod
    def instance(cls, name: t.Union[str, E], *args, **kwargs) -> P:
        item = cls.items(name) if isinstance(name, str) else name
        field_names = item.option_class.field_names()
        _options, _kwargs = cls._split_kwargs(field_names, kwargs)
        options = item.option_class(**_options)
        return item.value(*args, options=options, **_kwargs)

    @classmethod
    def _split_kwargs(
        cls,
        options: t.Tuple[str, ...],
        kwargs: t.Dict[str, t.Any],
    ) -> t.Tuple[t.Dict[str, t.Any], t.Dict[str, t.Any]]:
        kw_options = {}

        for opt in options:
            try:
                kw_options[opt] = kwargs.pop(opt)
            except KeyError:
                pass

        return kw_options, kwargs


class ClassLoader(abc.ABC, t.Generic[C]):
    BASE_CLASS: t.Type[C]
    ATTR_LABEL: str = "LABEL"
    PACKAGE: types.ModuleType

    def __init__(self) -> None:
        self._class_map: t.Dict[str, t.Type[C]] = {
            self.class_name(_cls): _cls for _cls in self.load()
        }

    @classmethod
    def pkg_path(cls) -> t.MutableSequence[str]:
        return cls.PACKAGE.__path__

    @classmethod
    def pkg_name(cls) -> str:
        return cls.PACKAGE.__name__

    @classmethod
    def class_name(cls, class_: t.Type[C]) -> str:
        return getattr(class_, cls.ATTR_LABEL, None) or class_.__name__

    @classmethod
    def load(cls) -> t.Generator[t.Type[C], None, None]:
        for obj in pkgutil.walk_packages(cls.pkg_path()):
            module = importlib.import_module(f"{cls.pkg_name()}.{obj.name}")
            for _, class_ in inspect.getmembers(module, inspect.isclass):
                if issubclass(class_, cls.BASE_CLASS) and class_ is not cls.BASE_CLASS:
                    yield class_

    @property
    def names(self) -> t.List[str]:
        return list(self._class_map.keys())

    @property
    def classes(self) -> t.List[t.Type[C]]:
        return list(self._class_map.values())

    def get(self, name: str) -> t.Type[C]:
        return self._class_map[name]
