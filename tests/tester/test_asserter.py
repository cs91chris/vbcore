import pytest

from vbcore.datastruct import ObjectDict
from vbcore.http.httpcode import StatusType
from vbcore.jsonschema.schemas.jsonrpc import JSONRPC
from vbcore.misc import CommonRegex
from vbcore.tester.asserter import Asserter


@Asserter.with_assertion_error("TEST FAILED")
def test_asserter_fail():
    Asserter.assert_that(lambda a, e: False, None, error="TEST FAILED")


@pytest.mark.parametrize(
    "actual, expected, error",
    [
        (1, 2, "Test that '1' is equals to '2' failed"),
        ("aaa", "bbb", "Test that 'aaa' is equals to 'bbb' failed"),
        (True, False, "Test that 'True' is equals to 'False' failed"),
        ([1, 2], [1, 3], "Test that '[1, 2]' is equals to '[1, 3]' failed"),
        ((1, 2), (1, 3), "Test that '(1, 2)' is equals to '(1, 3)' failed"),
        ({1, 2}, {1, 3}, "Test that '{1, 2}' is equals to '{1, 3}' failed"),
        ({1: 2}, {1: 3}, "Test that '{1: 2}' is equals to '{1: 3}' failed"),
    ],
    ids=[
        "number",
        "string",
        "bool",
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_assert_equals(actual, expected, error):
    Asserter.assert_equals(actual, actual)
    Asserter.assertion_error(error, Asserter.assert_equals, actual, expected)


@pytest.mark.parametrize(
    "actual, expected, error",
    [
        (1, 2, "Test that '1' is different from '1' failed"),
        ("aaa", "bbb", "Test that 'aaa' is different from 'aaa' failed"),
        (True, False, "Test that 'True' is different from 'True' failed"),
        ([1, 2], [2, 3], "Test that '[1, 2]' is different from '[1, 2]' failed"),
        ((1, 2), (2, 3), "Test that '(1, 2)' is different from '(1, 2)' failed"),
        ({1, 2}, {2, 3}, "Test that '{1, 2}' is different from '{1, 2}' failed"),
        ({1: 2}, {2: 3}, "Test that '{1: 2}' is different from '{1: 2}' failed"),
    ],
    ids=[
        "number",
        "string",
        "bool",
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_assert_different(actual, expected, error):
    Asserter.assert_different(actual, expected)
    Asserter.assertion_error(error, Asserter.assert_different, actual, actual)


@pytest.mark.parametrize(
    "item, error",
    [
        (1, "Test that '1' is False failed"),
        ("aaa", "Test that 'aaa' is False failed"),
        (True, "Test that 'True' is False failed"),
        ([1, 2], "Test that '[1, 2]' is False failed"),
        ((1, 2), "Test that '(1, 2)' is False failed"),
        ({1, 2}, "Test that '{1, 2}' is False failed"),
        ({1: 2}, "Test that '{1: 2}' is False failed"),
    ],
    ids=[
        "number",
        "string",
        "bool",
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_assert_true(item, error):
    Asserter.assert_true(item)
    Asserter.assertion_error(error, Asserter.assert_false, item)


@pytest.mark.parametrize(
    "item, error",
    [
        (0, "Test that '0' is True failed"),
        ("", "Test that '' is True failed"),
        (False, "Test that 'False' is True failed"),
        ([], "Test that '[]' is True failed"),
        ((), "Test that '()' is True failed"),
        (set(), "Test that 'set()' is True failed"),
        ({}, "Test that '{}' is True failed"),
    ],
    ids=[
        "number",
        "string",
        "bool",
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_assert_false(item, error):
    Asserter.assert_false(item)
    Asserter.assertion_error(error, lambda: Asserter.assert_true(item))


def test_assert_none():
    Asserter.assert_none(None)
    Asserter.assertion_error(
        "Test that 'None' is not None failed",
        lambda: Asserter.assert_not_none(None),
    )


@pytest.mark.parametrize(
    "item, error",
    [
        (0, "Test that '0' is None failed"),
        (False, "Test that 'False' is None failed"),
        ("", "Test that '' is None failed"),
        ([], "Test that '[]' is None failed"),
        ((), "Test that '()' is None failed"),
        (set(), "Test that 'set()' is None failed"),
        ({}, "Test that '{}' is None failed"),
    ],
    ids=[
        "number",
        "bool",
        "string",
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_assert_not_none(item, error):
    Asserter.assert_not_none(item)
    Asserter.assertion_error(error, lambda: Asserter.assert_none(item))


@pytest.mark.parametrize(
    "actual, expected",
    [
        (2, 1),
        (True, False),
        ("aaa", "a"),
        ([1, 2], [1]),
        ((1, 2), (1,)),
        ({1, 2}, {1}),
    ],
    ids=[
        "number",
        "bool",
        "string",
        "list",
        "tuple",
        "set",
    ],
)
def test_assert_greater(actual, expected):
    Asserter.assert_greater(actual, expected)
    Asserter.assert_greater(actual, actual, equals=True)

    Asserter.assertion_error(
        f"Test that '{expected}' is greater than '{actual}' failed",
        lambda: Asserter.assert_greater(expected, actual),
    )
    Asserter.assertion_error(
        f"Test that '{actual}' is greater than '{actual}' failed",
        lambda: Asserter.assert_greater(actual, actual),
    )


@pytest.mark.parametrize(
    "actual, expected",
    [
        (1, 2),
        (False, True),
        ("a", "aaa"),
        ([1], [1, 2]),
        ((1,), (1, 2)),
        ({1}, {1, 2}),
    ],
    ids=[
        "number",
        "bool",
        "string",
        "list",
        "tuple",
        "set",
    ],
)
def test_assert_lesser(actual, expected):
    Asserter.assert_lesser(actual, expected)
    Asserter.assert_lesser(actual, actual, equals=True)

    Asserter.assertion_error(
        f"Test that '{expected}' is less than '{actual}' failed",
        lambda: Asserter.assert_lesser(expected, actual),
    )
    Asserter.assertion_error(
        f"Test that '{actual}' is less than '{actual}' failed",
        lambda: Asserter.assert_lesser(actual, actual),
    )


@pytest.mark.parametrize(
    "iterable, error",
    (
        ([1, 2, 3], "Test that '4' is in '[1, 2, 3]' failed"),
        ((1, 2, 3), "Test that '4' is in '(1, 2, 3)' failed"),
        ({1, 2, 3}, "Test that '4' is in '{1, 2, 3}' failed"),
        ({1: True, 2: True}, "Test that '4' is in '{1: True, 2: True}' failed"),
    ),
    ids=[
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_assert_in(iterable, error):
    Asserter.assert_in(2, iterable)
    Asserter.assertion_error(error, lambda: Asserter.assert_in(4, iterable))


@pytest.mark.parametrize(
    "iterable, error",
    (
        ([1, 2, 3], "Test that '2' is not in '[1, 2, 3]' failed"),
        ((1, 2, 3), "Test that '2' is not in '(1, 2, 3)' failed"),
        ({1, 2, 3}, "Test that '2' is not in '{1, 2, 3}' failed"),
        ({1: 1, 2: 2}, "Test that '2' is not in '{1: 1, 2: 2}' failed"),
    ),
    ids=[
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_assert_not_in(iterable, error):
    Asserter.assert_not_in(4, iterable)
    Asserter.assertion_error(error, lambda: Asserter.assert_not_in(2, iterable))


@pytest.mark.parametrize(
    "item_type, item",
    [
        (int, 1),
        (float, 1.0),
        (bool, True),
        (str, "aaa"),
        (list, [1, 2, 3]),
        (tuple, (1, 2, 3)),
        (set, {1, 2, 3}),
        (dict, {1: 0, 2: 0}),
    ],
    ids=[
        "int",
        "float",
        "bool",
        "str",
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_assert_isinstance(item_type, item):
    class Custom:
        pass

    Asserter.assert_isinstance(item, item_type)
    Asserter.assertion_error(
        f"Test that '{item}' is instance of '{type(Custom())}' failed",
        lambda: Asserter.assert_isinstance(item, Custom),
    )


def test_assert_issubclass():
    class Base:
        pass

    class Custom:
        pass

    class SubCustom(Base):
        pass

    Asserter.assert_issubclass(SubCustom, Base)
    Asserter.assertion_error(
        f"Test that '{Custom}' is subclass of '{Base}' failed",
        lambda: Asserter.assert_issubclass(Custom, Base),
    )


@pytest.mark.parametrize(
    "actual, expected",
    [
        ((1, 3), [1, 2, 3]),
        ((1, 3), (1, 2, 3)),
        ((1, 3), {1, 2, 3}),
        ((1, 3), {1: "a", 2: "b", 3: "c"}),
    ],
    ids=[
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_allin_ok(actual, expected):
    Asserter.assert_allin(actual, expected)


@pytest.mark.parametrize(
    "actual, expected, error",
    [
        ((1, 4), [1, 2, 3], "Test that '(1, 4)' is all in '[1, 2, 3]' failed"),
        ((1, 4), (1, 2, 3), "Test that '(1, 4)' is all in '(1, 2, 3)' failed"),
        ((1, 4), {1, 2, 3}, "Test that '(1, 4)' is all in '{1, 2, 3}' failed"),
        ((1, 4), {1: 0, 2: 0}, "Test that '(1, 4)' is all in '{1: 0, 2: 0}' failed"),
    ],
    ids=[
        "list",
        "tuple",
        "set",
        "dict",
    ],
)
def test_allin_error(actual, expected, error):
    Asserter.assertion_error(error, lambda: Asserter.assert_allin(actual, expected))


@pytest.mark.parametrize(
    "center, left, right, in_value, out_value, message",
    [
        # fmt: off
        (False, False, False, 3, 5, "Test that '5' is in range '(1, 5)' failed"),
        (False, False, True,  5, 6, "Test that '6' is in range '(1, 5]' failed"),
        (False, True,  False, 1, 6, "Test that '6' is in range '[1, 5)' failed"),
        (False, True,  True,  1, 6, "Test that '6' is in range '[1, 5]' failed"),
        (True,  False, False, 1, 6, "Test that '6' is in range '[1, 5]' failed"),
        (True,  False, True,  1, 6, "Test that '6' is in range '[1, 5]' failed"),
        (True,  True,  False, 1, 6, "Test that '6' is in range '[1, 5]' failed"),
        (True,  True,  True,  1, 6, "Test that '6' is in range '[1, 5]' failed"),
        # fmt: on
    ],
    ids=[
        "open",
        "right",
        "left",
        "left-right",
        "closed",
        "closed-right",
        "closed-left",
        "closed-left-right",
    ],
)
def test_assert_range(center, left, right, in_value, out_value, message):
    sample_range = (1, 5)
    Asserter.assert_range(in_value, sample_range, closed=center, left=left, right=right)
    Asserter.assertion_error(
        message,
        lambda: Asserter.assert_range(
            out_value, sample_range, closed=center, left=left, right=right
        ),
    )


@pytest.mark.parametrize(
    "iterable, error",
    [
        ([1, 2, 3], "Test that len is 1 failed: actual len is 3"),
        ({1, 2, 3}, "Test that len is 1 failed: actual len is 3"),
        ((1, 2, 3), "Test that len is 1 failed: actual len is 3"),
        ({1: 1, 2: 2, 3: 3}, "Test that len is 1 failed: actual len is 3"),
    ],
    ids=[
        "list",
        "set",
        "tuple",
        "dict",
    ],
)
def test_assert_len(iterable, error):
    Asserter.assert_len(iterable, 3)
    Asserter.assertion_error(error, lambda: Asserter.assert_len(iterable, 1))


@Asserter.with_assertion_error("Test that '[1]' is empty list failed")
def test_assert_is_empty_list():
    Asserter.assert_is_empty_list([])
    Asserter.assert_is_empty_list([1])


@Asserter.with_assertion_error("Test that '(1,)' is empty tuple failed")
def test_assert_is_empty_tuple():
    Asserter.assert_is_empty_tuple(())
    Asserter.assert_is_empty_tuple((1,))


@Asserter.with_assertion_error("Test that '{1}' is empty set failed")
def test_assert_is_empty_set():
    Asserter.assert_is_empty_set(set())
    Asserter.assert_is_empty_set({1})


@Asserter.with_assertion_error("Test that '{1: 2}' is empty dict failed")
def test_assert_is_empty_dict():
    Asserter.assert_is_empty_dict({})
    Asserter.assert_is_empty_dict({1: 2})


@Asserter.with_assertion_error("Test that '[]' is not empty list failed")
def test_assert_not_empty_list():
    Asserter.assert_not_empty_list([1])
    Asserter.assert_not_empty_list([])


@Asserter.with_assertion_error("Test that '()' is not empty tuple failed")
def test_assert_not_empty_tuple():
    Asserter.assert_not_empty_tuple((1,))
    Asserter.assert_not_empty_tuple(())


@Asserter.with_assertion_error("Test that 'set()' is not empty set failed")
def test_assert_not_empty_set():
    Asserter.assert_not_empty_set({1})
    Asserter.assert_not_empty_set(set())


@Asserter.with_assertion_error("Test that '{}' is not empty dict failed")
def test_assert_not_empty_dict():
    Asserter.assert_not_empty_dict({1: 2})
    Asserter.assert_not_empty_dict({})


@pytest.mark.parametrize(
    "data, schema",
    [
        (
            {"jsonrpc": "2.0", "method": "sub", "params": [2, 1], "id": 1},
            JSONRPC.REQUEST,
        ),
        (
            {"jsonrpc": "2.0", "id": 1, "result": 1},
            JSONRPC.RESPONSE,
        ),
    ],
    ids=[
        "jsonrpc-request",
        "jsonrpc-response",
    ],
)
def test_assert_json_schema(data, schema):
    Asserter.assert_json_schema(data, schema)


@pytest.mark.parametrize(
    "email",
    [
        "pippo@example.fake",
        "p.pippo@example.fake",
        "p-pippo@example.fake",
        "123pippo@example.fake",
    ],
)
def test_assert_match(email):
    Asserter.assert_match(email, CommonRegex.EMAIL_REGEX)


@pytest.mark.parametrize(
    "email",
    [
        "pippo.example.com",
        "pippo@example",
        "pippo@example.é",
        "p$pippo@example.fake",
    ],
)
def test_assert_no_match(email):
    Asserter.assertion_error(
        f"Test that '{email}' matches '{CommonRegex.EMAIL_REGEX.pattern}' failed",
        lambda: Asserter.assert_match(email, CommonRegex.EMAIL_REGEX),
    )


@pytest.mark.parametrize(
    "occurrences, greater, lesser",
    [
        (3, False, False),
        (2, True, False),
        (4, False, True),
    ],
    ids=[
        "equals",
        "greater",
        "lesser",
    ],
)
def test_assert_occurrences(occurrences, greater, lesser):
    Asserter.assert_occurrences("aabbccaad aaa", "aa", occurrences, greater=greater, lesser=lesser)


@pytest.mark.parametrize(
    "occurrences, greater, lesser, error",
    [
        (4, False, False, "are equals to '4'"),
        (3, True, False, "are greater than '3'"),
        (2, False, True, "are less than '2'"),
    ],
    ids=[
        "equals",
        "greater",
        "lesser",
    ],
)
def test_assert_occurrences_fails(occurrences, greater, lesser, error):
    Asserter.assertion_error(
        f"Test that occurrences of 'aa' in 'aabbccaad aaa' {error} failed",
        lambda: Asserter.assert_occurrences(
            "aabbccaad aaa", "aa", occurrences, greater=greater, lesser=lesser
        ),
    )


@pytest.mark.parametrize(
    # fmt: off
    "status_ok, status_ko, expected, is_in, in_range, greater, lesser, that, error",
    [
        (201,   199,    (201, 203), True,    False,   False,   False, "'199' is in '(201, 203)'",       "199 is NOT one of (201, 203)"),  # noqa: B950 pylint: disable=line-too-long
        (201,   199,    (200, 299), False,   True,    False,   False, "'199' is in range '[200, 299]'", "199 is NOT in range [200, 299]"),  # noqa: B950 pylint: disable=line-too-long
        (400,   199,    300,        False,   False,   True,    False, "'199' is greater than '300'",    "199 is NOT greater than 300"),  # noqa: B950 pylint: disable=line-too-long
        (200,   599,    300,        False,   False,   False,   True,  "'599' is less than '300'",       "599 is NOT less than 300"),  # noqa: B950 pylint: disable=line-too-long
    ],
    ids=[
        "is_in",
        "in_range",
        "greater",
        "lesser",
    ],
    # fmt: on
)
def test_assert_status_code(
    status_ok, status_ko, expected, is_in, in_range, greater, lesser, that, error
):
    Asserter.assert_status_code(
        ObjectDict(status=status_ok),
        code=expected,
        is_in=is_in,
        in_range=in_range,
        greater=greater,
        lesser=lesser,
    )

    Asserter.assertion_error(
        f"Test that {that} failed: status code {error}",
        lambda: Asserter.assert_status_code(
            ObjectDict(status=status_ko),
            code=expected,
            is_in=is_in,
            in_range=in_range,
            greater=greater,
            lesser=lesser,
        ),
    )


@pytest.mark.parametrize(
    "status_ok, status_ko, expected, error",
    [
        (100, 200, StatusType.INFORMATIONAL, "'1' is equals to '2'"),
        (200, 300, StatusType.SUCCESS, "'2' is equals to '3'"),
        (300, 400, StatusType.REDIRECTION, "'3' is equals to '4'"),
        (400, 500, StatusType.CLIENT_ERROR, "'4' is equals to '5'"),
        (500, 100, StatusType.SERVER_ERROR, "'5' is equals to '1'"),
    ],
    ids=[
        "INFORMATIONAL",
        "SUCCESS",
        "REDIRECTION",
        "CLIENT_ERROR",
        "SERVER_ERROR",
    ],
)
def test_assert_status_type(status_ok, status_ko, expected, error):
    Asserter.assert_status_code(ObjectDict(status=status_ok), status_type=expected)

    Asserter.assertion_error(
        f"Test that {error} failed: status code {status_ko} is NOT {expected.name}",
        lambda: Asserter.assert_status_code(ObjectDict(status=status_ko), status_type=expected),
    )


@pytest.mark.parametrize(
    "value, expected, is_in, regex",
    [
        ("value", None, False, False),
        ("value", "value", False, False),
        ("value", "alu", True, False),
        ("value", "[a-z]", False, True),
    ],
    ids=[
        "exists",
        "equals",
        "is_in",
        "regex",
    ],
)
def test_assert_header(value, expected, is_in, regex):
    response = ObjectDict(headers={"X-Hdr": value})
    Asserter.assert_header(response, "X-Hdr", expected, is_in=is_in, regex=regex)


def test_assert_headers():
    Asserter.assert_headers(
        ObjectDict(
            headers={
                "X-Hdr-0": "value-0",
                "X-Hdr-1": "value-1",
                "X-Hdr-2": "value-2",
                "X-Hdr-3": "value-3",
                "X-Hdr-4": "value-4",
            }
        ),
        headers={
            "X-Hdr-0": "value-0",
            "X-Hdr-1": {"value": None, "is_in": False, "regex": False},
            "X-Hdr-2": {"value": "value-2", "is_in": False, "regex": False},
            "X-Hdr-3": {"value": "ue-3", "is_in": True, "regex": False},
            "X-Hdr-4": {"value": "[a-z]-4", "is_in": False, "regex": True},
        },
    )


def test_assert_content_type():
    response = ObjectDict(headers={"content-type": "application/json"})
    Asserter.assert_content_type(response, "json")
