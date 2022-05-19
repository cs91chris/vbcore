# based on https://github.com/enricobarzetti/sqlalchemy_get_or_create
import contextlib
import typing as t

from sqlalchemy import create_engine, inspect, tuple_
from sqlalchemy.exc import IntegrityError, NoResultFound as NoResultError
from sqlalchemy.orm import Query, Session
from sqlalchemy.sql import text as text_sql

from vbcore.db.events import register_engine_events
from vbcore.db.sqla import Model


class SQLASupport:
    def __init__(self, model: Model, session: Session, commit: bool = True):
        """

        :param model: a model class
        :param session: a session object
        """
        self.session = session
        self.model = model
        self._commit = commit

    @contextlib.contextmanager
    def transaction(self):
        try:
            yield self
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _prepare_params(defaults: t.Optional[dict] = None, **kwargs) -> dict:
        """

        :param defaults: overrides kwargs
        :param kwargs: overridden by defaults
        :return: merge of kwargs and defaults
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

        :param lookup: attributes used to find record
        :param params: attributes used to create record
        :param lock: flag used for atomic update
        :return:
        """
        obj = self.model(**params)
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
            else:
                return obj, True

    def get_or_create(
        self, defaults: t.Optional[dict] = None, **kwargs
    ) -> t.Tuple[t.Any, bool]:
        """

        :param defaults: attribute used to create record
        :param kwargs: filters used to fetch record or create
        :return:
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

        :param defaults: attribute used to create record
        :param kwargs: filters used to fetch record or create
        :return:
        """
        defaults = defaults or {}
        with self.session.begin_nested():
            try:
                query = self.fetch().with_for_update()
                obj = query.filter_by(**kwargs).one()
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

    def delete(self, *args, synchronize_session: str = "evaluate", **kwargs) -> int:
        row_count = self.fetch(*args, **kwargs).delete(synchronize_session)
        if self._commit:
            self.session.commit()
        return row_count

    def bulk_insert(self, records: t.Iterable[Model]):
        self.session.add_all(records)
        if self._commit:
            self.session.commit()

    def get_primary_key(self, record: t.Optional[Model] = None) -> t.Tuple:
        return tuple(
            getattr(record or self.model, pk_item.name)
            for pk_item in inspect(self.model).primary_key
        )

    def bulk_upsert(self, records: t.Iterable[Model]):
        db_objects = {}
        for record in records:
            db_objects[self.get_primary_key(record)] = record

        self.delete(
            tuple_(*self.get_primary_key()).in_(list(db_objects.keys())),
            synchronize_session="fetch",
        )

        self.session.flush()
        self.session.add_all(list(db_objects.values()))
        if self._commit:
            self.session.commit()

    @staticmethod
    def register_events(engine):
        register_engine_events(engine)

    @staticmethod
    def exec_from_file(
        url: str,
        filename: str,
        echo: bool = False,
        separator: str = ";\n",
        skip_line_prefixes: tuple = ("--",),
    ):
        engine = create_engine(url, echo=echo)
        with engine.connect() as conn, open(filename, encoding="utf-8") as f:
            for statement in f.read().split(separator):
                for skip_line in skip_line_prefixes:
                    if statement.startswith(skip_line):
                        break
                else:
                    conn.execute(text_sql(statement))
