from dataclasses import dataclass

import pytest
import sqlalchemy as sa

from vbcore.base import BaseDTO
from vbcore.db.sqla import Model
from vbcore.tester.asserter import Asserter


@dataclass
class SampleDTO(BaseDTO):
    id: int  # pylint: disable=invalid-name
    name: str


class Sample(Model):
    __tablename__ = "sample"
    dto_class = SampleDTO

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text())


def test_model_from_dto():
    record = Sample.from_dto(SampleDTO(id=1, name="name"))
    Asserter.assert_equals(record.id, 1)
    Asserter.assert_equals(record.name, "name")


def test_model_to_dto():
    dto = Sample(id=1, name="name")
    Asserter.assert_equals(dto.to_dto(), SampleDTO(id=1, name="name"))


def test_model_to_dict():
    Asserter.assert_equals(
        Sample(id=1, name="name").to_dict(),
        {"id": 1, "name": "name"},
    )


@pytest.mark.skip("implement me")
def test_connector_register_loaders():
    pass


@pytest.mark.skip("implement me")
def test_create_all():
    pass


@pytest.mark.skip("implement me")
def test_get_session():
    pass


@pytest.mark.skip("implement me")
def test_connection():
    pass


@pytest.mark.skip("implement me")
def test_transaction():
    pass
