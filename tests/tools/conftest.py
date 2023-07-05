import os

import pytest
from click.testing import CliRunner


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture
def sendmail_envvar(monkeypatch):
    monkeypatch.setitem(os.environ, "SMTP_HOST", "localhost")
    monkeypatch.setitem(os.environ, "SMTP_PORT", "22")
    monkeypatch.setitem(os.environ, "SMTP_USER", "user")
    monkeypatch.setitem(os.environ, "SMTP_PASSWORD", "password")
    monkeypatch.setitem(os.environ, "SMTP_SENDER", "sender@mail.com")
    monkeypatch.setitem(os.environ, "SMTP_IS_SSL", "1")


@pytest.fixture
def sftp_envvar(monkeypatch):
    monkeypatch.setitem(os.environ, "FTP_HOST", "localhost")
    monkeypatch.setitem(os.environ, "FTP_PORT", "22")
    monkeypatch.setitem(os.environ, "FTP_USER", "user")
    monkeypatch.setitem(os.environ, "FTP_PASSWORD", "password")
