import traceback

from vbcore.crypto import CryptoFactory, HasherEnum


def try_all():
    password = "password"

    for algo in HasherEnum.items():
        print()
        try:
            instance = CryptoFactory.instance(algo)
            print("ALGO:", algo)
            hashed = instance.hash(password)
            print("HASHED:", hashed)
        except Exception as exc:  # pylint: disable=broad-except
            traceback.print_exc()
            print("ERROR:", exc)


if __name__ == "__main__":
    try_all()
