import pytest

from vbcore.stringutils.notations import Case
from vbcore.tester.asserter import Asserter


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", True),
        ("SAMPLETESTVALUE", True),
        ("sampletestvalue", False),
        ("sampleTestValue", False),
        ("sample_test_value", False),
        ("Sample_Test_Value", False),
        ("SAMPLE_TEST_VALUE", False),
        ("sample_Test_Value", False),
        ("sample test value", False),
        ("Sample Test Value", False),
        ("SAMPLE TEST VALUE", False),
        ("sample Test Value", False),
        ("sample-test-value", False),
        ("Sample-Test-Value", False),
        ("SAMPLE-TEST-VALUE", False),
        ("sample-Test-Value", False),
    ],
)
def test_is_camel(value, expected):
    Asserter.assert_is(Case.is_camel(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", False),
        ("SAMPLETESTVALUE", False),
        ("sampletestvalue", True),
        ("sampleTestValue", True),
        ("sample_test_value", False),
        ("Sample_Test_Value", False),
        ("SAMPLE_TEST_VALUE", False),
        ("sample_Test_Value", False),
        ("sample test value", False),
        ("Sample Test Value", False),
        ("SAMPLE TEST VALUE", False),
        ("sample Test Value", False),
        ("sample-test-value", False),
        ("Sample-Test-Value", False),
        ("SAMPLE-TEST-VALUE", False),
        ("sample-Test-Value", False),
    ],
)
def test_is_drome(value, expected):
    Asserter.assert_is(Case.is_drome(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", False),
        ("SAMPLETESTVALUE", False),
        ("sampletestvalue", True),
        ("sampleTestValue", False),
        ("sample_test_value", True),
        ("Sample_Test_Value", False),
        ("SAMPLE_TEST_VALUE", False),
        ("sample_Test_Value", False),
        ("sample test value", False),
        ("Sample Test Value", False),
        ("SAMPLE TEST VALUE", False),
        ("sample Test Value", False),
        ("sample-test-value", False),
        ("Sample-Test-Value", False),
        ("SAMPLE-TEST-VALUE", False),
        ("sample-Test-Value", False),
    ],
)
def test_is_snake(value, expected):
    Asserter.assert_is(Case.is_snake(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", False),
        ("SAMPLETESTVALUE", False),
        ("sampletestvalue", True),
        ("sampleTestValue", False),
        ("sample_test_value", False),
        ("Sample_Test_Value", False),
        ("SAMPLE_TEST_VALUE", False),
        ("sample_Test_Value", False),
        ("sample test value", False),
        ("Sample Test Value", False),
        ("SAMPLE TEST VALUE", False),
        ("sample Test Value", False),
        ("sample-test-value", True),
        ("Sample-Test-Value", False),
        ("SAMPLE-TEST-VALUE", False),
        ("sample-Test-Value", False),
    ],
)
def test_is_kebab(value, expected):
    Asserter.assert_is(Case.is_kebab(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", False),
        ("SAMPLETESTVALUE", False),
        ("sampletestvalue", False),
        ("sampleTestValue", False),
        ("sample_test_value", False),
        ("Sample_Test_Value", False),
        ("SAMPLE_TEST_VALUE", False),
        ("sample_Test_Value", False),
        ("sample test value", True),
        ("Sample Test Value", True),
        ("SAMPLE TEST VALUE", True),
        ("sample Test Value", True),
        ("sample-test-value", False),
        ("Sample-Test-Value", False),
        ("SAMPLE-TEST-VALUE", False),
        ("sample-Test-Value", False),
    ],
)
def test_are_words(value, expected):
    Asserter.assert_is(Case.are_words(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", "SampleTestValue"),
        ("SAMPLETESTVALUE", "SAMPLETESTVALUE"),
        ("sampletestvalue", "Sampletestvalue"),
        ("sampleTestValue", "SampleTestValue"),
        ("sample_test_value", "SampleTestValue"),
        ("Sample_Test_Value", "SampleTestValue"),
        ("SAMPLE_TEST_VALUE", "SampleTestValue"),
        ("sample_Test_Value", "SampleTestValue"),
        ("sample test value", "SampleTestValue"),
        ("Sample Test Value", "SampleTestValue"),
        ("SAMPLE TEST VALUE", "SampleTestValue"),
        ("sample Test Value", "SampleTestValue"),
        ("sample-test-value", "SampleTestValue"),
        ("Sample-Test-Value", "SampleTestValue"),
        ("SAMPLE-TEST-VALUE", "SampleTestValue"),
        ("sample-Test-Value", "SampleTestValue"),
    ],
)
def test_to_camel(value, expected):
    Asserter.assert_equals(Case.to_camel(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", "sampleTestValue"),
        ("SAMPLETESTVALUE", "sAMPLETESTVALUE"),
        ("sampletestvalue", "sampletestvalue"),
        ("sampleTestValue", "sampleTestValue"),
        ("sample_test_value", "sampleTestValue"),
        ("Sample_Test_Value", "sampleTestValue"),
        ("SAMPLE_TEST_VALUE", "sampleTestValue"),
        ("sample_Test_Value", "sampleTestValue"),
        ("sample test value", "sampleTestValue"),
        ("Sample Test Value", "sampleTestValue"),
        ("SAMPLE TEST VALUE", "sampleTestValue"),
        ("sample Test Value", "sampleTestValue"),
        ("sample-test-value", "sampleTestValue"),
        ("Sample-Test-Value", "sampleTestValue"),
        ("SAMPLE-TEST-VALUE", "sampleTestValue"),
        ("sample-Test-Value", "sampleTestValue"),
    ],
)
def test_to_drome(value, expected):
    Asserter.assert_equals(Case.to_drome(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", "sample_test_value"),
        ("SAMPLETESTVALUE", "sampletestvalue"),
        ("sampletestvalue", "sampletestvalue"),
        ("sampleTestValue", "sample_test_value"),
        ("sample_test_value", "sample_test_value"),
        ("Sample_Test_Value", "sample_test_value"),
        ("SAMPLE_TEST_VALUE", "sample_test_value"),
        ("sample_Test_Value", "sample_test_value"),
        ("sample test value", "sample_test_value"),
        ("Sample Test Value", "sample_test_value"),
        ("SAMPLE TEST VALUE", "sample_test_value"),
        ("sample Test Value", "sample_test_value"),
        ("sample-test-value", "sample_test_value"),
        ("Sample-Test-Value", "sample_test_value"),
        ("SAMPLE-TEST-VALUE", "sample_test_value"),
        ("sample-Test-Value", "sample_test_value"),
    ],
)
def test_to_snake(value, expected):
    Asserter.assert_equals(Case.to_snake(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", "sample-test-value"),
        ("SAMPLETESTVALUE", "sampletestvalue"),
        ("sampletestvalue", "sampletestvalue"),
        ("sampleTestValue", "sample-test-value"),
        ("sample_test_value", "sample-test-value"),
        ("Sample_Test_Value", "sample-test-value"),
        ("SAMPLE_TEST_VALUE", "sample-test-value"),
        ("sample_Test_Value", "sample-test-value"),
        ("sample test value", "sample-test-value"),
        ("Sample Test Value", "sample-test-value"),
        ("SAMPLE TEST VALUE", "sample-test-value"),
        ("sample Test Value", "sample-test-value"),
        ("sample-test-value", "sample-test-value"),
        ("Sample-Test-Value", "sample-test-value"),
        ("SAMPLE-TEST-VALUE", "sample-test-value"),
        ("sample-Test-Value", "sample-test-value"),
    ],
)
def test_to_kebab(value, expected):
    Asserter.assert_equals(Case.to_kebab(value), expected)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SampleTestValue", "Sample Test Value"),
        ("SAMPLETESTVALUE", "SAMPLETESTVALUE"),
        ("sampletestvalue", "sampletestvalue"),
        ("sampleTestValue", "sample Test Value"),
        ("sample_test_value", "sample test value"),
        ("Sample_Test_Value", "Sample Test Value"),
        ("SAMPLE_TEST_VALUE", "SAMPLE TEST VALUE"),
        ("sample_Test_Value", "sample Test Value"),
        ("sample test value", "sample test value"),
        ("Sample Test Value", "Sample Test Value"),
        ("SAMPLE TEST VALUE", "SAMPLE TEST VALUE"),
        ("sample Test Value", "sample Test Value"),
        ("sample-test-value", "sample test value"),
        ("Sample-Test-Value", "Sample Test Value"),
        ("SAMPLE-TEST-VALUE", "SAMPLE TEST VALUE"),
        ("sample-Test-Value", "sample Test Value"),
    ],
)
def test_to_words(value, expected):
    Asserter.assert_equals(Case.to_words(value), expected)
