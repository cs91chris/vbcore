import click

from vbcore.datastruct.lazy import LazyImporter
from vbcore.db.mysql_dumper import cli_wrapper as mysql_dump_cli_wrapper
from vbcore.loggers import Log
from vbcore.tools.cli import Cli, CliOpt, CliOutputDir, CliOutputFile, CliReqOpt

db_to_schema, dump_model_ddl, model_to_uml = LazyImporter.import_many(
    "vbcore.db.schema:db_to_schema",
    "vbcore.db.schema:dump_model_ddl",
    "vbcore.db.schema:model_to_uml",
    message="you must install vbcore[db]",
)

DIALECTS = ["sqlite", "mysql", "oracle", "postgresql", "mssql"]

main = click.Group(name="database", help="tools for database")


@main.command(name="schema")
@CliOpt.string("-m", "--from-models", help="module of sqlalchemy models")
@CliOpt.string("-d", "--from-database", help="database url connection")
@CliReqOpt.string("-f", "--file", type=CliOutputFile(), help="output png filename")
def dump_schema(from_models, from_database, file):
    """Create png schema of database"""
    if from_models:
        graph = model_to_uml(from_models)
    elif from_database:
        graph = db_to_schema(from_database)
    else:
        raise click.UsageError("One of -m or -d are required")

    try:
        graph.write_png(file)  # pylint: disable=no-member
    except OSError as exc:
        Cli.abort(f"{str(exc)}\ntry to install 'graphviz'")


@main.command(name="dump-ddl")
@CliOpt.choice("--dialect", default="sqlite", values=DIALECTS)
@CliReqOpt.string("-m", "--metadata", help="metadata module")
def dump_ddl(dialect, metadata):
    """Dumps the DDL statements for a given metadata"""
    dump_model_ddl(metadata, dialect)


@main.command(name="mysql-backup")
@Cli.argument("db_url")
@CliOpt.string("--folder", default=".", type=CliOutputDir())
@CliOpt.multi("-i", "--ignore-database")
@CliOpt.boolean("-t", "--add-datetime", default=True)
@CliOpt.flag("-a", "--as-archive")
@CliOpt.string("-d", "--db-prefix")
@CliOpt.string("--datetime-format")
@CliOpt.string("--file-prefix")
def mysql_backup(**kwargs):
    """perform the backup of mysql databases"""
    with Log.execution_time():
        mysql_dump_cli_wrapper(**kwargs)
