from dataclasses import dataclass

from memediator import Mediator

from src.application.common.core.interfaces import UnitOfWork, UseCase
from src.application.department import dto
from src.application.department.commands import CreateDepartment


@dataclass(frozen=True)
class CreateDepartmentUseCase(UseCase):
    mediator: Mediator
    uow: UnitOfWork

    async def execute(self, cmd: CreateDepartment) -> dto.CreatedDepartment:
        created_department = await self.mediator.send(cmd, enter_scope=True)

        await self.uow.commit()

        return created_department
