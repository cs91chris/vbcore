from vbcore import misc
from vbcore.importer import Importer
from vbcore.tester.mixins import Asserter


def test_import_module():
    to_int_func = Importer.from_module("vbcore.misc:to_int")
    Asserter.assert_equals(to_int_func, misc.to_int)
