from typing import Any, List, Mapping, Sequence, Type, TYPE_CHECKING, Union

from sqlalchemy import Table
from sqlalchemy.orm import scoped_session, Session
from sqlalchemy.sql import ColumnExpressionArgument
from sqlalchemy.sql._typing import _ColumnsClauseArgument

if TYPE_CHECKING:
    from vbcore.db.base import Model
else:
    Model = Any

SqlColumns = Sequence[_ColumnsClauseArgument[Any]]
TableType = Union[Table, Type[Model]]
SqlWhereClause = ColumnExpressionArgument[bool]
SqlWhereClauses = Sequence[SqlWhereClause]
ExecParams = Union[List[Mapping[str, Any]], Mapping[str, Any]]
SessionType = Union[scoped_session, Session]
