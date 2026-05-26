import logging

from dataclasses import asdict, dataclass
from datetime import date

from memediator import EventMediator, Request, RequestHandler

from src.application.common.core.interfaces import UnitOfWork
from src.application.employee import dto
from src.application.employee.interfaces import EmployeeRepo
from src.domain.employee.entities import Employee


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateEmployee(Request[dto.CreatedEmployee]):
    department_id: int
    full_name: str
    position: str
    hired_at: date | None


@dataclass(frozen=True)
class CreateEmployeeHandler(RequestHandler[CreateEmployee, dto.CreatedEmployee]):
    depart_repo: EmployeeRepo

    mediator: EventMediator
    uow: UnitOfWork

    async def __call__(self, cmd: CreateEmployee) -> dto.CreatedEmployee:
        employee = Employee.create(**asdict(cmd))

        await self.depart_repo.add(employee)

        assert employee.oid is not None

        return dto.CreatedEmployee(
            id=employee.oid,
            department_id=employee.department_id,
            full_name=employee.full_name,
            position=employee.position,
            hired_at=employee.hired_at,
            created_at=employee.created_at,
        )
