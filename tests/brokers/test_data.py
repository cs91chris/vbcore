from vbcore.brokers.data import Header
from vbcore.tester.asserter import Asserter


def test_headers_to_dict(correlation_id: str, timestamp: float) -> None:
    Asserter.assert_equals(
        Header(timestamp=timestamp, correlation_id=correlation_id).to_dict(),
        {
            "timestamp": str(timestamp),
            "correlation_id": correlation_id,
        },
    )


def test_headers_from_dict(correlation_id: str, timestamp: float) -> None:
    Asserter.assert_equals(
        Header(timestamp=timestamp, correlation_id=correlation_id),
        Header.from_dict(
            timestamp=str(timestamp),
            correlation_id=correlation_id,
        ),
    )


def test_headers_default_unique() -> None:
    Asserter.assert_different(Header(), Header())
    Asserter.assert_different(Header(), Header.from_dict(**Header().to_dict()))
