import traceback

from vbcore.data.transformations.builders.factory import BuilderFactory, BuilderEnum


def try_all():
    data = {"A": 1, "B": 2, "C": 3}

    for builder in BuilderEnum.items():
        print()
        try:
            instance = BuilderFactory.instance(builder)
            print("BUILDER:", builder)
            print("-" * 100)
            built = instance.to_self(data)
            print("--- SELF ---", built, sep="\n")
            dict_data = instance.to_dict(built)
            print()
            print("--- DICT ---", dict_data, sep="\n")
        except Exception as exc:  # pylint: disable=broad-except
            traceback.print_exc()
            print("ERROR:", exc)
        print("=" * 100)


if __name__ == "__main__":
    try_all()
