from typing import Generator, Generic, NamedTuple, Optional, Sequence, Type, TypeVar

import sqlalchemy as sa

from vbcore.base import BaseDTO
from vbcore.db.types import (
    ExecParams,
    SqlColumns,
    SqlWhereClause,
    SqlWhereClauses,
    TableType,
)

C = TypeVar("C", bound=BaseDTO)
D = TypeVar("D", bound=BaseDTO)


class BaseRepo:
    def __init__(self, connection: sa.Connection):
        self.connection = connection

    def execute(
        self, statement: sa.Executable, parameters: Optional[ExecParams] = None
    ) -> sa.CursorResult:
        return self.connection.execute(statement, parameters=parameters)


class QuerierRepo(BaseRepo, Generic[D]):
    def __init__(self, connection: sa.Connection, dto_class: Type[D]):
        super().__init__(connection)
        self.dto_class = dto_class

    def prepare_query_dto(self, record: sa.Row) -> D:
        # noinspection PyProtectedMember
        return self.dto_class.from_dict(**record._asdict())

    @classmethod
    def query_builder(
        cls,
        table: TableType,
        columns: SqlColumns = (),
        clauses: SqlWhereClauses = (),
        **kwargs,
    ) -> sa.Select:
        stm = sa.select(*(columns or (table,)))
        stm = stm.select_from(table)
        stm = stm.filter(*clauses)
        stm = stm.filter_by(**kwargs)
        return stm

    def fetch(
        self,
        table: TableType,
        columns: SqlColumns = (),
        clauses: SqlWhereClauses = (),
        **kwargs,
    ) -> Generator[D, None, None]:
        return self.query(self.query_builder(table, columns, clauses, **kwargs))

    def fetch_one(
        self,
        table: TableType,
        columns: SqlColumns = (),
        clauses: SqlWhereClauses = (),
        **kwargs,
    ) -> D:
        query = self.query_builder(table, columns, clauses, **kwargs)
        return self.prepare_query_dto(self.execute(query).one())

    def query(self, query: sa.Select) -> Generator[D, None, None]:
        for record in self.execute(query):
            yield self.prepare_query_dto(record)


class MutatorRepo(BaseRepo, Generic[C]):
    def __init__(self, connection: sa.Connection, table: TableType):
        super().__init__(connection)
        self.table = table

    def insert(self, data: C) -> NamedTuple:
        stm = sa.insert(self.table).values(**data.to_dict())
        cursor = self.execute(stm)
        return cursor.inserted_primary_key

    def insert_many(self, values: Sequence[C]) -> None:
        self.execute(
            sa.insert(self.table),
            [value.to_dict() for value in values],
        )

    def insert_from_select(self, columns: Sequence[str], query: sa.Selectable) -> None:
        stm = sa.insert(self.table).from_select(columns, query)
        self.execute(stm)

    def update(self, *clauses: SqlWhereClause, **values) -> int:
        stm = sa.update(self.table).where(*clauses).values(values)  # type: ignore
        cursor = self.execute(stm)
        return cursor.rowcount

    def delete(self, *clauses: SqlWhereClause) -> int:
        stm = sa.delete(self.table).where(*clauses)
        cursor = self.execute(stm)
        return cursor.rowcount


class CrudRepo(Generic[C, D]):
    def __init__(self, connection: sa.Connection, dto_class: Type[D], table: TableType):
        self.querier = QuerierRepo[D](connection, dto_class)
        self.mutator = MutatorRepo[C](connection, table)

    def get(
        self, columns: SqlColumns = (), clauses: SqlWhereClauses = (), **kwargs
    ) -> D:
        return self.querier.fetch_one(self.mutator.table, columns, clauses, **kwargs)

    def get_all(
        self, columns: SqlColumns = (), clauses: SqlWhereClauses = (), **kwargs
    ) -> Generator[D, None, None]:
        return self.querier.fetch(self.mutator.table, columns, clauses, **kwargs)

    def create(self, data: C) -> NamedTuple:
        return self.mutator.insert(data)

    def update(self, *clauses: SqlWhereClause, **values) -> int:
        return self.mutator.update(*clauses, **values)

    def delete(self, *clauses: SqlWhereClause) -> int:
        return self.mutator.delete(*clauses)
