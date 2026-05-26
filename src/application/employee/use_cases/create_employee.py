from dataclasses import dataclass
from typing import Any

from memediator import Mediator

from src.application.common.core.interfaces import UnitOfWork, UseCase
from src.application.employee.commands import CreateEmployee


@dataclass(frozen=True)
class CreateEmployeeUseCase(UseCase):
    mediator: Mediator
    uow: UnitOfWork

    async def execute(self, cmd: CreateEmployee) -> Any:
        result = await self.mediator.send(cmd, enter_scope=True)

        await self.uow.commit()

        return result
