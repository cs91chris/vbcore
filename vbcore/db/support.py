import typing as t

from sqlalchemy import create_engine, inspect, tuple_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session
from sqlalchemy.orm.exc import NoResultFound as NoResultError
from sqlalchemy.sql import text as text_sql

from vbcore.db.events import ErrorsHandler
from vbcore.db.sqla import Model
from vbcore.db.views import DDLViewCompiler
from vbcore.files import FileHandler
from vbcore.types import StrTuple

SynchronizeSessionArgument = t.Literal[False, "auto", "evaluate", "fetch"]


class SQLASupport:
    def __init__(self, model: t.Type[Model], session: Session, commit: bool = True):
        """
        @param model: a model class
        @param session: a session object
        @param commit: enable auto commit
        """
        self.session = session
        self.model = model
        self._commit = commit

    @staticmethod
    def _prepare_params(defaults: t.Optional[dict] = None, **kwargs) -> dict:
        """
        @param defaults: overrides kwargs
        @param kwargs: overridden by defaults
        @return merge of kwargs and defaults
        """
        ret = {}
        defaults = defaults or {}
        ret.update(kwargs)
        ret.update(defaults)
        return ret

    def _create_object(
        self, lookup: dict, params: dict, lock: bool = False
    ) -> t.Tuple[t.Any, bool]:
        """
        @param lookup: attributes used to find record
        @param params: attributes used to create record
        @param lock: flag used for atomic update
        @return created object and is_created flag
        """
        obj = self.model(**params)  # type: ignore
        self.session.add(obj)

        with self.session.begin_nested():
            try:
                self.session.flush()
            except IntegrityError:
                self.session.rollback()
                query = self.fetch(**lookup)
                if lock:
                    query = query.with_for_update()
                    obj = query.one()
                return obj, False
            return obj, True

    def get_or_create(
        self, defaults: t.Optional[dict] = None, **kwargs
    ) -> t.Tuple[t.Any, bool]:
        """
        @param defaults: attribute used to create record
        @param kwargs: filters used to fetch record or create
        @return created object and is_created flag
        """
        try:
            return self.fetch(**kwargs).one(), False
        except NoResultError:
            params = self._prepare_params(defaults, **kwargs)
            return self._create_object(kwargs, params)

    def update_or_create(
        self, defaults: t.Optional[dict] = None, **kwargs
    ) -> t.Tuple[t.Any, bool]:
        """
        @param defaults: attribute used to create record
        @param kwargs: filters used to fetch record or create
        @return updated object and is_created flag
        """
        defaults = defaults or {}
        with self.session.begin_nested():
            try:
                query = self.fetch().with_for_update()
                obj = query.filter_by(**kwargs).one()  # type: ignore
            except NoResultError:
                params = self._prepare_params(defaults, **kwargs)
                obj, created = self._create_object(kwargs, params, lock=True)
                if created:
                    return obj, created

            for k, v in defaults.items():
                setattr(obj, k, v)

            self.session.merge(obj)
            self.session.flush()

        return obj, False

    def fetch(self, *args, fields: tuple = (), **kwargs) -> Query:
        columns = fields or (self.model,)
        return self.session.query(*columns).filter(*args).filter_by(**kwargs)

    def delete(
        self, *args, synchronize: SynchronizeSessionArgument = "evaluate", **kwargs
    ) -> int:
        row_count = self.fetch(*args, **kwargs).delete(synchronize)
        if self._commit:
            self.session.commit()
        return row_count

    def bulk_insert(self, records: t.Iterable[Model]) -> None:
        self.session.add_all(records)
        if self._commit:
            self.session.commit()

    def get_primary_key(self, record: t.Optional[Model] = None) -> t.Tuple:
        return tuple(
            getattr(record or self.model, pk_item.name)
            for pk_item in inspect(self.model).primary_key  # type: ignore
        )

    def bulk_upsert(self, records: t.Iterable[Model]) -> None:
        entities = {self.get_primary_key(record): record for record in records}

        pk_cols = self.get_primary_key()
        pk_values = list(entities.keys())
        self.delete(tuple_(*pk_cols).in_(pk_values), synchronize="fetch")

        self.session.flush()
        self.session.add_all(list(entities.values()))
        if self._commit:
            self.session.commit()

    @classmethod
    def register_custom_handlers(cls, engine) -> None:
        ErrorsHandler.register(engine)
        DDLViewCompiler().register()

    @classmethod
    def exec_from_file(
        cls,
        url: str,
        filename: str,
        echo: bool = False,
        separator: str = ";\n",
        skip_line_prefixes: StrTuple = ("--",),
    ) -> None:
        engine = create_engine(url, echo=echo)
        with engine.connect() as conn, FileHandler().open(filename) as f:
            for statement in f.read().split(separator):
                for prefix in skip_line_prefixes:
                    if statement.startswith(prefix):
                        break
                else:
                    conn.execute(text_sql(statement))
