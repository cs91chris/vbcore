import pytest

from vbcore.base import BaseDTO, Decorator, LogError, Singleton, Static

_ = BaseDTO, Singleton, Static, Decorator, LogError


@pytest.mark.skip("implement me")
def test_base_dto():
    pass


@pytest.mark.skip("implement me")
def test_singleton():
    pass


@pytest.mark.skip("implement me")
def test_static_class():
    pass


@pytest.mark.skip("implement me")
def test_decorator_idempotent():
    pass


@pytest.mark.skip("implement me")
def test_log_error_decorator():
    pass
