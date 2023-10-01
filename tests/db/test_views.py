from dataclasses import dataclass

import pytest
import sqlalchemy as sa

from vbcore.base import BaseDTO
from vbcore.db.base import ViewModel
from vbcore.db.exceptions import DBNonExistentTable
from vbcore.db.views import DDLCreateView
from vbcore.tester.asserter import Asserter


@dataclass
class SampleDTO(BaseDTO):
    id: int  # pylint: disable=invalid-name
    name: str


class SampleModel(ViewModel):
    __tablename__ = "sample_view"
    dto_class = SampleDTO

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


def test_create_view(connector, support):
    view_name = "sample_view"
    support.register_custom_handlers(connector.engine)

    select = sa.select(
        sa.literal_column("1").label("id"),
        sa.literal_column("'name'").label("name"),
    )
    DDLCreateView(name=view_name, metadata=connector.metadata, select=select)

    connector.create_all()
    with connector.connection() as session:
        result = session.query(SampleModel).all()

    Asserter.assert_equals(
        [record.to_dto() for record in result],
        [SampleModel(id=1, name="name").to_dto()],
    )

    connector.drop_all()
    with connector.connection() as session:
        with pytest.raises(DBNonExistentTable) as error:
            session.query(SampleModel).all()

        Asserter.assert_equals(error.value.table, view_name)
