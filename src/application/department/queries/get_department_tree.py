import logging

from dataclasses import dataclass
from typing import Any

from memediator import Request, RequestHandler

from src.application.department.interfaces import DepartmentReader


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetDepartmentById(Request[Any]):
    id: int
    depth: int
    include_employees: bool


@dataclass(frozen=True)
class GetDepartmentByIdHandler(RequestHandler[GetDepartmentById, Any]):
    department_reader: DepartmentReader

    async def __call__(self, query: GetDepartmentById) -> Any:
        department = await self.department_reader.get_tree(
            department_id=query.id, depth=query.depth, include_employees=query.include_employees
        )
        return department
