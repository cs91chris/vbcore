"""
FlatDict is a dict object that allows for single level, delimited
key/value pair mapping of nested dictionaries.

"""

from collections.abc import MutableMapping

# taken from: https://github.com/gmr/flatdict
__version__ = "4.0.1"

NO_DEFAULT = object()


class FlatDict(MutableMapping):
    """
    :class:`FlatDict` is a dictionary object that allows for
    single level, delimited key/value pair mapping of nested dictionaries.
    The default delimiter value is ``:`` but can be changed in the constructor
    or by calling :meth:`FlatDict.set_delimiter`.
    """

    _COERCE: tuple = (dict,)

    def __init__(self, value=None, delimiter=":", dict_class=dict):
        super().__init__()
        self._values = dict_class()
        self._delimiter = delimiter
        self.update(value)

    def __contains__(self, key):
        """
        Check to see if the key exists, checking for both delimited and
        not delimited key values.

        :param mixed key: The key to check for
        """
        if self._has_delimiter(key):
            pk, ck = key.split(self._delimiter, 1)
            return pk in self._values and ck in self._values[pk]
        return key in self._values

    def __delitem__(self, key):
        """
        Delete the item for the specified key, automatically dealing with
        nested children.

        :param mixed key: The key to use
        :raises: KeyError
        """
        if key not in self:
            raise KeyError
        if self._has_delimiter(key):
            pk, ck = key.split(self._delimiter, 1)
            del self._values[pk][ck]
            if not self._values[pk]:
                del self._values[pk]
        else:
            del self._values[key]

    def __eq__(self, other):
        """
        Check for equality against the other value

        :param other: The value to compare
        :type other: FlatDict
        :rtype: bool
        :raises: TypeError
        """
        if isinstance(other, dict):
            return self.as_dict() == other
        if not isinstance(other, self.__class__):
            raise TypeError
        return self.as_dict() == other.as_dict()

    def __ne__(self, other):
        """
        Check for inequality against the other value

        :param other: The value to compare
        :type other: dict or FlatDict
        :rtype: bool
        """
        return not self.__eq__(other)

    def __getitem__(self, key):
        """
        Get an item for the specified key, automatically dealing with
        nested children.

        :param mixed key: The key to use
        :rtype: mixed
        :raises: KeyError
        """
        values = self._values
        key = [key] if isinstance(key, int) else key.split(self._delimiter)
        for part in key:
            values = values[part]
        return values

    def __iter__(self):
        """
        Iterate over the flat dictionary key and values

        :rtype: Iterator
        :raises: RuntimeError
        """
        return iter(self.keys())

    def __len__(self):
        """
        Return the number of items.

        :rtype: int
        """
        return len(self.keys())

    def __reduce__(self):
        """
        Return state information for pickling

        :rtype: tuple
        """
        return type(self), (self.as_dict(), self._delimiter)

    def __repr__(self):
        """
        Return the string representation of the instance.

        :rtype: str
        """
        return f"<{self.__class__.__name__} id={id(self)} {str(self)}>"

    def __setitem__(self, key, value):
        """
        Assign the value to the key, dynamically building nested
        FlatDict items where appropriate.

        :param mixed key: The key for the item
        :param mixed value: The value for the item
        :raises: TypeError
        """
        if isinstance(value, self._COERCE) and not isinstance(value, FlatDict):
            value = self.__class__(value, self._delimiter)
        if self._has_delimiter(key):
            pk, ck = key.split(self._delimiter, 1)
            if pk not in self._values:
                self._values[pk] = self.__class__({ck: value}, self._delimiter)
                return
            if not isinstance(self._values[pk], FlatDict):
                raise TypeError(f"Assignment to invalid type for key {pk}")
            self._values[pk][ck] = value
        else:
            self._values[key] = value

    def __str__(self):
        """
        Return the string value of the instance.

        :rtype: str
        """
        # pylint: disable=consider-using-dict-items,consider-using-f-string
        return "{{{}}}".format(", ".join([f"{k!r}: {self[k]!r}" for k in self.keys()]))

    def as_dict(self):
        """
        Return the :class:`~flatdict.FlatDict` as a :class:`dict`

        :rtype: dict
        """
        out = dict({})
        for key in self.keys():
            if self._has_delimiter(key):
                pk, ck = key.split(self._delimiter, 1)
                if self._has_delimiter(ck):
                    ck = ck.split(self._delimiter, 1)[0]
                if isinstance(self._values[pk], FlatDict) and pk not in out:
                    out[pk] = {}
                if isinstance(self._values[pk][ck], FlatDict):
                    out[pk][ck] = self._values[pk][ck].as_dict()
                else:
                    out[pk][ck] = self._values[pk][ck]
            else:
                out[key] = self._values[key]
        return out

    def clear(self):
        """
        Remove all items from the flat dictionary.
        """
        self._values.clear()

    def copy(self):
        """
        Return a shallow copy of the flat dictionary.

        :rtype: flatdict.FlatDict
        """
        return self.__class__(self.as_dict(), delimiter=self._delimiter)

    def get(self, key, default=None):
        """
        Return the value for key if key is in the flat dictionary, else
        default. If default is not given, it defaults to ``None``, so that this
        method never raises :exc:`KeyError`.

        :param mixed key: The key to get
        :param mixed default: The default value
        :rtype: mixed
        """
        try:
            return self[key]
        except KeyError:
            return default

    def items(self):
        """
        Return a copy of the flat dictionary's list of ``(key, value)``
        pairs.

        .. note:: CPython implementation detail: Keys and values are listed in
            an arbitrary order which is non-random, varies across Python
            implementations, and depends on the flat dictionary's history of
            insertions and deletions.

        :rtype: list
        """
        # pylint: disable=consider-using-dict-items
        return [(k, self[k]) for k in self.keys()]

    def iteritems(self):
        """
        Return an iterator over the flat dictionary's (key, value) pairs.
        See the note for :meth:`flatdict.FlatDict.items`.

        Using ``iteritems()`` while adding or deleting entries in the flat
        dictionary may raise :exc:`RuntimeError` or fail to iterate over all
        entries.

        :rtype: Iterator
        :raises: RuntimeError
        """
        yield from self.items()

    def iterkeys(self):
        """
        Iterate over the flat dictionary's keys. See the note for
        :meth:`flatdict.FlatDict.items`.

        Using ``iterkeys()`` while adding or deleting entries in the flat
        dictionary may raise :exc:`RuntimeError` or fail to iterate over all
        entries.

        :rtype: Iterator
        :raises: RuntimeError
        """
        yield from self.keys()

    def itervalues(self):
        """
        Return an iterator over the flat dictionary's values. See the note
        :meth:`flatdict.FlatDict.items`.

        Using ``itervalues()`` while adding or deleting entries in the flat
        dictionary may raise a :exc:`RuntimeError` or fail to iterate over all
        entries.

        :rtype: Iterator
        :raises: RuntimeError
        """
        yield from self.values()

    def keys(self):
        """
        Return a copy of the flat dictionary's list of keys.
        See the note for :meth:`flatdict.FlatDict.items`.

        :rtype: list
        """
        keys = []

        for key, value in self._values.items():
            if isinstance(value, (FlatDict, dict)):
                nested = [self._delimiter.join([str(key), str(k)]) for k in value.keys()]
                keys += nested if nested else [key]
            else:
                keys.append(key)

        return keys

    def pop(self, key, default=NO_DEFAULT):
        """
        If key is in the flat dictionary, remove it and return its value,
        else return default. If default is not given and key is not in the
        dictionary, :exc:`KeyError` is raised.

        :param mixed key: The key name
        :param mixed default: The default value
        :rtype: mixed
        """
        if key not in self and default != NO_DEFAULT:
            return default
        value = self[key]
        self.__delitem__(key)  # pylint: disable=unnecessary-dunder-call
        return value

    def setdefault(self, key, default=None):
        """
        If key is in the flat dictionary, return its value. If not,
        insert key with a value of default and return default.
        default defaults to ``None``.

        :param mixed key: The key name
        :param mixed default: The default value
        :rtype: mixed
        """
        if key not in self:
            self[key] = default
        return self[key]

    def set_delimiter(self, delimiter):
        """
        Override the default or passed in delimiter with a new value. If
        the requested delimiter already exists in a key, a :exc:`ValueError`
        will be raised.

        :param str delimiter: The delimiter to use
        :raises: ValueError
        """
        for key in self.keys():
            if delimiter in key:
                raise ValueError(f"Key {key} collides with delimiter {delimiter}")
        self._delimiter = delimiter
        for key in self._values.keys():
            if isinstance(self._values[key], FlatDict):
                self._values[key].set_delimiter(delimiter)

    def update(self, __m=None, **kwargs):  # pylint: disable=arguments-differ
        """
        Update the flat dictionary with the key/value pairs from other,
        overwriting existing keys.

        ``update()`` accepts either another flat dictionary object or an
        iterable of key/value pairs (as tuples or other iterables of length
        two). If keyword arguments are specified, the flat dictionary is then
        updated with those key/value pairs: ``d.update(red=1, blue=2)``.

        :rtype: None
        """
        for k, v in dict(__m or kwargs).items():
            self[k] = v

    def values(self):
        """
        Return a copy of the flat dictionary's list of values. See the note
        for :meth:`flatdict.FlatDict.items`.

        :rtype: list
        """
        # pylint: disable=consider-using-dict-items
        return [self[k] for k in self.keys()]

    def _has_delimiter(self, key):
        """
        Checks to see if the key contains the delimiter.

        :rtype: bool
        """
        return isinstance(key, str) and self._delimiter in key


class FlatterDict(FlatDict):
    """
    Like :class:`FlatDict` but also coerces lists and sets
    to child-dict instances with the offset as the key. Alternative to
    the implementation added in v1.2 of FlatDict.
    """

    _COERCE: tuple = list, tuple, set, dict, FlatDict
    _ARRAYS = list, set, tuple

    def __init__(self, value=None, delimiter=":", dict_class=dict):
        self.original_type = type(value)
        if self.original_type in self._ARRAYS:
            value = {str(i): v for i, v in enumerate(value)}
        super().__init__(value, delimiter, dict_class)

    def __setitem__(self, key, value):
        """
        Assign the value to the key, dynamically building nested
        FlatDict items where appropriate.

        :param mixed key: The key for the item
        :param mixed value: The value for the item
        :raises: TypeError
        """
        if isinstance(value, self._COERCE) and not isinstance(value, FlatterDict):
            value = self.__class__(value, self._delimiter)
        if self._has_delimiter(key):
            pk, ck = key.split(self._delimiter, 1)
            if pk not in self._values:
                self._values[pk] = self.__class__({ck: value}, self._delimiter)
                return
            if getattr(self._values[pk], "original_type", None) in self._ARRAYS:
                try:
                    k, cck = ck.split(self._delimiter, 1)
                    int(k)
                except ValueError as exc:
                    raise TypeError(
                        f"Assignment to invalid type for key {pk}{self._delimiter}{ck}"
                    ) from exc
                self._values[pk][k][cck] = value
                return
            if not isinstance(self._values[pk], FlatterDict):
                raise TypeError(f"Assignment to invalid type for key {pk}")
            self._values[pk][ck] = value
        else:
            self._values[key] = value

    def as_dict(self):
        """
        Return the :class:`~flatdict.FlatterDict` as a nested
        :class:`dict`.

        :rtype: dict
        """
        out = {}
        for key in self.keys():
            if self._has_delimiter(key):
                pk, _ = key.split(self._delimiter, 1)
                if isinstance(self._values[pk], FlatterDict) and pk not in out:
                    if self._values[pk].original_type == tuple:
                        out[pk] = tuple(self._child_as_list(pk))
                    elif self._values[pk].original_type == list:
                        out[pk] = self._child_as_list(pk)
                    elif self._values[pk].original_type == set:
                        out[pk] = set(self._child_as_list(pk))
                    elif self._values[pk].original_type == dict:
                        out[pk] = self._values[pk].as_dict()
            else:
                if isinstance(self._values[key], FlatterDict):
                    out[key] = self._values[key].original_type()
                else:
                    out[key] = self._values[key]
        return out

    def _child_as_list(self, pk, ck=None):
        """
        Returns a list of values from the child FlatterDict instance
        with string based integer keys.

        :param str pk: The parent key
        :param str ck: The child key, optional
        :rtype: list
        """
        if ck is None:
            subset = self._values[pk]
        else:
            subset = self._values[pk][ck]
        # Check if keys has delimiter, which implies deeply nested dict
        keys = subset.keys()
        if any(self._has_delimiter(k) for k in keys):
            out = []
            split_keys = {k.split(self._delimiter)[0] for k in keys}
            for k in sorted(split_keys, key=int):
                if subset[k].original_type == tuple:
                    out.append(tuple(self._child_as_list(pk, k)))
                elif subset[k].original_type == list:
                    out.append(self._child_as_list(pk, k))
                elif subset[k].original_type == set:
                    out.append(set(self._child_as_list(pk, k)))
                elif subset[k].original_type == dict:
                    out.append(subset[k].as_dict())
            return out

        return [subset[k] for k in keys]
