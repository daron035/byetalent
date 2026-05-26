from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.common.entities.aggregate_root import AggregateRoot
from src.domain.department.exceptions import (
    DepartmentNameEmptyError,
    DepartmentNameTooLongError,
    DepartmentSelfParentError,
)
from src.domain.employee.entities import Employee


@dataclass
class Department(AggregateRoot):
    oid: int | None
    name: str
    parent_id: int | None
    created_at: datetime

    employees: list[Employee] = field(default_factory=list)
    children: list[Department] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        parent_id: int | None = None,
        oid: int | None = None,
    ) -> Department:
        now = datetime.now(UTC)
        clean_name = cls._normalize_name(name)

        return cls(
            oid=oid,
            name=clean_name,
            parent_id=parent_id,
            created_at=now,
        )

    def rename(self, name: str) -> None:
        normalized = self._normalize_name(name)
        self.name = normalized

    def move_to(self, new_parent_id: int | None) -> None:
        if self.oid is not None and self.oid == new_parent_id:
            raise DepartmentSelfParentError
        self.parent_id = new_parent_id

    @staticmethod
    def _normalize_name(name: str) -> str:
        clean_name = name.strip()
        if not clean_name:
            raise DepartmentNameEmptyError
        if len(clean_name) > 200:
            raise DepartmentNameTooLongError
        return clean_name
