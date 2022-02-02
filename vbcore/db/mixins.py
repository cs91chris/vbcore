import typing as t
from functools import partial

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.ext.declarative import declared_attr

from vbcore import json
from vbcore.crypto.argon import Argon2
from vbcore.crypto.base import Hasher

if t.TYPE_CHECKING:
    hybrid_property = property  # pylint: disable=C0103
else:
    from sqlalchemy.ext.hybrid import hybrid_property


class BaseMixin:
    __table__ = None

    def __init__(self, *args, **kwargs):
        """this is here only to remove pycharm warnings"""


class StandardMixin(BaseMixin):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, onupdate=sa.func.now())


class CatalogMixin(BaseMixin):
    @declared_attr
    def __table_args__(self):
        return (sa.UniqueConstraint("label", "type_id"),)

    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.String(100))
    type_id = sa.Column(sa.Integer)
    description = sa.Column(sa.String(250))

    def __str__(self):
        return str(self.label)


class CatalogXMixin(CatalogMixin):
    @declared_attr
    def __table_args__(self):
        return (sa.UniqueConstraint("code", "type_id"),)

    code = sa.Column(sa.String(20))
    order_id = sa.Column(sa.Integer, index=True)

    order_by = sa.asc(order_id)

    def __str__(self):
        return f"<{self.code} - {self.label}>"


class LoaderMixin(BaseMixin):
    values: t.Tuple[t.Dict[str, t.Any], ...] = ()

    @classmethod
    def load_values(cls, session):
        session.add_all(cls(**d) for d in cls.values)
        session.commit()

    @classmethod
    def register_loader(cls, session):
        event.listen(cls.__table__, "after_create", partial(cls.load_values, session))


class UserMixin(StandardMixin):
    _hasher_class: t.Type[Hasher] = Argon2
    _password = sa.Column("password", sa.String(128), nullable=False)

    email = sa.Column(sa.String(255), unique=True, nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = self._hasher_class().hash(password)

    def check_password(self, password):
        return self._hasher_class().verify(self._password, password)


class ExtraMixin(BaseMixin):
    _json_class = json
    _extra = sa.Column(sa.Text())

    @hybrid_property
    def extra(self) -> t.Dict[str, t.Any]:
        return self._json_class.loads(self._extra) if self._extra else {}

    @extra.setter
    def extra(self, value: t.Optional[t.Dict[str, t.Any]]):
        self._extra = None
        if value:
            self._extra = self._json_class.dumps(value)
