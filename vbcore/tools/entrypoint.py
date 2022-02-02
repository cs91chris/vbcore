import click

from vbcore.tools.crypto import main as main_crypto
from vbcore.tools.database import main as main_database

main = click.Group()
main.add_command(main_database)
main.add_command(main_crypto)

if __name__ == "__main__":
    main()
