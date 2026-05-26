from typing import Protocol

from src.domain.employee.entities import Employee


class EmployeeRepo(Protocol):
    async def add(self, employee: Employee) -> None: ...
