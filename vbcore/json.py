import datetime
import json
import uuid
from collections import Counter, defaultdict, deque, OrderedDict
from decimal import Decimal
from enum import Enum
from types import SimpleNamespace
from typing import Any, Callable, Optional, Type, Union

from vbcore.types import CoupleStr, OptInt

OptCallableHook = Optional[Callable[[Any], Any]]

JSONDecodeError = json.JSONDecodeError


try:
    # noinspection PyUnresolvedReferences
    from bson import ObjectId
    from bson.errors import InvalidId
except ImportError:  # pragma: no cover
    ObjectId = str
    InvalidId = ValueError


class SetsEncoderMixin(json.JSONEncoder):
    def default(self, o, *_, **__):
        if isinstance(o, (set, frozenset)):
            return list(o)
        return super().default(o)


class BytesEncoderMixin(json.JSONEncoder):
    def default(self, o, *_, **__):
        if isinstance(o, (bytes, bytearray)):
            return o.decode()
        return super().default(o)


class BuiltinEncoderMixin(BytesEncoderMixin, SetsEncoderMixin):
    def default(self, o, *_, **__):
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


class DateTimeEncoderMixin(json.JSONEncoder):
    def default(self, o, *_, **__):
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()
        if isinstance(o, datetime.timedelta):
            return o.total_seconds()
        return super().default(o)


class NamespaceEncoderMixin(json.JSONEncoder):
    def default(self, o, *_, **__):
        if isinstance(o, SimpleNamespace):
            return o.__dict__
        return super().default(o)


class CollectionsEncoderMixin(json.JSONEncoder):
    def default(self, o, *_, **__):
        if isinstance(o, deque):
            return list(o)
        if isinstance(o, (defaultdict, OrderedDict, Counter)):
            return dict(o)
        try:
            # check for namedtuple compliant
            # noinspection PyProtectedMember
            return o._asdict()
        except AttributeError:
            pass

        return super().default(o)


class HexUUIDMixin(json.JSONEncoder):
    def default(self, o, *_, **__):
        if isinstance(o, uuid.UUID):
            return o.hex
        return super().default(o)


class ObjectIdMixin(json.JSONEncoder):
    def default(self, o, *_, **__):
        if isinstance(o, ObjectId):
            return {"$oid": str(o)}
        return super().default(o)


class DictableMixin(json.JSONEncoder):
    methods = ("to_dict", "asdict", "dict", "as_dict", "todict")

    def default(self, o, *_, **__):
        for name in self.methods:
            method = getattr(o, name, None)
            if method is not None:
                return method()
        return super().default(o)


class JsonEncoder(
    BuiltinEncoderMixin,
    DateTimeEncoderMixin,
    NamespaceEncoderMixin,
    CollectionsEncoderMixin,
    HexUUIDMixin,
    ObjectIdMixin,
    DictableMixin,
):
    """
    Extends all encoders provided with this module
    """

    def default(self, o, *_, **__):
        return super().default(o)


class JsonObjectDecoderMixin:
    @classmethod
    def custom_object_hook(cls, data: dict) -> dict:
        return data

    @classmethod
    def custom_field_hook(cls, value):
        return value


class JsonISODateDecoder(JsonObjectDecoderMixin):
    ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"

    @classmethod
    def custom_field_hook(cls, value):
        if isinstance(value, str):
            try:
                return datetime.datetime.strptime(value, cls.ISO_FORMAT)
            except (TypeError, ValueError):
                return value

        return super().custom_object_hook(value)


class JsonObjectIdDecoder(JsonObjectDecoderMixin):
    @classmethod
    def custom_object_hook(cls, data: dict):
        if "$oid" in data:
            try:
                return ObjectId(data["$oid"])
            except (TypeError, InvalidId):
                return data

        return super().custom_object_hook(data)


class JsonDecoder(
    json.JSONDecoder,
    JsonObjectIdDecoder,
    JsonISODateDecoder,
):
    """
    Extends all decoders provided with this module
    """

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.custom_object_hook, *args, **kwargs)

    @classmethod
    def custom_object_hook(cls, data: dict) -> dict:
        # noinspection PyBroadException
        try:
            data = super().custom_object_hook(data)
            return {k: super().custom_field_hook(v) for k, v in data.items()}
        except Exception:  # pylint: disable=broad-except
            return data


def dumps(
    data: Any,
    *,
    skipkeys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    cls: Type[json.JSONEncoder] = JsonEncoder,
    indent: OptInt = None,
    separators: Optional[CoupleStr] = None,
    default: OptCallableHook = None,
    sort_keys: bool = False,
    **kwargs,
) -> str:
    return json.dumps(
        data,
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        cls=cls,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys,
        **kwargs,
    )


def loads(
    data: Union[str, bytes, bytearray],
    *,
    cls: Type[json.JSONDecoder] = JsonDecoder,
    object_hook: OptCallableHook = None,
    parse_float: OptCallableHook = None,
    parse_int: OptCallableHook = None,
    parse_constant: OptCallableHook = None,
    object_pairs_hook: OptCallableHook = None,
    **kwargs,
) -> dict:
    return json.loads(
        data,
        cls=cls,
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        object_pairs_hook=object_pairs_hook,
        **kwargs,
    )
