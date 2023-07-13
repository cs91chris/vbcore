import importlib
import typing as t

from sqlalchemy import create_mock_engine, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import class_mapper

from vbcore.db.schema_display.db_diagram import create_schema_graph
from vbcore.db.schema_display.model_diagram import create_uml_graph
from vbcore.db.sqla import SQLAConnector
from vbcore.loggers import Log
from vbcore.types import OptStr


def model_to_uml(
    module: str,
    show_operations: bool = True,
    show_attributes: bool = True,
    show_datatypes: bool = True,
    show_inherited: bool = True,
    show_multiplicity_one: bool = True,
    **kwargs,
):
    mappers = []
    models = importlib.import_module(module)

    for attr in dir(models):
        try:
            cls = getattr(models, attr)
            mappers.append(class_mapper(cls))
        except Exception as exc:  # pylint: disable=broad-exception-caught
            Log.get(__name__).debug(exc)

    return create_uml_graph(
        mappers,
        show_operations=show_operations,
        show_attributes=show_attributes,
        show_datatypes=show_datatypes,
        show_inherited=show_inherited,
        show_multiplicity_one=show_multiplicity_one,
        **kwargs,
    )


def db_to_schema(
    url: str,
    show_datatypes: bool = True,
    show_indexes: bool = True,
    concentrate: bool = True,
    rankdir: str = "TB",
    **kwargs,
):
    connector = SQLAConnector(url)
    return create_schema_graph(
        engine=connector.engine,
        metadata=connector.metadata,
        show_datatypes=show_datatypes,
        show_indexes=show_indexes,
        concentrate=concentrate,
        rankdir=rankdir,
        format_schema_name={"bold": True, "fontsize": "12"},
        format_table_name={"bold": True, "fontsize": "12"},
        **kwargs,
    )


def dump_model_ddl(metadata: MetaData, dialect: OptStr = None):
    dialect = dialect or "sqlite"

    def executor(sql, *_, **__):
        compiled = sql.compile(dialect=engine.dialect)
        print(compiled.replace("\n\n", ""), ";", sep="")

    engine = create_mock_engine(f"{dialect}://", executor=executor)
    metadata.create_all(t.cast(Engine, engine))
