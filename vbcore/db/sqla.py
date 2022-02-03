import typing as t
from contextlib import contextmanager
from functools import partial

import sqlalchemy as sa
import sqlalchemy.exc
from sqlalchemy import event
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker, Session

from vbcore.datastruct import ObjectDict

SessionType = t.Union[scoped_session, Session]
LoadersType = t.Tuple[t.Type["LoaderModel"], ...]


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

    @staticmethod
    def register_loaders(session: SessionType, loaders: LoadersType):
        def _load_values(loader_class: "LoaderModel", *_, **__):
            try:
                # noinspection PyCallingNonCallable
                session.add_all(loader_class(**d) for d in loader_class.values)
                session.commit()
            except sqlalchemy.exc.SQLAlchemyError:
                session.rollback()

        for loader in loaders:
            callback = partial(_load_values, loader)
            event.listen(loader.__table__, "after_create", callback)

    def create_all(self, loaders: LoadersType = ()):
        if loaders:
            with self.connection() as session:
                self.register_loaders(session, loaders)
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


class LoaderModel(Model):  # type: ignore
    __abstract__ = True

    values: t.Tuple[t.Dict[str, t.Any], ...] = ()
