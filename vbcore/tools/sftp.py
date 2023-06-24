import functools
import re

import click

from vbcore.net.sftp import AlgoKeyEnum, SFTPHandler, SFTPOptions
from vbcore.tools.cli import CliInputDir, CliInputFile, CliOpt, CliOutputFile, CliReqOpt

main = click.Group(name="sftp", help="sftp handler")


def common_options(func):
    @CliReqOpt.string("-H", "--host", envvar="SFTP_HOST")
    @CliReqOpt.integer("-P", "--port", envvar="SFTP_PORT")
    @CliOpt.string("-u", "--user", envvar="SFTP_USER")
    @CliOpt.string("-p", "--password", envvar="SFTP_PASSWORD")
    @CliOpt.string(
        "-P",
        "--private-key-file",
        envvar="SFTP_PK_FILE",
        type=CliInputFile(),
    )
    @CliOpt.choice(
        "-k",
        "--key-type",
        envvar="SFTP_KEY_TYPE",
        default="RSA",
        values=AlgoKeyEnum.items(),
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
    client = SFTPHandler(SFTPOptions(**kwargs))  # pylint: disable=missing-kwoa
    client.download_file(remote, local)


@main.command(name="upload", help="upload a single file")
@CliReqOpt.string("-r", "--remote")
@CliReqOpt.string("-l", "--local", type=CliInputFile())
@common_options
def upload(remote, local, **kwargs):
    client = SFTPHandler(SFTPOptions(**kwargs))  # pylint: disable=missing-kwoa
    client.upload_file(local, remote)


@main.command(name="download-dir", help="download files from remote directory")
@CliOpt.string("-r", "--remote", default=".")
@CliOpt.string("-l", "--local", type=CliInputDir(), default=".")
@CliOpt.string("--only")
@CliOpt.string("--exclude")
@common_options
def download_dir(remote, local, only, exclude, **kwargs):
    client = SFTPHandler(SFTPOptions(**kwargs))  # pylint: disable=missing-kwoa
    client.download_dir(
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
    client = SFTPHandler(SFTPOptions(**kwargs))  # pylint: disable=missing-kwoa
    client.upload_dir(
        local_path=local,
        remote_path=remote,
        only=re.compile(only) if only else None,
        exclude=re.compile(exclude) if exclude else None,
    )
