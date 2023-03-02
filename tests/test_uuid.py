import pytest

from vbcore import uuid
from vbcore.tester.asserter import Asserter


def test_uuid_valid():
    Asserter.assert_true(uuid.check_uuid(uuid.get_uuid()))
    Asserter.assert_true(uuid.check_uuid(uuid.get_uuid(hex_=False)))


@pytest.mark.parametrize("version", (0, 2, 6))
def test_uuid_invalid_version(version):
    with pytest.raises(TypeError) as error:
        uuid.get_uuid(ver=version)

    Asserter.assert_equals(error.value.args, (f"invalid uuid version {version}",))


@pytest.mark.parametrize("version", (1, 3, 4, 5))
def test_uuid_invalid(version):
    invalid_uuid = "fake uuid"

    Asserter.assert_false(uuid.check_uuid(invalid_uuid, ver=version))

    with pytest.raises(ValueError) as error:
        uuid.check_uuid(invalid_uuid, ver=version, raise_exc=True)

    Asserter.assert_equals(
        error.value.args, (f"'{invalid_uuid}' is an invalid UUID{version}",)
    )


@pytest.mark.parametrize(
    "version, name",
    [
        (1, None),
        (3, "test"),
        (4, None),
        (5, "test"),
    ],
)
def test_uuid_version(version, name):
    Asserter.assert_true(
        uuid.check_uuid(uuid.get_uuid(version, name=name), ver=version)
    )
