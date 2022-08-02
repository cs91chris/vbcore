from vbcore.db.sqla import SQLAConnector


def executor(str_conn: str, statement, echo=True):
    with SQLAConnector(str_conn, echo=echo).connection() as session:
        return session.execute(statement).all()


if __name__ == "__main__":
    records = executor(
        str_conn="sqlite://",
        statement="select 1",
    )
    print(records)
