import logging

from dataclasses import dataclass
from enum import Enum

from memediator import EventMediator, Request, RequestHandler

from src.application.common.core.interfaces import UnitOfWork
from src.application.department.exceptions import (
    DepartmentNotFoundError,
    InvalidReassignTargetError,
    MissingReassignDepartmentIdError,
)
from src.application.department.interfaces import DepartmentRepo


logger = logging.getLogger(__name__)


class DeleteMode(Enum):
    CASCADE = "cascade"
    REASSIGN = "reassign"


@dataclass(frozen=True)
class DeleteDepartment(Request[None]):
    id: int
    mode: DeleteMode
    reassign_to_id: int | None = None


@dataclass(frozen=True)
class DeleteDepartmentHandler(RequestHandler[DeleteDepartment, None]):
    depart_repo: DepartmentRepo

    mediator: EventMediator
    uow: UnitOfWork

    async def __call__(self, cmd: DeleteDepartment) -> None:
        dept = await self.depart_repo.acquire_by_id(cmd.id)
        if not dept:
            raise DepartmentNotFoundError(cmd.id)

        if cmd.mode == DeleteMode.REASSIGN:
            if not cmd.reassign_to_id:
                raise MissingReassignDepartmentIdError

            if cmd.id == cmd.reassign_to_id:
                raise InvalidReassignTargetError

            target_dept = await self.depart_repo.acquire_by_id(cmd.reassign_to_id)
            if not target_dept:
                raise DepartmentNotFoundError(cmd.reassign_to_id)

            await self.depart_repo.delete_and_reassign(
                department_id=cmd.id,
                reassign_to_id=cmd.reassign_to_id,
            )

        else:
            await self.depart_repo.delete_cascade(cmd.id)

        await self.uow.commit()
