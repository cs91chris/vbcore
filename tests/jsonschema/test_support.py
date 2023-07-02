from textwrap import dedent

import pytest
from jsonschema import ValidationError

from vbcore.jsonschema.schemas.jsonrpc import JSONRPC
from vbcore.jsonschema.support import JSONSchema
from vbcore.tester.asserter import Asserter

_ = JSONSchema, JSONRPC


@pytest.mark.skip("implement me")
def test_jsonschema_load_from_url():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_jsonschema_load_from_file():
    """TODO implement me"""


def test_jsonschema_validate():
    data = {
        "jsonrpc": "2.0",
        "id": "action-id",
        "method": "Sample.action",
        "params": {},
    }
    Asserter.assert_true(JSONSchema.validate(data, JSONRPC.REQUEST))


def test_jsonschema_error_report():
    data = {"id": "action-id", "params": {}}
    try:
        JSONSchema.validate(data, JSONRPC.REQUEST, raise_exc=True)
        Asserter.assert_true(False)
    except ValidationError as error:
        report = JSONSchema.error_report(error, data)
        Asserter.assert_equals(
            report,
            "{'id': 'action-id', 'params': {}} is not valid under any of the given schemas",
        )

    data = {
        "jsonrpc": 2,
        "id": "action-id",
        "method": "Sample.action",
        "params": {},
    }
    try:
        JSONSchema.validate(data, JSONRPC.REQUEST, raise_exc=True)
        Asserter.assert_true(False)
    except ValidationError as error:
        report = JSONSchema.error_report(error, data)
        expected = dedent(
            """
                2 is not one of ['2.0']
                Error in line 2:
                   1:    {
                   2: >>>    "jsonrpc": 2,
                   3:        "id": "action-id",
                   4:        "method": "Sample.action",
                   5:        "params": {}
                   6:    }
                2 is not one of ['2.0']
            """
        )
        Asserter.assert_equals(report, expected.strip())
