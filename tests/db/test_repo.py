from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from unittest.mock import ANY

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from vbcore.base import BaseDTO
from vbcore.db.base import Func, Model, SQLAConnector
from vbcore.db.repo import CrudRepo, MutatorRepo, QuerierRepo
from vbcore.tester.asserter import Asserter


@dataclass(frozen=True, kw_only=True)
class UserInput(BaseDTO):
    name: str


@dataclass(frozen=True, kw_only=True)
class User(BaseDTO):
    id: int
    name: str
    created_at: Optional[datetime] = field(repr=False, default=None)


class UserOrm(Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, server_default=Func.NOW())


class UserQuerierRepo(QuerierRepo[User]):
    pass


class UserMutatorRepo(MutatorRepo[UserInput]):
    pass


class UserRepo(CrudRepo[UserInput, User]):
    pass


def test_querier_fetch(connector: SQLAConnector) -> None:
    connector.create_all()

    connection = connector.engine.connect()
    repo = UserQuerierRepo(connection, User)
    repo.execute(
        sa.insert(UserOrm),
        [
            UserInput(name="topolino").to_dict(),
            UserInput(name="pippo").to_dict(),
            UserInput(name="pluto").to_dict(),
            UserInput(name="paperino").to_dict(),
        ],
    )

    records = list(
        repo.fetch(
            table=UserOrm,
            columns=(UserOrm.id, UserOrm.name),
            clauses=(UserOrm.name.like("p%"),),
        )
    )
    Asserter.assert_equals(
        records,
        [
            User(id=2, name="pippo", created_at=None),
            User(id=3, name="pluto", created_at=None),
            User(id=4, name="paperino", created_at=None),
        ],
    )


def test_crud_perform(connector: SQLAConnector) -> None:
    user_t = UserOrm
    connector.create_all()

    connection = connector.engine.connect()
    repo = UserRepo(connection, User, user_t)
    repo.mutator.insert_many(
        [
            UserInput(name="pippo"),
            UserInput(name="pluto"),
            UserInput(name="paperino"),
        ]
    )

    repo.create(UserInput(name="who"))
    record = repo.get(id=4)
    Asserter.assert_equals(record, User(id=4, name="who", created_at=ANY))

    repo.update(user_t.id == 4, name="what")
    records = repo.get_all(id=4)
    Asserter.assert_equals(list(records), [User(id=4, name="what", created_at=ANY)])

    repo.delete(user_t.id == 4)
    records = repo.get_all()
    Asserter.assert_equals(
        list(records),
        [
            User(id=1, name="pippo", created_at=ANY),
            User(id=2, name="pluto", created_at=ANY),
            User(id=3, name="paperino", created_at=ANY),
        ],
    )
