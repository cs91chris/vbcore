import os
import shutil
import sys
from pathlib import Path

import click


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
        print(f"Unable to create new app. Error: {e}", file=sys.stderr)
        sys.exit(1)


def init_app(name: str):
    copy_skeleton(name)
    init_file = Path(os.path.join(name, "__init__.py"))
    init_file.write_text("from .version import *\n", encoding="utf-8")

    for root, _, files in os.walk("."):
        for f in files:
            file = os.path.join(root, f)
            replace_in_file(file, "{skeleton}", name)


@click.command(name="init")
@click.argument("name")
def main(name):
    """Create skeleton for new application"""
    init_app(name)
