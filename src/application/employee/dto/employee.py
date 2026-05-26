from dataclasses import dataclass
from datetime import date, datetime

from src.application.common.core.dto import DTO


@dataclass(frozen=True, slots=True)
class CreatedEmployee(DTO):
    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: date | None
    created_at: datetime


@dataclass(slots=True, kw_only=True)
class Employee(DTO):
    id: int
    department_id: int
    full_name: str
    position: str
    created_at: datetime
    hired_at: date | None = None
