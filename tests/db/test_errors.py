import pytest
import sqlalchemy as sa

from vbcore.db import exceptions as exc
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "exception, data",
    [
        (
            exc.DBDuplicateEntry(["col-1"], "value"),
            {
                "error": "DBDuplicateEntry",
                "columns": ["col-1"],
                "value": "value",
                "message": None,
            },
        ),
        (
            exc.DBConstraintError("users", "constraint-1"),
            {
                "error": "DBConstraintError",
                "table": "users",
                "check_name": "constraint-1",
                "message": None,
            },
        ),
        (
            exc.DBReferenceError("users", "constraint-1", "col-1", "key-table-1"),
            {
                "error": "DBReferenceError",
                "table": "users",
                "constraint": "constraint-1",
                "key": "col-1",
                "key_table": "key-table-1",
                "message": None,
            },
        ),
        (
            exc.DBNonExistentConstraint("users", "constraint-1"),
            {
                "error": "DBNonExistentConstraint",
                "table": "users",
                "constraint": "constraint-1",
                "message": None,
            },
        ),
        (
            exc.DBNonExistentTable("users"),
            {
                "error": "DBNonExistentTable",
                "table": "users",
                "message": None,
            },
        ),
        (
            exc.DBNonExistentDatabase("database"),
            {
                "error": "DBNonExistentDatabase",
                "database": "database",
                "message": None,
            },
        ),
        (
            exc.DBInvalidUnicodeParameter(),
            {
                "error": "DBInvalidUnicodeParameter",
                "message": exc.DBInvalidUnicodeParameter.default_message,
            },
        ),
        (
            exc.DBDataError(),
            {
                "error": "DBDataError",
                "message": exc.DBDataError.default_message,
            },
        ),
        (
            exc.DBNotSupportedError(),
            {
                "error": "DBNotSupportedError",
                "message": exc.DBNotSupportedError.default_message,
            },
        ),
        (
            exc.DBDeadlock(),
            {
                "error": "DBDeadlock",
                "message": exc.DBDeadlock.default_message,
            },
        ),
        (
            exc.DBConnectionError(),
            {
                "error": "DBConnectionError",
                "message": exc.DBConnectionError.default_message,
            },
        ),
    ],
    ids=[
        "DBDuplicateEntry",
        "DBConstraintError",
        "DBReferenceError",
        "DBNonExistentConstraint",
        "DBNonExistentTable",
        "DBNonExistentDatabase",
        "DBInvalidUnicodeParameter",
        "DBDataError",
        "DBNotSupportedError",
        "DBDeadlock",
        "DBConnectionError",
    ],
)
def test_custom_exceptions(exception, data):
    Asserter.assert_equals(exception.as_dict(), data)


@pytest.mark.parametrize(
    "statement, exception, expected",
    [
        (
            sa.text("FAIL"),
            exc.DBError,
            {
                "error": "DBError",
                "message": None,
            },
        ),
        (
            sa.text("SELECT * FROM table_not_found"),
            exc.DBNonExistentTable,
            {
                "error": "DBNonExistentTable",
                "table": "table_not_found",
                "message": None,
            },
        ),
    ],
    ids=[
        "DBError",
        "DBNonExistentTable",
    ],
)
def test_register_events(statement, exception, expected, connector, support):
    with pytest.raises(exception) as error:
        support.session.execute(statement)

    Asserter.assert_equals(error.value.as_dict(), expected)
