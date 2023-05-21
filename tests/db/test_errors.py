import pytest

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
            },
        ),
        (
            exc.DBConstraintError("users", "constraint-1"),
            {
                "error": "DBConstraintError",
                "table": "users",
                "check_name": "constraint-1",
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
            },
        ),
        (
            exc.DBNonExistentConstraint("users", "constraint-1"),
            {
                "error": "DBNonExistentConstraint",
                "table": "users",
                "constraint": "constraint-1",
            },
        ),
        (
            exc.DBNonExistentTable("users"),
            {
                "error": "DBNonExistentTable",
                "table": "users",
            },
        ),
        (
            exc.DBNonExistentDatabase("database"),
            {
                "error": "DBNonExistentDatabase",
                "database": "database",
            },
        ),
        (
            exc.DBInvalidUnicodeParameter(),
            {
                "error": "DBInvalidUnicodeParameter",
                "message": "Invalid Parameter: Encoding directive wasn't provided.",
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
    ],
)
def test_custom_exceptions(exception, data):
    Asserter.assert_equals(exception.as_dict(), data)


@pytest.mark.parametrize(
    "statement, exception, expected",
    [
        (
            "FAIL",
            exc.DBError,
            {
                "error": "DBError",
                "message": '(sqlite3.OperationalError) near "FAIL": syntax error',
            },
        ),
        (
            "SELECT * FROM table_not_found",
            exc.DBNonExistentTable,
            {
                "error": "DBNonExistentTable",
                "table": "table_not_found",
            },
        ),
    ],
    ids=[
        "DBError",
        "DBNonExistentTable",
    ],
)
def test_register_events(statement, exception, expected, connector, support):
    support.register_custom_handlers(connector.engine)

    with pytest.raises(exception) as error:
        support.session.execute(statement)

    Asserter.assert_equals(error.value.as_dict(), expected)
