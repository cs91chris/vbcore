from typing import NamedTuple

from vbcore.db.sqla import SQLAConnector, Model, sa, LoaderModel


class UserDTO(NamedTuple):
    id: int
    name: str


class RoleDTO(NamedTuple):
    id: int
    name: str


class Role(LoaderModel):
    __tablename__ = "roles"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(200))

    values = (
        {"id": 1, "name": "ADMIN"},
        {"id": 2, "name": "GUEST"},
    )


class User(Model):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(200))


if __name__ == "__main__":
    connector = SQLAConnector("sqlite://", echo=True)
    with connector.connection() as conn:
        connector.register_loaders(conn, (Role,))
        connector.create_all()
        conn.add_all(
            [
                User(id=1, name="user-1"),
                User(id=2, name="user-2"),
                User(id=3, name="user-3"),
            ]
        )
        roles = (RoleDTO(id=r.id, name=r.name) for r in conn.query(Role).all())
        users = (UserDTO(id=r.id, name=r.name) for r in conn.query(User).all())

    print("\n", *roles, sep="\n")
    print("\n", *users, sep="\n")
