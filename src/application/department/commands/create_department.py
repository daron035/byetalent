import logging

from dataclasses import dataclass

from memediator import EventMediator, Request, RequestHandler

from src.application.common.core.interfaces import UnitOfWork
from src.application.department import dto
from src.application.department.interfaces import DepartmentRepo
from src.domain.department.entities import Department


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateDepartment(Request[dto.CreatedDepartment]):
    name: str
    parent_id: int | None


@dataclass(frozen=True)
class CreateDepartmentHandler(RequestHandler[CreateDepartment, dto.CreatedDepartment]):
    depart_repo: DepartmentRepo

    mediator: EventMediator
    uow: UnitOfWork

    async def __call__(self, cmd: CreateDepartment) -> dto.CreatedDepartment:
        department = Department.create(cmd.name, cmd.parent_id)

        await self.depart_repo.add(department)

        assert department.oid is not None

        return dto.CreatedDepartment(
            id=department.oid,
            name=department.name,
            parent_id=department.parent_id,
            created_at=department.created_at,
        )
