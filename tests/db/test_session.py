import sqlalchemy as sa

from vbcore.db.base import LoaderModel
from vbcore.tester.asserter import Asserter


def test_connection(local_session):
    cursor = local_session.execute(sa.text("SELECT 1"))
    Asserter.assert_equals(list(cursor), [(1,)])


def test_model(local_session, session_save, sample_model):
    session_save(
        (
            sample_model(id=1, name="user-1"),
            sample_model(id=2, name="user-2"),
            sample_model(id=3, name="user-3"),
        )
    )
    Asserter.assert_equals(len(local_session.query(sample_model).all()), 3)


def test_loaders(connector):
    class SampleLoader(LoaderModel):
        __tablename__ = "sample_loader"

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String(200), unique=True)

        values = (
            {"id": 1, "name": "name-1"},
            {"id": 2, "name": "name-2"},
            {"id": 3, "name": "name-3"},
        )

    connector.create_all(loaders=(SampleLoader,))
    with connector.connection() as session:
        Asserter.assert_equals(len(session.query(SampleLoader).all()), 3)
