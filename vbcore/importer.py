import importlib
import typing as t
from types import ModuleType

from vbcore.exceptions import VBException
from vbcore.types import OptStr


class ImporterError(VBException):
    pass


class ImporterModuleError(ImporterError):
    def __init__(self, name: str, exc: Exception):
        self.name = name
        self.exception = exc
        super().__init__(f"unable to import module: {name}", orig=exc)


class ImporterValueError(ImporterError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"class not registered: '{name}'")


class ImporterClassError(ImporterError):
    def __init__(self, item: t.Any, class_: t.Type):
        self.item = item
        self.class_ = class_
        self.class_name = f"{class_.__module__}:{class_.__name__}"
        super().__init__(str(self))


class ImporterSubclassError(ImporterClassError):
    def __str__(self) -> str:
        return f"'{self.item}' must be subclass of '{self.class_name}'"


class ImporterInstanceError(ImporterClassError):
    def __str__(self) -> str:
        return f"'{self.item}' must be instance of '{self.class_name}'"


class ImporterAttributeError(ImporterError):
    def __init__(self, module: ModuleType, attribute: t.Optional[str] = None):
        self.module = module
        self.attribute = attribute
        super().__init__(f"attribute '{attribute}' not found in module '{module}'")


class Importer:
    attribute_separator: str = ":"

    @classmethod
    def check_subclass(cls, item: t.Any, subclass_of: t.Optional[t.Type]) -> None:
        if subclass_of and isinstance(item, type) and not issubclass(item, subclass_of):
            raise ImporterSubclassError(item, subclass_of)

    @classmethod
    def check_isinstance(cls, item: t.Any, instance_of: t.Optional[t.Type]) -> None:
        if instance_of and not isinstance(item, instance_of):
            raise ImporterInstanceError(item, instance_of)

    @classmethod
    def parse_string(cls, name: str) -> t.Tuple[str, OptStr]:
        if cls.attribute_separator in name:
            mod, attr = name.split(cls.attribute_separator)
            return mod, attr
        return name, None

    @classmethod
    def from_module(
        cls,
        name: str,
        *args,
        subclass_of: t.Optional[t.Type] = None,
        instance_of: t.Optional[t.Type] = None,
        package: OptStr = None,
        call_with: bool = False,
        raise_exc: bool = True,
        **kwargs,
    ) -> t.Any:
        mod, attr = cls.parse_string(name)

        try:
            module = importlib.import_module(mod, package)
        except ModuleNotFoundError as exc:
            if raise_exc:
                name = f"{package}.{mod}" if package else mod
                raise ImporterModuleError(name, exc) from exc
            return None

        if attr is None:
            return module

        if raise_exc:
            try:
                imported = getattr(module, attr)
            except AttributeError as exc:
                raise ImporterAttributeError(module, attr) from exc
        else:
            imported = getattr(module, attr, None)

        cls.check_subclass(imported, subclass_of)
        cls.check_isinstance(imported, instance_of)

        if call_with is False and not (args or kwargs):
            return imported

        return imported(*args, **kwargs) if args or kwargs else imported()


class ImporterFactory:
    def __init__(
        self,
        package: OptStr = None,
        base_class: t.Optional[t.Type] = None,
        classes: t.Optional[t.Dict[str, str]] = None,
    ):
        self.package = package
        self.base_class = base_class
        self.classes: t.Optional[t.Dict[str, str]] = {}
        self.register_classes(classes or {})

    def register_classes(self, classes: t.Optional[t.Dict[str, str]]) -> None:
        for key, value in classes.items():
            self.register_class(key, value)

    def register_class(self, name: str, module_class: str) -> None:
        self.classes[name] = f".{module_class}" if self.package else module_class

    def get_instance(self, name: str, *args, **kwargs):
        return self.get_class(name, *args, call_with=True, **kwargs)

    def get_class(self, name: str, *args, call_with: bool = False, **kwargs):
        if name not in self.classes:
            raise ImporterValueError(name)

        return Importer.from_module(
            self.classes[name],
            *args,
            call_with=call_with,
            package=self.package,
            subclass_of=self.base_class,
            **kwargs,
        )
