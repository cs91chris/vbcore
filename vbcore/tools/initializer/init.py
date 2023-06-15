import os
import shutil
from pathlib import Path

import click

from vbcore.tools.cli import Cli


def replace_in_file(file: str, src: str, dst: str):
    _f = Path(file)
    text = _f.read_text(encoding="utf-8")
    text = text.replace(src, dst)
    _f.write_text(text, encoding="utf-8")


def copy_skeleton(name: str):
    from vbcore.tools import initializer  # pylint: disable=import-outside-toplevel

    try:
        source = os.path.join(initializer.__path__[0], "skeleton")
        shutil.copytree(source, ".", dirs_exist_ok=True)
        shutil.move("skel", name)
    except OSError as e:
        Cli.abort(f"Unable to create new app. Error: {e}")


def init_app(name: str):
    copy_skeleton(name)
    init_file = Path(os.path.join(name, "__init__.py"))
    init_file.write_text("", encoding="utf-8")

    for root, _, files in os.walk("."):
        for f in files:
            replace_in_file(os.path.join(root, f), "{skeleton}", name)


@click.command(name="init")
@Cli.argument("name")
def main(name):
    """Create skeleton for new application"""
    init_app(name)
