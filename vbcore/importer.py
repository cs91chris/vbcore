import importlib
import typing as t


class Importer:
    attribute_separator = ":"

    @classmethod
    def from_module(
        cls,
        name: str,
        *args,
        subclass_of: t.Type = None,
        create: bool = False,
        raise_exc: bool = True,
        **kwargs,
    ) -> t.Any:
        """

        :param name:
        :param args:
        :param subclass_of:
        :param create:
        :param raise_exc:
        :param kwargs:
        :return:
        """
        if cls.attribute_separator in name:
            mod, attr = name.split(cls.attribute_separator)
        else:
            mod, attr = name, None

        module = importlib.import_module(mod)
        if attr is None:
            return module

        if raise_exc:
            ia = getattr(module, attr)
        else:
            ia = getattr(module, attr, None)

        if raise_exc and subclass_of and not issubclass(ia, subclass_of):
            raise TypeError(f"'{name}' must be subclass of {subclass_of}")

        if args or kwargs:
            return ia(*args, **kwargs)

        return ia() if create is True else ia
