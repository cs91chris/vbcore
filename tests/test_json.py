import datetime
import uuid
from collections import deque, OrderedDict
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from types import SimpleNamespace
from unittest.mock import patch

from bson.objectid import ObjectId

from vbcore import json
from vbcore.base import BaseDTO
from vbcore.tester.asserter import Asserter


def test_sets_encoder():
    result = json.dumps({"sample": {1, 2, 3}})
    Asserter.assert_equals(result, '{"sample": [1, 2, 3]}')


def test_bytes_encoder():
    result = json.dumps({"sample": b"123"})
    Asserter.assert_equals(result, '{"sample": "123"}')


def test_builtin_encoder():
    class Sample(Enum):
        A = "A"
        B = "B"

    result = json.dumps({"sample": Sample.A})
    Asserter.assert_equals(result, '{"sample": "A"}')

    result = json.dumps({"sample": Decimal("123.12345")})
    Asserter.assert_equals(result, '{"sample": 123.12345}')


def test_datetime_encoder():
    result = json.dumps({"sample": datetime.datetime(year=2020, month=1, day=1, hour=12)})
    Asserter.assert_equals(result, '{"sample": "2020-01-01T12:00:00"}')

    result = json.dumps({"sample": datetime.date(year=2020, month=1, day=1)})
    Asserter.assert_equals(result, '{"sample": "2020-01-01"}')

    result = json.dumps({"sample": datetime.timedelta(days=1)})
    Asserter.assert_equals(result, '{"sample": 86400.0}')


def test_namespace_encoder():
    result = json.dumps({"sample": SimpleNamespace(a=1, b=2)})
    Asserter.assert_equals(result, '{"sample": {"a": 1, "b": 2}}')


@patch("uuid.uuid4")
def test_uuid_encoder(mock_uuid):
    mock_uuid.return_value = uuid.UUID("85c53af8-1905-11ee-a6d2-7b71bab1db3b")
    result = json.dumps({"sample": uuid.uuid4()})
    Asserter.assert_equals(result, '{"sample": "85c53af8-1905-11ee-a6d2-7b71bab1db3b"}')


def test_collection_encoder():
    _deque = deque()
    _deque.append("a")
    _deque.append("b")

    result = json.dumps({"sample": _deque})
    Asserter.assert_equals(result, '{"sample": ["a", "b"]}')

    result = json.dumps({"sample": OrderedDict(a=1, b=2)})
    Asserter.assert_equals(result, '{"sample": {"a": 1, "b": 2}}')


def test_object_id_encoder():
    result = json.dumps({"sample": ObjectId("0123456789ab0123456789ab")})
    Asserter.assert_equals(result, '{"sample": {"$oid": "0123456789ab0123456789ab"}}')


def test_dictable_encoder() -> None:
    @dataclass
    class SampleDTO(BaseDTO):
        id: int
        name: str

    result = json.dumps({"sample": SampleDTO(id=1, name="name")})
    Asserter.assert_equals(result, '{"sample": {"id": 1, "name": "name"}}')


def test_iso_date_decoder():
    result = json.loads('{"sample": {"$datetime": "2020-01-01T12:00:00"}}')
    Asserter.assert_equals(
        result, {"sample": datetime.datetime(year=2020, month=1, day=1, hour=12)}
    )


def test_object_id_decoder():
    result = json.loads('{"sample": {"$oid": "0123456789ab0123456789ab"}}')
    Asserter.assert_equals(result, {"sample": ObjectId("0123456789ab0123456789ab")})
