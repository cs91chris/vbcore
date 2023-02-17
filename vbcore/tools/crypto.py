import sys
from functools import partial

import click

from vbcore.crypto.exceptions import VBInvalidHashError
from vbcore.crypto.factory import CryptoFactory, HasherEnum
from vbcore.tools.cli import Cli, CliReqOpt

main = click.Group(name="crypto", help="tools for cryptography")

crypto_type_option = partial(
    CliReqOpt.choice, "-t", "--type", "crypto_class", values=HasherEnum.items()
)


@main.command(name="hash-encode")
@Cli.argument("data")
@crypto_type_option()
def hash_encode(crypto_class, data):
    hasher = CryptoFactory.instance(crypto_class)
    Cli.print(hasher.hash(data))


@main.command(name="hash-verify")
@Cli.argument("hash_value")
@Cli.argument("data")
@crypto_type_option()
def hash_verify(crypto_class, hash_value, data):
    hasher = CryptoFactory.instance(crypto_class)
    try:
        hasher.verify(hash_value, data, raise_exc=True)
    except VBInvalidHashError as exc:
        Cli.print(exc)
        sys.exit(1)
