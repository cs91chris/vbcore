import typing as t
from contextlib import contextmanager

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker, Session

from vbcore.datastruct import ObjectDict

SessionType = t.Union[scoped_session, Session]


class BaseModel:
    __table__ = None
    dto_class = ObjectDict

    def columns(self) -> t.Tuple[str, ...]:
        if self.__table__ is None:
            return ()
        return tuple(self.__table__.columns.keys())

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {col: getattr(self, col, None) for col in self.columns()}

    def to_dto(self):
        return self.dto_class(**self.to_dict())


class SQLAConnector:
    metadata = sa.MetaData()
    session_class = scoped_session

    def __init__(
        self,
        str_conn: str,
        session_options: t.Optional[dict] = None,
        **kwargs,
    ):
        self.engine = sa.create_engine(str_conn, **kwargs)
        self._session_options = session_options or {}
        self._factory: t.Optional[sessionmaker] = None

    def create_all(self):
        self.metadata.create_all(self.engine)

    def get_session(self, **options) -> SessionType:
        if options:
            return self.session_class(sessionmaker(self.engine, **options))
        if self._factory is None:
            self._factory = sessionmaker(self.engine, **self._session_options)
        return self.session_class(self._factory)

    @contextmanager
    def connection(self, **options) -> t.Generator[SessionType, None, None]:
        session = self.get_session(**options)
        yield session
        session.close()  # pylint: disable=no-member


Model = declarative_base(
    metadata=SQLAConnector.metadata,
    cls=BaseModel,
    name=BaseModel.__name__,
)
