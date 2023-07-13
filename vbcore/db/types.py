from typing import Any, List, Mapping, Sequence, Type, Union

from sqlalchemy import Table
from sqlalchemy.sql import ColumnExpressionArgument
from sqlalchemy.sql._typing import _ColumnsClauseArgument

from vbcore.db.sqla import Model

SqlColumns = Sequence[_ColumnsClauseArgument[Any]]
TableType = Union[Table, Type[Model]]
SqlWhereClause = ColumnExpressionArgument[bool]
SqlWhereClauses = Sequence[SqlWhereClause]
ExecParams = Union[List[Mapping[str, Any]], Mapping[str, Any]]
