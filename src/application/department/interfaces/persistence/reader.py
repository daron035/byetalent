from typing import Protocol

from src.application.department.dto import DepartmentTree as DepartmentTreeDTO


class DepartmentReader(Protocol):
    async def get_tree(self, department_id: int, depth: int, include_employees: bool) -> DepartmentTreeDTO | None: ...
