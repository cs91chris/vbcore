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


class JsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.custom_object_hook, *args, **kwargs)

    @staticmethod
    def custom_object_hook(dct):
        if "$oid" in dct:
            try:
                return ObjectId(dct["$oid"])
            except (TypeError, InvalidId):
                pass
        for k, v in dct.items():
            try:
                dct[k] = datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except (TypeError, ValueError):
                pass
        return dct


def dumps(data, *args, **kwargs):
    kwargs.setdefault("cls", JsonEncoder)
    return json.dumps(data, *args, **kwargs)


def loads(data, *args, **kwargs):
    kwargs.setdefault("object_hook", JsonDecoder.custom_object_hook)
    return json.loads(data, *args, **kwargs)
