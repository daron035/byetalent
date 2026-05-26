from dataclasses import dataclass, field
from datetime import datetime

from src.application.common.core.dto import DTO
from src.application.employee.dto import Employee


@dataclass(frozen=True, slots=True)
class CreatedDepartment(DTO):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime


@dataclass(slots=True, kw_only=True)
class DepartmentTree(DTO):
    id: int
    name: str
    created_at: datetime
    parent_id: int | None = None

    employees: list[Employee] = field(default_factory=list)
    children: list[DepartmentTree] = field(default_factory=list)
