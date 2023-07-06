from functools import partial
from unittest.mock import ANY, MagicMock, patch

from vbcore.net.ftpclient.legacy import FTPHandler, FTPOptions
from vbcore.tester.asserter import Asserter

patch_ftp_client = partial(patch, "vbcore.net.ftpclient.legacy.FTP")


def prepare_handler(mock_ftp):
    ftp_instance = MagicMock()
    ftp_instance.__enter__.return_value = ftp_instance
    mock_ftp.return_value = ftp_instance
    handler = FTPHandler(FTPOptions(host="localhost", port=21, user="user"))
    return handler, ftp_instance


@patch_ftp_client()
def test_connect(mock_ftp):
    handler, ftp_instance = prepare_handler(mock_ftp)

    with handler.connect() as conn:
        Asserter.assert_is(conn, ftp_instance)

    mock_ftp.assert_called_once_with(timeout=300, encoding="utf-8")
    ftp_instance.connect.assert_called_once_with("localhost", 21)
    ftp_instance.login.assert_called_once_with("user", "")


@patch_ftp_client()
def test_download_file(mock_ftp, tmpdir):
    handler, ftp_instance = prepare_handler(mock_ftp)
    local_file = tmpdir.join("local.txt")

    handler.download_file("remote.txt", local_file)
    ftp_instance.retrbinary.assert_called_once_with("RETR remote.txt", ANY)


@patch_ftp_client()
def test_upload_file(mock_ftp, tmpdir):
    handler, ftp_instance = prepare_handler(mock_ftp)
    local_file = tmpdir.join("local.txt")
    local_file.write("")

    handler.upload_file(local_file, "remote.txt")
    ftp_instance.storbinary.assert_called_once_with("STOR remote.txt", ANY)
