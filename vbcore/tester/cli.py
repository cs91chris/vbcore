import sys

import pytest


def main():
    pytest.main(
        [
            "-v",
            "-rf",
            "--strict-markers",
            "-p",
            "vbcore.tester.plugins.fixtures",
            "-p",
            "vbcore.tester.plugins.startup",
            *sys.argv[1:],
        ]
    )


if __name__ == "__main__":
    main()
