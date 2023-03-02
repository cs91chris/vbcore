import enum
import functools
import re
import typing as t
from functools import partial

import pytest

from vbcore.http import httpcode
from vbcore.http.headers import HeaderEnum
from vbcore.lambdas import Op
from vbcore.types import OptAny, OptInt, OptStr, RegexType

try:
    from vbcore.jsonschema.support import JSONSchema
except ImportError:  # pragma: no cover
    JSONSchema = object  # type: ignore

CallBackType = t.Callable[[t.Any, t.Any], bool]


class Operator(enum.Enum):
    # fmt: off
    IS_SUBCLASS = issubclass,     "'{actual}' is subclass of '{expected}'"             # noqa: E221
    IS_INSTANCE = isinstance,     "'{actual}' is instance of '{expected}'"             # noqa: E221
    EQUALS      = Op.eq,          "'{actual}' is equals to '{expected}'"               # noqa: E221
    NOT_EQUALS  = Op.ne,          "'{actual}' is different from '{expected}'"          # noqa: E221
    IS          = Op.is_,         "'{actual}' is '{expected}'"                         # noqa: E221
    IS_NOT      = Op.is_not,      "'{actual}' is not '{expected}'"                     # noqa: E221
    IN          = Op.in_,         "'{actual}' is in '{expected}'"                      # noqa: E221
    NOT_IN      = Op.not_in,      "'{actual}' is not in '{expected}'"                  # noqa: E221
    GREATER     = Op.gt,          "'{actual}' is greater than '{expected}'"            # noqa: E221
    GREATER_EQ  = Op.ge,          "'{actual}' is greater than/equals to '{expected}'"  # noqa: E221
    LESSER      = Op.lt,          "'{actual}' is less than '{expected}'"               # noqa: E221
    LESSER_EQ   = Op.le,          "'{actual}' is less than/equals to '{expected}'"     # noqa: E221
    ALL_IN      = Op.allin,       "'{actual}' is all in '{expected}'"                  # noqa: E221
    IS_TRUE     = Op.is_true,     "'{actual}' is True"                                 # noqa: E221
    IS_FALSE    = Op.is_false,    "'{actual}' is False"                                # noqa: E221
    IS_NONE     = Op.is_none,     "'{actual}' is None"                                 # noqa: E221
    IS_NOT_NONE = Op.is_not_none, "'{actual}' is not None"                             # noqa: E221
    # fmt: on


# pylint: disable=too-many-public-methods
class BaseAssert:
    exception = AssertionError
    fail_message = "Test that {that} failed{error}"
    operators = Operator

    @classmethod
    def assertion_error(cls, message: str, callback: t.Callable, *args, **kwargs):
        with pytest.raises(AssertionError) as error:
            callback(*args, **kwargs)

        Asserter.assert_equals(error.value.args, (message,))

    @classmethod
    def with_assertion_error(cls, message: str):
        def _inner(callback):
            @functools.wraps(callback)
            def wrapper(*args, **kwargs):
                cls.assertion_error(message, callback, *args, **kwargs)

            return wrapper

        return _inner

    @classmethod
    def fail(cls, that: OptStr = None, error: OptStr = None):
        if not that:
            raise cls.exception(error)
        raise cls.exception(
            cls.fail_message.format(that=that, error=f": {error}" if error else "")
        )

    @classmethod
    def assert_that(
        cls,
        func: CallBackType,
        actual: t.Any,
        expected: OptAny = None,
        that: OptStr = None,
        error: OptStr = None,
    ):
        if __debug__:
            if not func(actual, expected):
                cls.fail(that, error)

    @classmethod
    def assert_operator(
        cls,
        operator: Operator,
        actual: t.Any,
        expected: OptAny = None,
        error: OptStr = None,
    ):
        callback, that = operator.value
        that = that.format(actual=actual, expected=expected)
        cls.assert_that(callback, actual, expected, that, error)

    @classmethod
    def assert_equals(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.EQUALS, actual, expected, error)

    @classmethod
    def assert_different(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.NOT_EQUALS, actual, expected, error)

    @classmethod
    def assert_is(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.IS, actual, expected, error)

    @classmethod
    def assert_is_not(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.IS_NOT, actual, expected, error)

    @classmethod
    def assert_true(cls, actual: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.IS_TRUE, actual, error=error)

    @classmethod
    def assert_false(cls, actual: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.IS_FALSE, actual, error=error)

    @classmethod
    def assert_none(cls, actual: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.IS_NONE, actual, error=error)

    @classmethod
    def assert_not_none(cls, actual: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.IS_NOT_NONE, actual, error=error)

    @classmethod
    def assert_in(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.IN, actual, expected, error)

    @classmethod
    def assert_not_in(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.NOT_IN, actual, expected, error)

    @classmethod
    def assert_allin(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.ALL_IN, actual, expected, error)

    @classmethod
    def assert_greater(
        cls, actual: t.Any, expected: t.Any, equals: bool = False, error: OptStr = None
    ):
        _operator = cls.operators.GREATER_EQ if equals else cls.operators.GREATER
        cls.assert_operator(_operator, actual, expected, error)

    @classmethod
    def assert_lesser(
        cls, actual: t.Any, expected: t.Any, equals: bool = False, error: OptStr = None
    ):
        _operator = cls.operators.LESSER_EQ if equals else cls.operators.LESSER
        cls.assert_operator(_operator, actual, expected, error)

    @classmethod
    def assert_isinstance(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.IS_INSTANCE, actual, expected, error)

    @classmethod
    def assert_issubclass(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        cls.assert_operator(cls.operators.IS_SUBCLASS, actual, expected, error)

    @classmethod
    def assert_range(
        cls,
        actual: t.Any,
        expected: t.Any,
        error: OptStr = None,
        closed: bool = False,
        left: bool = False,
        right: bool = False,
    ):
        callback = Op.in_range
        low, high = expected[0], expected[1]
        repr_range = f"({low}, {high})"

        if closed is True or (left and right):
            callback = partial(callback, closed=True)
            repr_range = f"[{low}, {high}]"
        elif left is True:
            callback = partial(callback, left=True)
            repr_range = f"[{low}, {high})"
        elif right is True:
            callback = partial(callback, right=True)
            repr_range = f"({low}, {high}]"

        cls.assert_that(
            callback,
            error=error,
            actual=actual,
            expected=expected,
            that=f"'{actual}' is in range '{repr_range}'",
        )


class IterablesMixin(BaseAssert):
    @classmethod
    def assert_len(cls, actual: t.Any, expected: t.Any, error: OptStr = None):
        callback, _ = Operator.EQUALS.value
        that = f"len is {expected}"
        error = error or f"actual len is {len(actual)}"
        cls.assert_that(callback, len(actual), expected, that, error)

    @classmethod
    def assert_is_empty_list(cls, actual: t.Any, error: OptStr = None):
        callback, _ = Operator.EQUALS.value
        cls.assert_that(callback, actual, [], f"'{actual}' is empty list", error)

    @classmethod
    def assert_is_empty_tuple(cls, actual: t.Any, error: OptStr = None):
        callback, _ = Operator.EQUALS.value
        cls.assert_that(callback, actual, (), f"'{actual}' is empty tuple", error)

    @classmethod
    def assert_is_empty_set(cls, actual, error: OptStr = None):
        callback, _ = Operator.EQUALS.value
        cls.assert_that(callback, actual, set(), f"'{actual}' is empty set", error)

    @classmethod
    def assert_is_empty_dict(cls, actual, error: OptStr = None):
        callback, _ = Operator.EQUALS.value
        cls.assert_that(callback, actual, {}, f"'{actual}' is empty dict", error)

    @classmethod
    def assert_not_empty_list(cls, actual: t.Any, error: OptStr = None):
        callback, _ = Operator.NOT_EQUALS.value
        cls.assert_that(callback, actual, [], f"'{actual}' is not empty list", error)

    @classmethod
    def assert_not_empty_tuple(cls, actual: t.Any, error: OptStr = None):
        callback, _ = Operator.NOT_EQUALS.value
        cls.assert_that(callback, actual, (), f"'{actual}' is not empty tuple", error)

    @classmethod
    def assert_not_empty_set(cls, actual, error: OptStr = None):
        callback, _ = Operator.NOT_EQUALS.value
        cls.assert_that(callback, actual, set(), f"'{actual}' is not empty set", error)

    @classmethod
    def assert_not_empty_dict(cls, actual, error: OptStr = None):
        callback, _ = Operator.NOT_EQUALS.value
        cls.assert_that(callback, actual, {}, f"'{actual}' is not empty dict", error)


class JSONValidatorMixin(BaseAssert, JSONSchema):
    @classmethod
    def assert_json_schema(
        cls, data: dict, schema: t.Union[dict, str], strict: bool = True
    ):
        cls.assert_different(JSONSchema, object, error="you must install jsonschema")
        if strict and not schema:
            cls.assert_that(
                lambda a, e: a is not None, actual=schema, error="Missing schema"
            )
        try:
            cls.validate(data, schema, raise_exc=True)
            valid, message = True, None
        except cls.service.ValidationError as exc:
            valid, message = False, cls.error_report(exc, data)

        cls.assert_that(
            lambda a, e: a is True,
            actual=valid,
            error=f"Test that json is valid failed, got: {message}",
        )


class RegexMixin(BaseAssert):
    @classmethod
    def regex_find(
        cls, data: str, pattern: RegexType, index: OptInt = None
    ) -> t.Optional[t.Union[t.List[str], str]]:
        _pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        occ = re.findall(_pattern, data)
        if index is not None:
            if len(occ) > index:
                return occ[index]
            return None
        return occ

    @classmethod
    def regex_match(cls, data: str, pattern: RegexType) -> bool:
        _pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        return bool(re.search(_pattern, data))

    @classmethod
    def assert_match(cls, actual: str, expected: RegexType, error: OptStr = None):
        regex = expected if isinstance(expected, str) else expected.pattern
        cls.assert_that(
            cls.regex_match,
            error=error,
            that=f"'{actual}' matches '{regex}'",
            actual=actual,
            expected=expected,
        )

    @classmethod
    def assert_occurrences(
        cls,
        actual: str,
        expected: RegexType,
        occurrences: int,
        error: OptStr = None,
        greater: bool = False,
        lesser: bool = False,
    ):
        def find_all(a, e):
            tmp = len(cls.regex_find(a, e))
            if greater:
                return Op.gt(tmp, occurrences)
            if lesser:
                return Op.lt(tmp, occurrences)
            return Op.eq(tmp, occurrences)

        opmess = "equals to"
        if greater:
            opmess = "greater than"
        elif lesser:
            opmess = "less than"

        that = f"occurrences of '{expected}' in '{actual}' are {opmess} '{occurrences}'"
        cls.assert_that(
            find_all, error=error, that=that, actual=actual, expected=expected
        )


class HttpAsserter(BaseAssert):
    @classmethod
    def assert_status_code(
        cls,
        response,
        code: t.Optional[t.Union[int, t.Iterable[int]]] = None,
        status_type: httpcode.StatusType = httpcode.StatusType.SUCCESS,
        in_range: bool = False,
        is_in: bool = False,
        greater: bool = False,
        lesser: bool = False,
    ):
        status_code = response.status_code or response.status
        prefix_mess = f"status code {status_code} is NOT"

        if code is None:
            resp_status_type = httpcode.StatusType(status_code)
            cls.assert_equals(
                status_type,
                resp_status_type,
                error=f"{prefix_mess} {status_type.name}",
            )
        elif isinstance(code, (list, tuple)):
            if in_range is True:
                message = f"{prefix_mess} in range {list(code)}"
                cls.assert_range(status_code, code, error=message, closed=True)
            elif is_in is True:
                message = f"{prefix_mess} one of {code}"
                cls.assert_in(status_code, code, error=message)
            else:
                cls.fail(
                    error="one of (is_in, in_range) must be true if a list of codes is given"
                )
        else:
            if greater is True:
                message = f"{prefix_mess} greater than {code}"
                cls.assert_greater(status_code, code, error=message)
            elif lesser is True:
                message = f"{prefix_mess} less than {code}"
                cls.assert_lesser(status_code, code, error=message)
            else:
                message = f"{prefix_mess} {code}"
                cls.assert_equals(status_code, code, error=message)

    @classmethod
    def assert_header(
        cls,
        response,
        name: str,
        value: OptStr = None,
        is_in: bool = False,
        regex: bool = False,
    ):
        header = response.headers.get(name) or ""

        if value is None:
            cls.assert_in(
                actual=name,
                expected=response.headers,
                error=f"header '{name}' not exists",
            )
        elif is_in is True:
            cls.assert_in(
                actual=value,
                expected=header,
                error=f"value '{value}' is not in header '{name}: {header}'",
            )
        elif regex is True:
            RegexMixin.assert_match(
                actual=header,
                expected=value,
                error=f"header '{name}: {header}' does not match '{value}'",
            )
        else:
            cls.assert_equals(
                actual=value,
                expected=header,
                error=f"header '{name}: {header}' is different from: '{value}'",
            )

    @classmethod
    def assert_headers(cls, response, headers: t.Dict[str, t.Union[dict, t.Any]]):
        """

        :param response:
        :param headers: {"name": {"value": "", "is_in": False, "regex": None}}
        :return:
        """
        for k, v in headers.items():
            if isinstance(v, dict):
                cls.assert_header(response, name=k, **v)
            else:
                cls.assert_header(response, name=k, value=str(v))

    @classmethod
    def assert_content_type(
        cls, response, value: OptStr = None, exact: bool = False, regex: bool = False
    ):
        cls.assert_header(
            response,
            name=HeaderEnum.CONTENT_TYPE.value,
            value=value,
            is_in=not exact,
            regex=regex,
        )


class Asserter(
    RegexMixin,
    IterablesMixin,
    JSONValidatorMixin,
    HttpAsserter,
):
    """single interface that inherits all Asserter mixins"""
