import functools
import re
from typing import TYPE_CHECKING, Union

import click

from vbcore.datastruct.lazy import LazyImporter
from vbcore.loggers import Log
from vbcore.net.ftpclient.legacy import FTPHandler, FTPOptions
from vbcore.tools.cli import CliInputDir, CliInputFile, CliOpt, CliOutputFile, CliReqOpt

if TYPE_CHECKING:
    from vbcore.net.ftpclient.sftp import SFTPHandler, SFTPOptions
else:
    SFTPHandler, SFTPOptions = LazyImporter.import_many(
        "vbcore.net.ftpclient.sftp:SFTPHandler",
        "vbcore.net.ftpclient.sftp:SFTPOptions",
        message="you must install vbcore[net]",
    )

main = click.Group(name="ftpclient", help="ftp client handler")


def factory(options: dict) -> Union[FTPHandler, SFTPHandler]:
    no_secure = options.pop("no_secure", False)
    if no_secure:
        return FTPHandler(FTPOptions.from_dict(**options))
    return SFTPHandler(SFTPOptions.from_dict(**options))


def common_options(func):
    @CliOpt.flag("--debug", envvar="FTP_DEBUG")
    @CliOpt.integer("--timeout", envvar="FTP_TIMEOUT", default=300)
    @CliOpt.flag("--no-secure", envvar="FTP_NO_SECURE")
    @CliReqOpt.string("-H", "--host", envvar="FTP_HOST")
    @CliReqOpt.integer("-P", "--port", envvar="FTP_PORT")
    @CliOpt.string("-u", "--user", envvar="FTP_USER")
    @CliOpt.string("-p", "--password", envvar="FTP_PASSWORD")
    @CliOpt.flag("--debug", envvar="FTP_DEBUG")
    @CliOpt.string(
        "-P",
        "--private-key-file",
        envvar="FTP_PK_FILE",
        type=CliInputFile(),
    )
    @CliOpt.choice(
        "-k",
        "--key-type",
        envvar="FTP_KEY_TYPE",
        default="RSA",
        values=["RSA", "DSS", "ECDSA", "ED25519"],
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@main.command(name="download", help="download a single file")
@CliReqOpt.string("-r", "--remote")
@CliReqOpt.string("-l", "--local", type=CliOutputFile())
@common_options
def download(remote, local, **kwargs):
    with Log.execution_time():
        factory(kwargs).download_file(remote, local)


@main.command(name="upload", help="upload a single file")
@CliReqOpt.string("-r", "--remote")
@CliReqOpt.string("-l", "--local", type=CliInputFile())
@common_options
def upload(remote, local, **kwargs):
    with Log.execution_time():
        factory(kwargs).upload_file(local, remote)


@main.command(name="download-dir", help="download files from remote directory")
@CliOpt.string("-r", "--remote", default=".")
@CliOpt.string("-l", "--local", type=CliInputDir(), default=".")
@CliOpt.string("--only")
@CliOpt.string("--exclude")
@common_options
def download_dir(remote, local, only, exclude, **kwargs):
    with Log.execution_time():
        factory(kwargs).download_dir(
            remote_path=remote,
            local_path=local,
            only=re.compile(only) if only else None,
            exclude=re.compile(exclude) if exclude else None,
        )


@main.command(name="upload-dir", help="upload files from local directory")
@CliOpt.string("-r", "--remote", default=".")
@CliOpt.string("-l", "--local", type=CliInputDir(), default=".")
@CliOpt.string("--only")
@CliOpt.string("--exclude")
@common_options
def upload_dir(remote, local, only, exclude, **kwargs):
    with Log.execution_time():
        factory(kwargs).upload_dir(
            local_path=local,
            remote_path=remote,
            only=re.compile(only) if only else None,
            exclude=re.compile(exclude) if exclude else None,
        )
