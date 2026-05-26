import pytest

from tests.mocks.department_repo import FakeDepartmentRepo
from tests.mocks.uow import UnitOfWorkMock


@pytest.fixture
def repo() -> FakeDepartmentRepo:
    return FakeDepartmentRepo()


@pytest.fixture
def uow() -> UnitOfWorkMock:
    return UnitOfWorkMock()
