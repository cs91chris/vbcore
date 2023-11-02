from dataclasses import dataclass

import pytest
import sqlalchemy as sa

from vbcore.base import BaseDTO
from vbcore.db.base import Model
from vbcore.tester.asserter import Asserter


@dataclass(frozen=True, kw_only=True)
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
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_create_all():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_get_session():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_connection():
    """TODO implement me"""


@pytest.mark.skip("implement me")
def test_transaction():
    """TODO implement me"""
