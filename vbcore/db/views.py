from typing import Optional, Type

from sqlalchemy import MetaData
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import Select
from sqlalchemy.sql.compiler import SQLCompiler

from vbcore.db.listener import Listener
from vbcore.types import OptStr


# pylint: disable=too-many-ancestors, abstract-method
class DDLView(DDLElement):
    # TODO I do not know why it is required
    __slots__ = ()

    def __init__(self, name: str, schema: OptStr = None):
        self.name = name
        self.schema = schema


class DDLDropView(DDLView):
    pass


class DDLCreateView(DDLView):
    def __init__(
        self,
        name: str,
        select: Select,
        schema: OptStr = None,
        metadata: Optional[MetaData] = None,
        drop_class: Type[DDLDropView] = DDLDropView,
    ):
        super().__init__(name, schema)
        self.name = name
        self.select = select
        self.drop_class = drop_class
        if metadata is not None:
            self.register_listener(metadata)

    def register_listener(self, metadata: MetaData):
        ddl_drop = self.drop_class(self.name, self.schema)
        Listener.register_before_drop(metadata, ddl_drop)
        # emit a "drop" and a "create" for better compatibility
        Listener.register_after_create(metadata, ddl_drop)
        Listener.register_after_create(metadata, self)


def register_views_compiler(
    create_class: Type[DDLCreateView] = DDLCreateView,
    drop_class: Type[DDLDropView] = DDLDropView,
) -> None:
    def view_name(element: DDLView) -> str:
        return f"{element.schema}.{element.name}" if element.schema else element.name

    @compiles(create_class)
    def create_view(element: DDLCreateView, compiler: SQLCompiler, **__) -> str:
        query = compiler.sql_compiler.process(element.select, literal_binds=True)
        return f"CREATE VIEW {view_name(element)} AS {query}"

    @compiles(drop_class)
    def drop_view(element: DDLDropView, _: SQLCompiler, **__) -> str:
        return f"DROP VIEW IF EXISTS {view_name(element)}"
