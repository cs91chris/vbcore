import sys

import click

from vbcore.tools.crypto import main as main_crypto
from vbcore.tools.database import main as main_database
from vbcore.version import __version__


def dump_version():
    print(f"vbcore version: {__version__}")
    print(f"python version: {sys.version}")


main = click.Group(invoke_without_command=True, callback=dump_version)
main.add_command(main_database)
main.add_command(main_crypto)

if __name__ == "__main__":
    main()
