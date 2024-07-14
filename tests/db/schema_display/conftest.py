import pytest
from sqlalchemy import MetaData
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base


@pytest.fixture
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def metadata(engine):  # pylint: disable=redefined-outer-name
    _metadata = MetaData()
    _metadata.reflect(engine)
    return _metadata


@pytest.fixture
def base_model(metadata):  # pylint: disable=redefined-outer-name
    return declarative_base(metadata=metadata)
