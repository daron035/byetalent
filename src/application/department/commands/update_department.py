import logging

from dataclasses import dataclass

from memediator import EventMediator, Request, RequestHandler

from src.application.common.core.interfaces import UnitOfWork
from src.application.department import dto
from src.application.department.exceptions import CyclicalDepartmentError, DepartmentNotFoundError
from src.application.department.interfaces import DepartmentRepo
from src.domain.common.constants import Empty


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateDepartment(Request[dto.DepartmentTree]):
    id: int
    name: str | Empty | None = Empty.UNSET
    parent_id: int | Empty | None = Empty.UNSET


@dataclass(frozen=True)
class UpdateDepartmentHandler(RequestHandler[UpdateDepartment, dto.DepartmentTree]):
    depart_repo: DepartmentRepo

    mediator: EventMediator
    uow: UnitOfWork

    async def __call__(self, cmd: UpdateDepartment) -> dto.DepartmentTree:
        dept = await self.depart_repo.acquire_by_id(cmd.id)
        if not dept:
            raise DepartmentNotFoundError(cmd.id)

        if cmd.parent_id is not Empty.UNSET:
            new_parent_id: int | None = cmd.parent_id

            if new_parent_id is not None:
                is_cycle = await self.depart_repo.is_cyclical(
                    department_id=cmd.id,
                    new_parent_id=new_parent_id,
                )

                if is_cycle:
                    raise CyclicalDepartmentError

            dept.move_to(new_parent_id)

        if cmd.name is not Empty.UNSET:
            if cmd.name is None:
                raise ValueError("Имя департамента не может быть пустым (None)")
            dept.rename(cmd.name)

        updated_dept = await self.depart_repo.update(dept)

        await self.uow.commit()

        assert updated_dept.oid is not None

        return dto.DepartmentTree(
            id=updated_dept.oid,
            name=updated_dept.name,
            parent_id=updated_dept.parent_id,
            created_at=updated_dept.created_at,
        )
