import os
import re
import sys
import typing as t

from pkg_resources import parse_requirements
from setuptools import find_packages as base_find_packages, setup
from setuptools.command.test import test

LICENSE = "MIT"
URL = "https://github.com/cs91chris/vbcore"
PLATFORMS = "any"
PYTHON_VERSION = ">=3.8"
DESCRIPTION = "VBCore common helpers and components"
PACKAGE_DATA = True

PKG_NAME = "vbcore"
PKG_TEST = "tests"
PKG_SCRIPTS = f"{PKG_NAME}.scripts"
EXCLUDE_FILES: t.List = []

ENTRY_POINTS: t.Dict[str, t.List[str]] = {
    "console_scripts": [],
}

BASE_PATH = os.path.dirname(__file__)
VERSION_FILE = os.path.join(PKG_NAME, "version.py")

REQUIRES = [
    "python-dateutil",
    "python-decouple",
    "python-dotenv",
    "pyyaml",
]

REQUIRES_ALL = REQUIRES + [
    "requests",
    "jsonschema",
    "user_agents",
    "pysocks",
]

REQUIRES_TEST = REQUIRES_ALL + [
    "responses",
    "coverage",
    "pytest",
    "pytest-cov",
]


try:
    # must be after setuptools
    # noinspection PyPackageRequirements
    from Cython.Build import cythonize as base_cythonize

    # noinspection PyPackageRequirements,PyPep8Naming
    import Cython.Compiler.Options as cython_options

    cython_options.docstrings = False
except ImportError:
    cython_options = None
    base_cythonize = None

if "--cythonize" not in sys.argv:
    base_cythonize = None  # pylint: disable=invalid-name
else:
    sys.argv.remove("--cythonize")


def ext_paths(root_dir, exclude=()):
    paths = []
    for root, _, files in os.walk(root_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_ext = filename.split(".")[-1]
            if file_path in exclude or file_ext not in ("py", "pyx"):
                continue

            paths.append(file_path)
    return paths


def read(file):
    with open(os.path.join(BASE_PATH, file), encoding="utf-8") as f:
        return f.read()


def grep(file, name):
    (value,) = re.findall(rf'{name}\W*=\W*"([^"]+)"', read(file))
    return value


def readme(file):
    try:
        return read(file)
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return None


def read_requirements(filename):
    return [str(req) for req in parse_requirements(read(filename))]


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)

    def run_tests(self):
        import pytest  # pylint: disable=C0415,E0401

        sys.exit(pytest.main([PKG_TEST]))


def cythonize(paths):
    if base_cythonize is not None:
        # noinspection PyCallingNonCallable
        return base_cythonize(paths, language_level=3)
    return None


def find_packages():
    if base_cythonize is not None:
        return [PKG_SCRIPTS]
    return base_find_packages(
        exclude=(
            "sandbox",
            PKG_TEST,
            f"{PKG_TEST}.*",
        )
    )


setup(
    name=PKG_NAME,
    url=URL,
    license=LICENSE,
    description=DESCRIPTION,
    platforms=PLATFORMS,
    python_requires=PYTHON_VERSION,
    long_description=readme("README.rst"),
    version=grep(VERSION_FILE, "__version__"),
    author=grep(VERSION_FILE, "__author_name__"),
    author_email=grep(VERSION_FILE, "__author_email__"),
    zip_safe=False,
    include_package_data=PACKAGE_DATA,
    packages=find_packages(),
    ext_modules=cythonize(ext_paths(PKG_NAME, EXCLUDE_FILES)),
    entry_points=ENTRY_POINTS,
    test_suite=PKG_TEST,
    install_requires=REQUIRES,
    extras_require={
        "test": REQUIRES_TEST,
        "all": REQUIRES_ALL,
    },
    cmdclass=dict(test=PyTest),
    classifiers=[],
)
