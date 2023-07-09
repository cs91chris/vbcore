from typing import (
    Any,
    Generator,
    Generic,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

import sqlalchemy as sa

from vbcore.base import BaseDTO
from vbcore.db.sqla import Model

TableType = Union[sa.Table, Type[Model]]
ExecParams = Union[List[Mapping[str, Any]], Mapping[str, Any]]

C = TypeVar("C", bound=BaseDTO)
D = TypeVar("D", bound=BaseDTO)


class BaseRepo(Generic[C, D]):
    def __init__(
        self,
        connection: sa.Connection,
        dto_class: Type[D],
        table: Optional[TableType] = None,
    ):
        self._table = table
        self.dto_class = dto_class
        self.connection = connection

    @property
    def table(self) -> TableType:
        if self._table is None:
            raise ValueError("no table provided")
        return self._table

    def execute(
        self, statement: sa.Executable, parameters: Optional[ExecParams] = None
    ) -> sa.CursorResult:
        return self.connection.execute(statement, parameters=parameters)

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

    def update(self, *clauses, **values) -> int:
        stm = sa.update(self.table).where(*clauses).values(values)  # type: ignore
        cursor = self.execute(stm)
        return cursor.rowcount

    def delete(self, *clauses) -> int:
        stm = sa.delete(self.table).where(*clauses)
        cursor = self.execute(stm)
        return cursor.rowcount

    def prepare_query_dto(self, record: sa.Row) -> D:
        # noinspection PyProtectedMember
        return self.dto_class.from_dict(**record._asdict())

    def query(self, query: sa.Select) -> Generator[D, None, None]:
        for record in self.execute(query):
            yield self.prepare_query_dto(record)
