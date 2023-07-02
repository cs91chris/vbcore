import typing as t

D = t.TypeVar("D", bound="IDict")
OD = t.TypeVar("OD", bound="ObjectDict")


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class IDict(dict):
    def patch(self: D, __dict: t.Optional[D] = None, **kwargs) -> D:
        if __dict:
            super().update(__dict)
        else:
            super().update(**kwargs)
        return self

    def get_namespace(
        self: D,
        prefix: str,
        lowercase: bool = True,
        trim: bool = True,
    ) -> D:
        """
        Returns a dictionary containing a subset of configuration options
        that match the specified prefix.

        :param prefix: a configuration prefix
        :param lowercase: a flag indicating if the keys should be lowercase
        :param trim: a flag indicating if the keys should include the namespace
        """
        _prefix = f"{prefix}_"
        data: D = self.__class__()
        for k, v in self.items():
            if k.startswith(_prefix):
                key = k[len(_prefix) :] if trim else k
                data[key.lower() if lowercase else key] = v
        return data


class ObjectDict(IDict):
    def __init__(self: OD, seq=None, **kwargs):
        super().__init__()
        self.__setstate__(kwargs if seq is None else dict(seq))

    def __setstate__(self, state: dict):
        for k, v in state.items():
            self.__setattr__(k, v)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def __setattr__(self, name, value):
        self[name] = self.normalize(value, raise_exc=False)

    def __delattr__(self, name):
        if name in self:
            del self[name]

    @classmethod
    def normalize(cls, data, raise_exc=True):
        # TODO using cls instead of ObjectDict
        def normalize_iterable(_data: t.Any):
            for r in _data:
                yield ObjectDict(**r) if isinstance(r, t.Mapping) else r

        try:
            if isinstance(data, t.Mapping):
                return ObjectDict(**data)

            if isinstance(data, (tuple, list, set)):
                return type(data)(normalize_iterable(data))

            raise TypeError(f"can not convert '{type(data)}' into {cls}")
        except (TypeError, ValueError, AttributeError):
            if raise_exc is True:
                raise
            return data


class BDict(dict):
    @classmethod
    def from_dict(cls, data: dict) -> "BDict":
        return cls(**data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=invalid-name
        self.T = {v: k for k, v in self.items()}

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.T[value] = key

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.T[self[key]]
