from typing import NamedTuple

from vbcore.db.sqla import SQLAConnector, Model, sa


class UserDTO(NamedTuple):
    id: int
    name: str


class User(Model):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(200))


if __name__ == "__main__":
    connector = SQLAConnector("sqlite://", echo=True)
    connector.create_all()
    with connector.connection() as conn:
        conn.add_all(
            [
                User(id=1, name="user-1"),
                User(id=2, name="user-2"),
                User(id=3, name="user-3"),
            ]
        )
        users = (UserDTO(id=r.id, name=r.name) for r in conn.query(User).all())

    print(*users, sep="\n")
