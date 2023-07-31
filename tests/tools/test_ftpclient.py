import re
from unittest.mock import MagicMock, patch

from vbcore.net.ftpclient.legacy import FTPOptions
from vbcore.net.ftpclient.sftp import SFTPOptions
from vbcore.tester.asserter import Asserter
from vbcore.tools.entrypoint import main


@patch("vbcore.tools.ftpclient.SFTPHandler")
def test_sftp_download(mock_sftp, runner, ftp_envvar):
    _ = ftp_envvar
    mock_instance = MagicMock()
    mock_sftp.return_value = mock_instance

    result = runner.invoke(
        main,
        [
            "ftpclient",
            "download",
            "--ssh",
            "-r",
            "remote.txt",
            "-l",
            "local.txt",
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_sftp.assert_called_once_with(
        SFTPOptions(
            host="localhost",
            port=22,
            user="user",
            password="password",
            private_key_file=None,
            key_type="RSA",
        )
    )
    mock_instance.download_file.assert_called_once_with("remote.txt", "local.txt")


@patch("vbcore.tools.ftpclient.SFTPHandler")
def test_sftp_upload(mock_sftp, runner, ftp_envvar, tmpdir):
    _ = ftp_envvar
    mock_instance = MagicMock()
    mock_sftp.return_value = mock_instance

    local = tmpdir.join("local.txt")
    local_file = f"{local.dirname}/{local.basename}"
    local.write("")

    result = runner.invoke(
        main,
        [
            "ftpclient",
            "upload",
            "--ssh",
            "-r",
            "remote.txt",
            "-l",
            local_file,
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_sftp.assert_called_once_with(
        SFTPOptions(
            host="localhost",
            port=22,
            user="user",
            password="password",
            private_key_file=None,
            key_type="RSA",
        )
    )
    mock_instance.upload_file.assert_called_once_with(local_file, "remote.txt")


@patch("vbcore.tools.ftpclient.FTPHandler")
def test_ftp_download(mock_ftp, runner, ftp_envvar):
    _ = ftp_envvar
    mock_instance = MagicMock()
    mock_ftp.return_value = mock_instance

    result = runner.invoke(
        main,
        [
            "ftpclient",
            "download",
            "-r",
            "remote.txt",
            "-l",
            "local.txt",
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_ftp.assert_called_once_with(
        FTPOptions(
            host="localhost",
            port=22,
            user="user",
            password="password",
        )
    )
    mock_instance.download_file.assert_called_once_with("remote.txt", "local.txt")


@patch("vbcore.tools.ftpclient.FTPHandler")
def test_ftp_upload(mock_ftp, runner, ftp_envvar, tmpdir):
    _ = ftp_envvar
    mock_instance = MagicMock()
    mock_ftp.return_value = mock_instance

    local = tmpdir.join("local.txt")
    local_file = f"{local.dirname}/{local.basename}"
    local.write("")

    result = runner.invoke(
        main,
        [
            "ftpclient",
            "upload",
            "-r",
            "remote.txt",
            "-l",
            local_file,
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_ftp.assert_called_once_with(
        FTPOptions(
            host="localhost",
            port=22,
            user="user",
            password="password",
        )
    )
    mock_instance.upload_file.assert_called_once_with(local_file, "remote.txt")


@patch("vbcore.tools.ftpclient.SFTPHandler")
def test_sftp_download_dir(mock_sftp, runner, ftp_envvar):
    _ = ftp_envvar
    mock_instance = MagicMock()
    mock_sftp.return_value = mock_instance

    result = runner.invoke(
        main,
        [
            "ftpclient",
            "download-dir",
            "--ssh",
            "-r",
            "/data/remote",
            "--only",
            ".*_ONLY_.*",
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_sftp.assert_called_once_with(
        SFTPOptions(
            host="localhost",
            port=22,
            user="user",
            password="password",
            private_key_file=None,
            key_type="RSA",
        )
    )
    mock_instance.download_dir.assert_called_once_with(
        remote_path="/data/remote",
        local_path=".",
        only=re.compile(".*_ONLY_.*"),
        exclude=None,
    )


@patch("vbcore.tools.ftpclient.SFTPHandler")
def test_sftp_upload_dir(mock_sftp, runner, ftp_envvar):
    _ = ftp_envvar
    mock_instance = MagicMock()
    mock_sftp.return_value = mock_instance

    result = runner.invoke(
        main,
        [
            "ftpclient",
            "upload-dir",
            "--ssh",
            "-r",
            "/data/remote",
            "--exclude",
            ".*_EXCLUDE_.*",
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_sftp.assert_called_once_with(
        SFTPOptions(
            host="localhost",
            port=22,
            user="user",
            password="password",
            private_key_file=None,
            key_type="RSA",
        )
    )
    mock_instance.upload_dir.assert_called_once_with(
        local_path=".",
        remote_path="/data/remote",
        only=None,
        exclude=re.compile(".*_EXCLUDE_.*"),
    )
