import pytest
import sqlalchemy as sa

from vbcore.db.exceptions import DBDuplicateEntry
from vbcore.db.mixins import CatalogMixin, ExtraMixin
from vbcore.db.sqla import Model
from vbcore.tester.mixins import Asserter


class SampleExtraModel(Model, ExtraMixin):
    __tablename__ = "sample_extra_model"

    id = sa.Column(sa.Integer, primary_key=True)


class SampleCatalogModel(Model, CatalogMixin):
    __tablename__ = "sample_catalog_model"


def test_extra_mixin(local_session, session_save):
    extra_info = {"a": 1, "b": 2}

    session_save([SampleExtraModel(id=1, extra=extra_info)])
    record = local_session.query(SampleExtraModel).one()
    Asserter.assert_equals(record.extra, extra_info)


def test_catalog_mixin_constraint(connector, support):
    support.register_events(connector.engine)
    with pytest.raises(DBDuplicateEntry) as error:
        support.bulk_insert(
            [
                SampleCatalogModel(id=1, type_id=1, code="001"),
                SampleCatalogModel(id=2, type_id=2, code="001"),
                SampleCatalogModel(id=3, type_id=1, code="001"),
            ]
        )
    support.session.rollback()

    Asserter.assert_equals(
        error.value.as_dict(),
        {"error": "DBDuplicateEntry", "columns": ["code", "type_id"], "value": None},
    )
