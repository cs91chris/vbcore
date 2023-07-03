import typing as t
from functools import cached_property, partial

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from vbcore import json
from vbcore.crypto.base import Hasher
from vbcore.crypto.factory import CryptoFactory
from vbcore.misc import get_uuid
from vbcore.types import StrDict

if t.TYPE_CHECKING:
    hybrid_property = property  # pylint: disable=C0103
else:
    from sqlalchemy.ext.hybrid import hybrid_property


class Column:
    id: t.ClassVar = partial(sa.Column, sa.Integer, primary_key=True)
    uuid: t.ClassVar = partial(
        sa.Column, sa.String(36), primary_key=True, default=lambda: get_uuid
    )
    auto: t.ClassVar = partial(
        sa.Column, sa.Integer, primary_key=True, autoincrement=True
    )
    date_created: t.ClassVar = partial(
        sa.Column, sa.DateTime, server_default=sa.func.now()
    )
    date_updated: t.ClassVar = partial(sa.Column, sa.DateTime, onupdate=sa.func.now())
    description: t.ClassVar = partial(sa.Column, sa.Text(), nullable=True)


class BaseMixin:
    __table__: sa.Table

    def __init__(self, *args, **kwargs):
        """this is here only to remove pycharm warnings"""


class StandardMixin(BaseMixin):
    id = Column.auto()
    created_at = Column.date_created()
    updated_at = Column.date_updated()


class StandardUuidMixin(BaseMixin):
    id = Column.uuid()
    created_at = Column.date_created()
    updated_at = Column.date_updated()


class CatalogMixin(BaseMixin):
    __table_args__ = (sa.UniqueConstraint("code", "type_id"),)

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    code: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    order_id: Mapped[str] = mapped_column(sa.Integer, nullable=True, index=True)
    description: Mapped[str] = mapped_column(sa.Text(), nullable=True)


class UserMixin(StandardMixin):
    _hasher_type: str = "ARGON2"
    _password: Mapped[str] = mapped_column("password", sa.String(128), nullable=False)

    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)

    @cached_property
    def hasher_instance(self) -> Hasher:
        return CryptoFactory.instance(self._hasher_type)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = self.hasher_instance.hash(password)

    def check_password(self, password):
        return self.hasher_instance.verify(self._password, password)


class ExtraMixin(BaseMixin):
    _json_class = json
    _extra: Mapped[str] = mapped_column(sa.Text())  # type: ignore

    @property
    def extra(self) -> t.Dict[str, t.Any]:
        return self._json_class.loads(self._extra) if self._extra else {}

    @extra.setter
    def extra(self, value: t.Optional[StrDict]):
        self._extra = None
        if value is not None:
            self._extra = self._json_class.dumps(value)
