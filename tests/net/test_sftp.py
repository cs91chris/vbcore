import re
from functools import partial
from unittest.mock import patch

from vbcore.tester.mixins import Asserter

REMOTE_FILE = "remote.txt"
LOCAL_FILE = "local.txt"
REMOTE_DIR = "/remote"

patch_sftp_client = partial(patch, "vbcore.net.sftp.SFTPClient")
patch_sftp_transport = partial(patch, "vbcore.net.sftp.Transport")


@patch_sftp_client()
@patch_sftp_transport()
def test_connect_disconnect(mock_sftp, mock_transport, sftp_handler):
    _ = mock_sftp, mock_transport
    sftp_handler.transport.is_active.return_value = False
    with sftp_handler.context() as conn:
        _ = conn

    sftp_handler.transport.connect.assert_called_once_with(None, "user", None)
    sftp_handler.transport.close.assert_called_once()
    sftp_handler.sftp.close.assert_called_once()


@patch_sftp_client()
@patch_sftp_transport()
def test_download_file(mock_sftp, mock_transport, sftp_handler):
    _ = mock_sftp, mock_transport
    sftp_handler.download_file(REMOTE_FILE, LOCAL_FILE)
    sftp_handler.sftp.get.assert_called_once_with(REMOTE_FILE, LOCAL_FILE)


@patch_sftp_client()
@patch_sftp_transport()
def test_upload_file(mock_sftp, mock_transport, sftp_handler):
    _ = mock_sftp, mock_transport
    sftp_handler.upload_file(LOCAL_FILE, REMOTE_FILE)
    sftp_handler.sftp.put.assert_called_once_with(LOCAL_FILE, REMOTE_FILE)


@patch_sftp_client()
@patch_sftp_transport()
def test_download_dir(mock_sftp, mock_transport, sftp_handler):
    _ = mock_sftp, mock_transport
    sftp_handler.sftp.listdir.return_value = [
        "file_1.txt",
        "file_2.txt",
        "file_3.txt",
    ]

    Asserter.assert_equals(sftp_handler.download_dir(REMOTE_DIR), 3)

    sftp_handler.sftp.listdir.assert_called_once_with(path=REMOTE_DIR)
    sftp_handler.sftp.get.has_calls(
        [
            ("./file_1.txt", "local/file_1.txt"),
            ("./file_2.txt", "local/file_2.txt"),
            ("./file_3.txt", "local/file_3.txt"),
        ]
    )


@patch_sftp_client()
@patch_sftp_transport()
def test_download_dir_exclude(mock_sftp, mock_transport, sftp_handler):
    _ = mock_sftp, mock_transport
    sftp_handler.sftp.listdir.return_value = [
        "file.txt",
        "file.csv",
        "file.bat",
    ]

    Asserter.assert_equals(
        sftp_handler.download_dir(REMOTE_DIR, exclude=re.compile(r".*\.csv")), 2
    )

    sftp_handler.sftp.listdir.assert_called_once_with(path=REMOTE_DIR)
    sftp_handler.sftp.get.has_calls(
        [
            ("./file.txt", "local/file.txt"),
            ("./file.bat", "local/file.bat"),
        ]
    )


@patch_sftp_client()
@patch_sftp_transport()
def test_bulk_download_dir_only(mock_sftp, mock_transport, sftp_handler):
    _ = mock_sftp, mock_transport
    sftp_handler.sftp.listdir.return_value = [
        "file_X_1.txt",
        "file_Y_1.txt",
        "file_X_2.txt",
    ]

    Asserter.assert_equals(
        sftp_handler.download_dir(REMOTE_DIR, only=re.compile(r".*_X_.*")), 2
    )

    sftp_handler.sftp.listdir.assert_called_once_with(path=REMOTE_DIR)
    sftp_handler.sftp.get.has_calls(
        [
            ("./file_X_1.txt", "local/file_X_1.txt"),
            ("./file_X_2.txt", "local/file_X_2.txt"),
        ]
    )
