# pylint: disable=redefined-outer-name

import pytest

from vbcore.misc import get_uuid


@pytest.fixture(scope="session")
def session_id():
    return get_uuid()
