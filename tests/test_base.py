from dataclasses import dataclass

import pytest

from vbcore.base import BaseDTO, Decorator, Singleton, Static
from vbcore.tester.asserter import Asserter


@dataclass(frozen=True)
class SampleDTO(BaseDTO):
    id: int
    name: str


def test_base_dto_fields():
    Asserter.assert_equals(SampleDTO.field_names(), ("id", "name"))
    Asserter.assert_equals(SampleDTO.field_types(), {"id": "int", "name": "str"})


def test_base_dto_to_dict():
    data = SampleDTO(id=1, name="name")
    Asserter.assert_equals(data.to_dict(), {"id": 1, "name": "name"})


def test_base_dto_from_dict():
    data = {"id": 1, "name": "name"}
    Asserter.assert_equals(SampleDTO.from_dict(**data), SampleDTO(id=1, name="name"))


def test_singleton():
    class MyClass:
        pass

    class MySingletonClass(MyClass, metaclass=Singleton):
        pass

    Asserter.assert_is_not(MyClass(), MyClass())
    Asserter.assert_is(MySingletonClass(), MySingletonClass())


def test_static_class():
    class MyStaticClass(metaclass=Static):
        pass

    with pytest.raises(TypeError) as error:
        MyStaticClass()

    Asserter.assert_equals(
        str(error.value), "can not instantiate Static class MyStaticClass"
    )


@pytest.mark.skip("implement me")
def test_decorator_idempotent():
    """TODO implement me"""
    _ = Decorator
