import sys

import click

try:
    from vbcore.db.schema import db_to_schema, dump_model_ddl, model_to_uml
except ImportError:
    db_to_schema = dump_model_ddl = model_to_uml = None


DIALECTS = ["sqlite", "mysql", "oracle", "postgresql", "mssql"]

main = click.Group(name="database", help="tools for database")


def check_dependency(label):
    if label is None:
        raise ImportError("you must install vbcore[db]")


@main.command(name="schema")
@click.option("-m", "--from-models", help="module of sqlalchemy models")
@click.option("-d", "--from-database", help="database url connection")
@click.option("-f", "--file", required=True, help="output png filename")
def dump_schema(from_models, from_database, file):
    """Create png schema of database"""
    check_dependency(model_to_uml or db_to_schema)

    if from_models:
        graph = model_to_uml(from_models)
    elif from_database:
        graph = db_to_schema(from_database)
    else:
        raise click.UsageError("One of -m or -d are required")

    try:
        graph.write_png(file)  # pylint: disable=E1101
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        print("try to install 'graphviz'", file=sys.stderr)


@main.command(name="dump-ddl")
@click.option("--dialect", default="sqlite", type=click.Choice(DIALECTS))
@click.option("-m", "--metadata", help="metadata module", required=True)
def dump_ddl(dialect, metadata):
    """Dumps the create table statements for a given metadata"""
    check_dependency(dump_model_ddl)
    dump_model_ddl(metadata, dialect)
