from vbcore.tester.mixins import Asserter


def test_connection(local_session):
    cursor = local_session.execute("SELECT 1")
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
