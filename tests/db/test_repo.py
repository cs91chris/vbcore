from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from unittest.mock import ANY

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from vbcore.base import BaseDTO
from vbcore.db.repo import CrudRepo
from vbcore.db.sqla import Model, SQLAConnector


@dataclass
class UserInput(BaseDTO):
    name: str


@dataclass(frozen=True)
class User(BaseDTO):
    id: int
    name: str
    created_at: Optional[datetime] = field(repr=False, default=None)


class UserOrm(Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, server_default=sa.func.now()
    )


class UserRepo(CrudRepo[UserInput, User]):
    pass


def test_crud():
    user_t = UserOrm
    connector = SQLAConnector("sqlite+pysqlite:///:memory:", echo=True)
    connector.create_all()

    connection = connector.engine.connect()
    base_query = sa.select(user_t.id, user_t.name, user_t.created_at)

    repo = UserRepo(connection, User, user_t)
    repo.mutator.insert_many(
        [
            UserInput(name="pippo"),
            UserInput(name="pluto"),
            UserInput(name="paperino"),
        ]
    )
    repo.mutator.insert(UserInput(name="who"))
    records = repo.querier.query(base_query)
    assert list(records) == [
        User(id=1, name="pippo", created_at=ANY),
        User(id=2, name="pluto", created_at=ANY),
        User(id=3, name="paperino", created_at=ANY),
        User(id=4, name="who", created_at=ANY),
    ]

    repo.mutator.update(user_t.id == 4, name="what")
    record = repo.querier.query(base_query.where(user_t.id == 4))
    assert list(record) == [User(id=4, name="what", created_at=ANY)]

    repo.mutator.delete(user_t.id == 4)
    records = repo.querier.query(base_query)
    assert list(records) == [
        User(id=1, name="pippo", created_at=ANY),
        User(id=2, name="pluto", created_at=ANY),
        User(id=3, name="paperino", created_at=ANY),
    ]
