from vbcore.crypto import CryptoFactory, CryptoEnum


def try_all():
    password = "password"

    for algo in CryptoEnum.products():
        print()
        try:
            instance = CryptoFactory.instance(algo)
            print("ALGO:", algo)
            hashed = instance.hash(password)
            print("HASHED:", hashed)
        except Exception as exc:
            print("ERROR:", exc)


if __name__ == "__main__":
    try_all()
