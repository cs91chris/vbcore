import datetime
import json
import uuid
from collections import Counter, defaultdict, deque, OrderedDict
from decimal import Decimal
from enum import Enum
from types import SimpleNamespace

JSONDecodeError = json.JSONDecodeError

try:
    # noinspection PyUnresolvedReferences
    from bson import ObjectId
    from bson.errors import InvalidId
except ImportError:
    ObjectId = str
    InvalidId = ValueError


class SetsEncoderMixin(json.JSONEncoder):
    """
    Encoders for: set, frozenset
    """

    def default(self, o, *_, **__):
        if isinstance(o, (set, frozenset)):
            return list(o)

        return super().default(o)


class BytesEncoderMixin(json.JSONEncoder):
    """
    Encoders for: bytes, bytearray
    """

    def default(self, o, *_, **__):
        if isinstance(o, (bytes, bytearray)):
            return o.decode()

        return super().default(o)


class BuiltinEncoderMixin(BytesEncoderMixin, SetsEncoderMixin):
    """
    Encoders for: Enum, Decimal
    Extends: BytesEncoderMixin, SetsEncoderMixin
    """

    def default(self, o, *_, **__):
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Decimal):
            return float(o)

        return super().default(o)


class DateTimeEncoderMixin(json.JSONEncoder):
    """
    Encoders for: datetime, date, time, timedelta
    """

    def default(self, o, *_, **__):
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()
        if isinstance(o, datetime.timedelta):
            return o.total_seconds()

        return super().default(o)


class TypesEncoderMixin(json.JSONEncoder):
    """
    Encoders for: types
    """

    def default(self, o, *_, **__):
        if isinstance(o, SimpleNamespace):
            return o.__dict__

        return super().default(o)


class CollectionsEncoderMixin(json.JSONEncoder):
    """
    Encoders for: collections
    """

    def default(self, o, *_, **__):
        if isinstance(o, deque):
            return list(o)
        if isinstance(o, (defaultdict, OrderedDict, Counter)):
            return dict(o)
        try:
            # check for namedtuple compliant
            # noinspection PyProtectedMember
            return o._asdict()
        except (AttributeError, TypeError):
            pass

        return super().default(o)


class ExtraEncoderMixin(json.JSONEncoder):
    """
    Encoders for: UUID, ObjectId and object with methods: to_dict, asdict
    """

    def default(self, o, *_, **__):
        if isinstance(o, uuid.UUID):
            return o.hex
        if isinstance(o, ObjectId):
            return {"$oid": str(o)}
        try:
            return o.asdict()
        except (AttributeError, TypeError):
            pass
        try:
            return o.to_dict()
        except (AttributeError, TypeError):
            pass

        return super().default(o)


class JsonEncoder(
    BuiltinEncoderMixin,
    DateTimeEncoderMixin,
    TypesEncoderMixin,
    CollectionsEncoderMixin,
    ExtraEncoderMixin,
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
                pass

        return value


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
            data = {k: super().custom_field_hook(v) for k, v in data.items()}
        except Exception:  # pylint: disable=broad-except
            pass
        return data


def dumps(data, *args, **kwargs):
    kwargs.setdefault("cls", JsonEncoder)
    return json.dumps(data, *args, **kwargs)


def loads(data, *args, **kwargs):
    kwargs.setdefault("object_hook", JsonDecoder.custom_object_hook)
    return json.loads(data, *args, **kwargs)
