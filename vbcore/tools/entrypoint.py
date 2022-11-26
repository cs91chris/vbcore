import sys

import click

from vbcore.tools.cli import Cli
from vbcore.tools.crypto import main as main_crypto
from vbcore.tools.database import main as main_database
from vbcore.tools.initializer.init import main as main_init
from vbcore.tools.scheduler import main as main_scheduler
from vbcore.version import __version__

main = click.Group()


@main.command(name="version")
def dump_version():
    """dump python and vbcore version"""
    Cli.print(f"vbcore version: {__version__}")
    Cli.print(f"python version: {sys.version}")


main.add_command(main_database)
main.add_command(main_crypto)
main.add_command(main_init)
main.add_command(main_scheduler)

if __name__ == "__main__":
    main()
