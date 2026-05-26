from datetime import datetime
from unittest.mock import AsyncMock

import src.domain.department.entities as ent

from src.application.department.commands import UpdateDepartment, UpdateDepartmentHandler
from tests.mocks.department_repo import FakeDepartmentRepo
from tests.mocks.uow import UnitOfWorkMock


async def test_update_department_handler_success(
    repo: FakeDepartmentRepo,
    uow: UnitOfWorkMock,
):
    existing_dept = ent.Department(oid=1, name="Old IT", parent_id=None, created_at=datetime.utcnow())
    repo.seed_data(existing_dept)

    handler = UpdateDepartmentHandler(depart_repo=repo, uow=uow, mediator=AsyncMock())

    command = UpdateDepartment(id=1, name="New IT")
    await handler(command)

    updated_dept = await repo.acquire_by_id(1)
    assert updated_dept.name == "New IT"

    assert uow.committed is True
    assert uow.rolled_back is False
