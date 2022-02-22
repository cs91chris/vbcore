import pytest

from vbcore import misc
from vbcore.importer import (
    Importer,
    ImporterFactory,
    ImporterAttributeError,
    ImporterModuleError,
    ImporterValueError,
    ImporterInstanceError,
    ImporterSubclassError,
)
from vbcore.tester.mixins import Asserter


class Base:
    @classmethod
    def perform(cls):
        return "base"


class AClass(Base):
    @classmethod
    def perform(cls):
        return "A"


class BClass(Base):
    @classmethod
    def perform(cls):
        return "B"


def test_import_module():
    to_int_func = Importer.from_module("vbcore.misc:to_int")
    Asserter.assert_equals(to_int_func, misc.to_int)


def test_import_module_error():
    with pytest.raises(ImporterModuleError) as error:
        Importer.from_module("module.not.found")

    Asserter.assert_equals(error.value.name, "module.not.found")
    Asserter.assert_true(isinstance(error.value.exception, ModuleNotFoundError))


def test_import_attribute_error():
    with pytest.raises(ImporterAttributeError) as error:
        Importer.from_module("vbcore.misc:not_found")

    Asserter.assert_equals(error.value.module.__name__, "vbcore.misc")
    Asserter.assert_equals(error.value.attribute, "not_found")


def test_import_instance_error():
    with pytest.raises(ImporterInstanceError) as error:
        Importer.from_module("vbcore.misc:to_int", instance_of=str)

    Asserter.assert_equals(error.value.item, misc.to_int)
    Asserter.assert_equals(error.value.instance_of, str)


def test_import_subclass_error():
    with pytest.raises(ImporterSubclassError) as error:
        Importer.from_module("tests.test_importer:AClass", subclass_of=dict)

    Asserter.assert_equals(error.value.item, AClass)
    Asserter.assert_equals(error.value.subclass_of, dict)


def test_import_factory():
    factory = ImporterFactory(
        base_class=Base,
        package="tests",
        classes={"A": "test_importer:AClass", "B": "test_importer:BClass"},
    )

    Asserter.assert_equals(factory.get_class("A"), AClass)
    Asserter.assert_equals(factory.get_class("A").perform(), "A")
    Asserter.assert_true(isinstance(factory.get_instance("B"), BClass))


def test_import_factory_error():
    factory = ImporterFactory()

    with pytest.raises(ImporterValueError) as error:
        factory.get_class("A")

    Asserter.assert_equals(error.value.name, "A")
