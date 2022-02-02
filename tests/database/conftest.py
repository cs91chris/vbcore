import pytest
import sqlalchemy as sa

from vbcore.db.sqla import Model, SQLAConnector
from vbcore.db.support import SQLASupport


class User(Model):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(200), unique=True)
    description = sa.Column(sa.Text())


def db_session(conn):
    with conn.connection() as session:
        session.execute("PRAGMA case_sensitive_like=ON;")
        conn.create_all()
        return session


@pytest.fixture(scope="function")
def sample_model():
    return User


@pytest.fixture()
def connector():
    return SQLAConnector("sqlite://", echo=True)


@pytest.fixture(scope="function")
def local_session(connector):  # pylint: disable=redefined-outer-name
    return db_session(connector)


@pytest.fixture()
def session_save(local_session):  # pylint: disable=redefined-outer-name
    def _save(items):
        for i in items:
            local_session.merge(i)
        local_session.commit()

    return _save


@pytest.fixture()
def support(sample_model, local_session):  # pylint: disable=redefined-outer-name
    return SQLASupport(model=sample_model, session=local_session)
