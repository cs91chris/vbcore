import logging
import typing as t
from contextlib import contextmanager
from dataclasses import make_dataclass
from functools import partial

import sqlalchemy as sa
import sqlalchemy.exc
from sqlalchemy.orm import declarative_base  # type: ignore
from sqlalchemy.orm import scoped_session, Session, sessionmaker

from vbcore.datastruct import BaseDTO

from .events import Listener

SessionType = t.Union[scoped_session, Session]
LoadersType = t.Tuple[t.Type["LoaderModel"], ...]

logger = logging.getLogger(__name__)


class BaseModel:
    __table__ = None
    dto_class = None

    def columns(self) -> t.Tuple[str, ...]:
        if self.__table__ is None:
            return ()
        return tuple(self.__table__.columns.keys())

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {col: getattr(self, col, None) for col in self.columns()}

    # noinspection PyArgumentList
    @classmethod
    def from_dto(cls, dto):
        if isinstance(dto, BaseDTO):
            return cls(**dto.to_dict())
        return cls(**dto)

    def to_dto(self):
        items = tuple((col, getattr(self, col, None)) for col in self.columns())
        dto_class = self.dto_class
        if self.dto_class is None:
            dto_class = make_dataclass(
                f"{self.__class__.__name__}DTO",
                [(col, type(value)) for col, value in items],
                bases=(BaseDTO,),
                frozen=True,
            )
        return dto_class(**dict(items))


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
        for loader in loaders:
            callback = partial(loader.load_values, session)
            Listener.register_after_create(loader.__table__, callback)

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

    @contextmanager
    def transaction(self, **options) -> t.Generator[SessionType, None, None]:
        with self.connection(**options) as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise


Model = declarative_base(
    metadata=SQLAConnector.metadata,
    cls=BaseModel,
    name=BaseModel.__name__,
)


class LoaderModel(Model):  # type: ignore
    __abstract__ = True

    values: t.Tuple[t.Dict[str, t.Any], ...] = ()

    @classmethod
    def load_values(cls, session: Session, *_, **__):
        try:
            session.add_all(cls(**d) for d in cls.values)
            session.commit()
        except sqlalchemy.exc.SQLAlchemyError as exc:
            logger.exception(exc)
            session.rollback()
