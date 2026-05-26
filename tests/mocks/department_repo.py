import src.domain.department.entities as ent

from src.application.department.exceptions import DepartmentNotFoundError
from src.application.department.interfaces.persistence.repo import DepartmentRepo


class FakeDepartmentRepo(DepartmentRepo):
    def __init__(self):
        self._data: dict[int, ent.Department] = {}

    def seed_data(self, department: ent.Department) -> None:
        self._data[department.oid] = department

    async def acquire_by_id(self, department_id: int) -> ent.Department:
        dept = self._data.get(department_id)
        if dept is None:
            raise DepartmentNotFoundError(department_id)
        return dept
