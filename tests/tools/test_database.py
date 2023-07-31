from unittest.mock import MagicMock, patch

from vbcore.tester.asserter import Asserter
from vbcore.tools.entrypoint import main


@patch("vbcore.tools.database.model_to_uml")
def test_dump_schema_from_models(mock_model_to_uml, runner):
    mock_instance = MagicMock()
    mock_model_to_uml.return_value = mock_instance

    result = runner.invoke(
        main,
        ["database", "schema", "--from-models", "app.db.models", "-f", "output.png"],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_model_to_uml.assert_called_once_with("app.db.models")
    mock_instance.write_png.assert_called_once_with("output.png")


@patch("vbcore.tools.database.db_to_schema")
def test_dump_schema_from_database(mock_db_to_schema, runner):
    mock_instance = MagicMock()
    mock_db_to_schema.return_value = mock_instance

    result = runner.invoke(
        main,
        ["database", "schema", "--from-database", "sqlite:///", "-f", "output.png"],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_db_to_schema.assert_called_once_with("sqlite:///")
    mock_instance.write_png.assert_called_once_with("output.png")


@patch("vbcore.tools.database.dump_model_ddl")
def test_dump_ddl(mock_dump_model_ddl, runner):
    result = runner.invoke(
        main,
        ["database", "dump-ddl", "--metadata", "app.db.metadata", "--dialect", "mysql"],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_dump_model_ddl.assert_called_once_with("app.db.metadata", "mysql")


@patch("vbcore.tools.database.mysql_dump_cli_wrapper")
def test_mysql_backup(mock_wrapper, runner):
    result = runner.invoke(main, ["database", "mysql-backup", "mysql://localhost:3306/test"])

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_wrapper.assert_called_once_with(
        db_url="mysql://localhost:3306/test",
        folder=".",
        ignore_database=(),
        add_datetime=True,
        as_archive=False,
        db_prefix=None,
        datetime_format=None,
        file_prefix=None,
    )
