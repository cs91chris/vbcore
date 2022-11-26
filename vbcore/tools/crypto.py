import click

from vbcore.tools.cli import Cli, CliReqOpt

try:
    from vbcore.crypto.argon import Argon2
except ImportError:
    Argon2 = None  # type: ignore


HASHERS = {
    "argon2": None if Argon2 is None else Argon2(),
}

main = click.Group(name="crypto", help="tools for cryptography")


def check_dependency(hasher):
    if hasher is None:
        Cli.abort("you must install vbcore[crypto]")


@main.command(name="hash-encode")
@Cli.argument("data")
@CliReqOpt.choice("-t", "--hasher-type", values=list(HASHERS.keys()))
def hash_encode(hasher_type, data):
    hasher = HASHERS[hasher_type]
    check_dependency(hasher)
    Cli.print(hasher.hash(data))


@main.command(name="hash-verify")
@Cli.argument("hash_value")
@Cli.argument("data")
@CliReqOpt.choice("-t", "--hasher-type", values=list(HASHERS.keys()))
def hash_verify(hasher_type, hash_value, data):
    hasher = HASHERS[hasher_type]
    check_dependency(hasher)
    Cli.print(hasher.verify(hash_value, data))
