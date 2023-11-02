import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from vbcore.db.base import Model
from vbcore.db.exceptions import DBDuplicateEntry
from vbcore.db.mixins import CatalogMixin, ExtraMixin
from vbcore.tester.asserter import Asserter


class SampleExtraModel(Model, ExtraMixin):
    __tablename__ = "sample_extra_model"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)


class SampleCatalogModel(Model, CatalogMixin):
    __tablename__ = "sample_catalog_model"


def test_extra_mixin(local_session, session_save):
    extra_info = {"a": 1, "b": 2}

    session_save([SampleExtraModel(id=1, extra=extra_info)])
    record = local_session.query(SampleExtraModel).one()
    Asserter.assert_equals(record.extra, extra_info)


def test_catalog_mixin_constraint(support):
    with pytest.raises(DBDuplicateEntry) as error:
        support.bulk_insert(
            [
                SampleCatalogModel(id=1, type_id=1, code="001"),
                SampleCatalogModel(id=2, type_id=2, code="001"),
                SampleCatalogModel(id=3, type_id=1, code="001"),
            ]
        )
    support.session.rollback()

    Asserter.assert_equals(error.value.error_type, "DBDuplicateEntry")
    Asserter.assert_equals(error.value.columns, ["code", "type_id"])
    Asserter.assert_equals(error.value.value, None)
