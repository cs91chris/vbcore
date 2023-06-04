import pytest

from vbcore.data.transformations.builders.factory import BuilderEnum, BuilderFactory


@pytest.fixture
def json_builder():
    return BuilderFactory.instance(BuilderEnum.JSON)


@pytest.fixture
def xml_builder():
    return BuilderFactory.instance(BuilderEnum.XML)


@pytest.fixture
def html_builder():
    return BuilderFactory.instance(BuilderEnum.HTML)


@pytest.fixture
def csv_builder():
    return BuilderFactory.instance(BuilderEnum.CSV)


@pytest.fixture
def yaml_builder():
    return BuilderFactory.instance(BuilderEnum.YAML)
