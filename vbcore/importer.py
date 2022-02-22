import importlib
import typing as t
from types import ModuleType


class ImporterError(Exception):
    pass


class ImporterModuleError(ImporterError):
    def __init__(self, name, exc: Exception):
        self.exception = exc
        self.name = name
        super().__init__(exc)


class ImporterValueError(ImporterError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"class not registered: '{name}'")


class ImporterSubclassError(ImporterError):
    def __init__(self, item: t.Any, subclass_of: t.Type):
        self.item = item
        self.subclass_of = subclass_of
        class_name = f"{subclass_of.__module__}:{subclass_of.__name__}"
        super().__init__(f"'{item}' must be subclass of '{class_name}'")


class ImporterInstanceError(ImporterError):
    def __init__(self, item: t.Any, instance_of: t.Type):
        self.item = item
        self.instance_of = instance_of
        class_name = f"{instance_of.__module__}:{instance_of.__name__}"
        super().__init__(f"'{item}' must be instance of '{class_name}'")


class ImporterAttributeError(ImporterError):
    def __init__(self, module: ModuleType, attribute: t.Optional[str] = None):
        self.module = module
        self.attribute = attribute
        super().__init__(f"attribute '{attribute}' not found in module '{module}'")


class Importer:
    attribute_separator: str = ":"

    @classmethod
    def check_subclass(cls, item: t.Any, subclass_of: t.Optional[t.Type]):
        if subclass_of and isinstance(item, type) and not issubclass(item, subclass_of):
            raise ImporterSubclassError(item, subclass_of)

    @classmethod
    def check_isinstance(cls, item: t.Any, instance_of: t.Optional[t.Type]):
        if instance_of and not isinstance(item, instance_of):
            raise ImporterInstanceError(item, instance_of)

    @classmethod
    def parse_string(cls, name: str) -> t.Tuple[str, t.Optional[str]]:
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
        package: t.Optional[str] = None,
        call_with: bool = False,
        raise_exc: bool = True,
        **kwargs,
    ) -> t.Any:
        mod, attr = cls.parse_string(name)

        try:
            module = importlib.import_module(mod, package)
        except ModuleNotFoundError as exc:
            if raise_exc:
                raise ImporterModuleError(mod, exc) from exc
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

        if call_with is False and not (args and kwargs):
            return imported

        return imported(*args, **kwargs) if args and kwargs else imported()


class ImporterFactory:
    def __init__(
        self,
        base_class: t.Optional[t.Type] = None,
        package: t.Optional[str] = None,
        classes: t.Optional[t.Dict[str, str]] = None,
    ):
        self.base_class = base_class
        self.package = package
        self.classes: t.Optional[t.Dict[str, str]] = {}
        if classes:
            self.register_classes(classes)

    def register_classes(self, classes: t.Optional[t.Dict[str, str]]):
        for key, value in classes.items():
            self.register_class(key, value)

    def register_class(self, name: str, module_class: str):
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
