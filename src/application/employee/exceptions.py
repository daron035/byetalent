from dataclasses import dataclass

from src.application.common.core.exceptions import ApplicationError


@dataclass(eq=False)
class EmployeeIdAlreadyExistsError(ApplicationError):
    employee_id: int

    @property
    def title(self) -> str:
        return f'A employee with the "{self.employee_id}" employee_id already exists'
