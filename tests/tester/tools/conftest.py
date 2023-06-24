import pytest
from click.testing import CliRunner


@pytest.fixture(scope="session")
def runner():
    return CliRunner()
