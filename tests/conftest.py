from typing import cast
from unittest.mock import MagicMock

import pytest

from vbcore.sftp import SFTPHandler, SFTPOptions


@pytest.fixture()
def sftp_handler() -> MagicMock:
    handler = SFTPHandler(SFTPOptions(host="localhost", port=25, user="user"))
    handler.sftp = MagicMock()
    handler.transport = MagicMock()
    handler.transport.is_active.return_value = True
    return cast(MagicMock, handler)
