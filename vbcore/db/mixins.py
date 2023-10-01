from datetime import datetime
from functools import cached_property
from typing import Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from vbcore import json
from vbcore.crypto.base import Hasher
from vbcore.crypto.factory import CryptoFactory
from vbcore.db.base import Column, StrCol
from vbcore.types import StrDict

if TYPE_CHECKING:
    hybrid_property = property  # pylint: disable=C0103
else:
    from sqlalchemy.ext.hybrid import hybrid_property


class UuidMixin:
    id: Mapped[str] = Column.uuid()


class IdAutoMixin:
    id: Mapped[int] = Column.auto()


class DateMixin:
    created_at: Mapped[datetime] = Column.date_created()
    updated_at: Mapped[Optional[datetime]] = Column.date_updated()

    @hybrid_property
    def last_update(self) -> datetime:
        return self.updated_at or self.created_at


class CatalogMixin:
    __table_args__ = (sa.UniqueConstraint("code", "type_id"),)

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    code: Mapped[str] = mapped_column(StrCol.small, nullable=False)
    order_id: Mapped[str] = mapped_column(sa.Integer, nullable=True, index=True)
    description: Mapped[str] = mapped_column(sa.Text(), nullable=True)


class UserMixin(UuidMixin, DateMixin):
    _hasher_type: str = "ARGON2"
    _password: Mapped[str] = mapped_column("password", StrCol.medium, nullable=False)

    email: Mapped[str] = mapped_column(StrCol.medium, unique=True, nullable=False)

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


class ExtraMixin:
    _json_class = json
    _extra: Mapped[str] = mapped_column(sa.Text())  # type: ignore

    @property
    def extra(self) -> StrDict:
        return self._json_class.loads(self._extra) if self._extra else {}

    @extra.setter
    def extra(self, value: Optional[StrDict]):
        self._extra = None
        if value is not None:
            self._extra = self._json_class.dumps(value)
