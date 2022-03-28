import click

try:
    from vbcore.crypto.argon import Argon2
except ImportError:
    Argon2 = None  # type: ignore


HASHERS = {
    "argon2": None if Argon2 is None else Argon2(),
}
HASHERS_CHOICE = click.Choice(list(HASHERS.keys()))

main = click.Group(name="crypto", help="tools for cryptography")


def check_dependency(hasher):
    if hasher is None:
        raise ImportError("you must install vbcore[crypto]")


@main.command(name="hash-encode")
@click.argument("data")
@click.option("-t", "--hasher-type", type=HASHERS_CHOICE, help="hasher type")
def hash_encode(hasher_type, data):
    hasher = HASHERS[hasher_type]
    check_dependency(hasher)
    print(hasher.hash(data), flush=True)


@main.command(name="hash-verify")
@click.argument("hash_value")
@click.argument("data")
@click.option("-t", "--hasher-type", type=HASHERS_CHOICE, help="hasher type")
def hash_verify(hasher_type, hash_value, data):
    hasher = HASHERS[hasher_type]
    check_dependency(hasher)
    print(hasher.verify(hash_value, data), flush=True)
