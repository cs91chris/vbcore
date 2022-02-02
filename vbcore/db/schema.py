import importlib
import typing as t

from sqlalchemy import MetaData, create_mock_engine  # type: ignore
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import class_mapper
from sqlalchemy_schemadisplay import create_schema_graph, create_uml_graph


def model_to_uml(module):
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

    return create_uml_graph(mappers, show_operations=False)


def db_to_schema(url: str):
    return create_schema_graph(
        metadata=MetaData(url),
        show_datatypes=False,
        show_indexes=False,
        rankdir="LR",
        concentrate=False,
    )


def dump_model_ddl(metadata: MetaData, dialect: t.Optional[str] = None):
    dialect = dialect or "sqlite"

    def executor(sql, *_, **__):
        compiled = sql.compile(dialect=engine.dialect).replace("\n\n", "")
        print(compiled, ";", sep="")  # type: ignore

    engine = create_mock_engine(f"{dialect}://", executor=executor)
    metadata.create_all(engine)
