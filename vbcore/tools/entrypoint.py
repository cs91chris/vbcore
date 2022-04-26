import sys

import click

from vbcore.tools.crypto import main as main_crypto
from vbcore.tools.database import main as main_database
from vbcore.tools.initializer.init import main as main_init
from vbcore.version import __version__

main = click.Group()


@main.command(name="version")
def dump_version():
    """dump python and vbcore version"""
    print(f"vbcore version: {__version__}")
    print(f"python version: {sys.version}")


main.add_command(main_database)
main.add_command(main_crypto)
main.add_command(main_init)

if __name__ == "__main__":
    main()
