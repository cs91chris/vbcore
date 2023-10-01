import typing as t
from contextlib import contextmanager
from functools import partial

import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, Session, sessionmaker

from ..loggers import VBLoggerMixin
from ..types import OptDict
from .events import ErrorsHandler, Listener
from .types import SessionType
from .views import DDLViewCompiler

if t.TYPE_CHECKING:
    from .base import LoadersType


class SQLAConnector(VBLoggerMixin):
    metadata = sa.MetaData()
    views_metadata = sa.MetaData()
    session_class = scoped_session

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        str_conn: str,
        session_options: OptDict = None,
        echo: bool = False,
        connect_args: OptDict = None,
        execution_options: OptDict = None,
        pool_pre_ping: bool = False,
        pool_size: int = 5,
        session_class: type = Session,
        autoflush: bool = True,
        autocommit: bool = False,
        expire_on_commit: bool = True,
        custom_handlers: bool = True,
        **kwargs,
    ):
        self._session_options = session_options or {}
        self._session_options.setdefault("class_", session_class)
        self._session_options.setdefault("autoflush", autoflush)
        self._session_options.setdefault("autocommit", autocommit)
        self._session_options.setdefault("expire_on_commit", expire_on_commit)
        self._factory: t.Optional[sessionmaker] = None

        self._fix_loggers(echo)

        self.engine = sa.create_engine(
            url=str_conn,
            echo=echo,
            connect_args=connect_args or {},
            execution_options=execution_options,
            pool_pre_ping=pool_pre_ping,
            pool_size=pool_size,
            **kwargs,
        )

        if custom_handlers:
            self.register_custom_handlers()

    def register_custom_handlers(self):
        ErrorsHandler.register(self.engine)
        DDLViewCompiler().register()

    def _fix_loggers(self, echo: bool):
        """customize what echo flag means for logging"""
        if echo is True:
            self.logger("sqlalchemy.pool").setLevel("DEBUG")
            self.logger("sqlalchemy.engine.Engine").handlers.clear()

    @classmethod
    def register_loaders(cls, session: SessionType, loaders: "LoadersType") -> None:
        for loader in loaders:
            callback = partial(loader.load_values, session)
            Listener.register_after_create(loader.__table__, callback)

    def create_all(self, loaders: "LoadersType" = ()) -> None:
        if loaders:
            with self.connection() as session:
                self.register_loaders(session, loaders)
        self.metadata.create_all(self.engine)

    def drop_all(self) -> None:
        self.metadata.drop_all(self.engine)

    def get_session(self, **options) -> SessionType:
        if options:
            return self.session_class(sessionmaker(self.engine, **options))
        if self._factory is None:
            self._factory = sessionmaker(self.engine, **self._session_options)
        return self.session_class(self._factory)

    @contextmanager
    def connection(self, **options) -> t.Generator[SessionType, None, None]:
        session = self.get_session(**options)
        try:
            yield session
        finally:
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
