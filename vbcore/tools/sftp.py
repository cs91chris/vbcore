import functools
import re

import click

from vbcore.net.sftp import SFTPHandler, SFTPOptions
from vbcore.tools.cli import CliOpt, CliReqOpt

main = click.Group(name="sftp", help="sftp handler")


def common_options(func):
    @CliReqOpt.string("-H", "--host")
    @CliReqOpt.integer("-P", "--port")
    @CliOpt.string("-u", "--user")
    @CliOpt.string("-p", "--password")
    @CliOpt.string("-k", "--key-type")
    @CliOpt.string("-P", "--private-key-file")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@main.command(name="download")
@CliReqOpt.string("-r", "--remote")
@CliReqOpt.string("-l", "--local")
@common_options
def download(remote, local, **kwargs):
    client = SFTPHandler(SFTPOptions(**kwargs))  # pylint: disable=missing-kwoa
    client.download_file(remote, local)


@main.command(name="upload")
@CliReqOpt.string("-r", "--remote")
@CliReqOpt.string("-l", "--local")
@common_options
def upload(remote, local, **kwargs):
    client = SFTPHandler(SFTPOptions(**kwargs))  # pylint: disable=missing-kwoa
    client.upload_file(local, remote)


@main.command(name="download-dir")
@CliReqOpt.string("-r", "--remote")
@CliReqOpt.string("-l", "--local")
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


@main.command(name="upload-dir")
@CliReqOpt.string("-r", "--remote")
@CliReqOpt.string("-l", "--local")
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
