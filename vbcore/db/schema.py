import importlib
import typing as t

from sqlalchemy import create_mock_engine, MetaData  # type: ignore
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import class_mapper
from sqlalchemy_schemadisplay import create_schema_graph, create_uml_graph


def model_to_uml(
    module: str,
    show_operations: bool = False,
    show_attributes: bool = True,
    show_inherited: bool = True,
    show_datatypes: bool = True,
    **kwargs,
):
    mappers = []
    models = importlib.import_module(module)

    for attr in dir(models):
        if attr[0] == "_":
            continue
        try:
            cls = getattr(models, attr)
            mappers.append(class_mapper(cls))
        except SQLAlchemyError:
            pass

    return create_uml_graph(
        mappers,
        show_operations=show_operations,
        show_attributes=show_attributes,
        show_inherited=show_inherited,
        show_datatypes=show_datatypes,
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
    return create_schema_graph(
        metadata=MetaData(url),  # type: ignore
        show_datatypes=show_datatypes,
        show_indexes=show_indexes,
        concentrate=concentrate,
        rankdir=rankdir,
        **kwargs,
    )


def dump_model_ddl(metadata: MetaData, dialect: t.Optional[str] = None):
    dialect = dialect or "sqlite"

    def executor(sql, *_, **__):
        compiled = sql.compile(dialect=engine.dialect).replace("\n\n", "")
        print(compiled, ";", sep="")  # type: ignore

    engine = create_mock_engine(f"{dialect}://", executor=executor)
    metadata.create_all(t.cast(Engine, engine))
