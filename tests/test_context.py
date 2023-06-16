from dataclasses import dataclass

import pytest

from vbcore.context import ContextCorrelationId
from vbcore.tester.asserter import Asserter


@dataclass(frozen=True, kw_only=True)
class MyContext(ContextCorrelationId):
    user_id: str


def test_context_metadata_empty() -> None:
    with pytest.raises(LookupError):
        _ = MyContext.get()


def test_context_metadata_set() -> None:
    MyContext.set(MyContext(user_id="user-id", correlation_id="correlation-id"))
    metadata = MyContext.get()

    Asserter.assert_equals(metadata.user_id, "user-id")
    Asserter.assert_equals(metadata.correlation_id, "correlation-id")


def test_context_metadata_set_kwargs() -> None:
    MyContext.set(user_id="user-id", correlation_id="correlation-id")
    metadata = MyContext.get()

    Asserter.assert_equals(metadata.user_id, "user-id")
    Asserter.assert_equals(metadata.correlation_id, "correlation-id")


def test_context_correlation_id() -> None:
    correlation_id = ContextCorrelationId.generate_correlation_id()
    Asserter.assert_true(ContextCorrelationId.check_correlation_id(correlation_id))
