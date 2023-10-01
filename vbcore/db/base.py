import typing as t
from dataclasses import make_dataclass
from functools import partial
from typing import ClassVar, Type, Union

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import as_declarative, mapped_column, Session

from vbcore.base import BaseDTO
from vbcore.db.sqla import SQLAConnector
from vbcore.loggers import Log
from vbcore.misc import get_uuid
from vbcore.types import StrDict, StrTuple

LoadersType = t.Tuple[t.Type["LoaderModel"], ...]


class StrSize:
    small: ClassVar[int] = 50
    medium: ClassVar[int] = 255
    large: ClassVar[int] = 20_000


class Func:
    NOW = partial(sa.func.now)  # pylint:disable=not-callable
    COUNT = partial(sa.func.count)  # pylint:disable=not-callable
    CAST = partial(sa.func.cast)  # pylint:disable=not-callable
    COALESCE = partial(sa.func.coalesce)  # pylint:disable=not-callable
    SUM = partial(sa.func.sum)  # pylint:disable=not-callable
    MAX = partial(sa.func.max)  # pylint:disable=not-callable
    MIN = partial(sa.func.min)  # pylint:disable=not-callable
    CONCAT = partial(sa.func.concat)  # pylint:disable=not-callable
    SYSDATE = partial(sa.func.sysdate)  # pylint:disable=not-callable
    CURRENT_DATE = partial(sa.func.current_date)  # pylint:disable=not-callable
    CURRENT_TIME = partial(sa.func.current_time)  # pylint:disable=not-callable
    CURRENT_TIMESTAMP = partial(sa.func.current_timestamp)  # pylint:disable=not-callable
    NEXT_VALUE = partial(sa.func.next_value)  # pylint:disable=not-callable


def create_index(tablename: str, *columns: str, **kwargs) -> sa.Index:
    col_names = "-".join(columns)
    return sa.Index(f"idx-{tablename}-{col_names}", *columns, **kwargs)


class StrCol:
    small: sa.String = sa.String(StrSize.small)
    medium: sa.String = sa.String(StrSize.medium)
    large: Type[sa.Text] = sa.Text


class Column:
    id: ClassVar = partial(mapped_column, sa.Integer, primary_key=True)
    auto: ClassVar = partial(mapped_column, sa.Integer, primary_key=True, autoincrement=True)
    uuid: ClassVar = partial(mapped_column, sa.String(36), primary_key=True, default=get_uuid)
    date_created: ClassVar = partial(mapped_column, sa.DateTime, server_default=Func.NOW())
    date_updated: ClassVar = partial(mapped_column, sa.DateTime, onupdate=Func.NOW())
    description: ClassVar = partial(mapped_column, sa.Text(), nullable=True)
    decimal: ClassVar = partial(mapped_column, sa.Numeric(9, 3))


class BaseModel:
    __table__: sa.Table
    dto_class: t.Type[BaseDTO]

    def __init__(self, *_, **__):
        """only to avoid warnings"""

    def columns(self) -> StrTuple:
        if self.__table__ is None:
            return ()
        return tuple(self.__table__.columns.keys())

    def to_dict(self) -> StrDict:
        return {col: getattr(self, col, None) for col in self.columns()}

    @classmethod
    def from_dto(cls, dto: Union[BaseDTO, dict]):
        if isinstance(dto, BaseDTO):
            return cls(**dto.to_dict())
        return cls(**dto)

    def to_dto(self):
        items = tuple((col, getattr(self, col, None)) for col in self.columns())
        dto_class = self.dto_class
        if self.dto_class is None:
            dto_class = make_dataclass(
                f"{self.__class__.__name__}DTO",
                [(col, type(value)) for col, value in items],
                bases=(BaseDTO,),
                frozen=True,
            )
        return dto_class(**dict(items))


@as_declarative(metadata=SQLAConnector.metadata)
class Model(BaseModel):
    pass


@as_declarative(metadata=SQLAConnector.views_metadata)
class ViewModel(BaseModel):
    """
    NOTE: the models that maps the views must be in a separate declarative base
    so the views are not affected by create_all and drop_all
    """


class LoaderModel(Model):
    __abstract__ = True

    values: t.Sequence[StrDict] = ()

    @classmethod
    def load_values(cls, session: Session, *_, **__) -> None:
        try:
            session.add_all(cls(**d) for d in cls.values)
            session.commit()
        except SQLAlchemyError as exc:
            Log.get(cls.__module__).exception(exc)
            session.rollback()
