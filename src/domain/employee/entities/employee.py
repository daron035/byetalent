from dataclasses import dataclass
from datetime import UTC, date, datetime

from src.domain.common.entities.aggregate_root import AggregateRoot
from src.domain.employee.exceptions import EmployeePositionEmptyError, EmployeeValidationError


@dataclass
class Employee(AggregateRoot):
    oid: int | None  # TODO: id от клиента или default_factory
    department_id: int
    full_name: str
    position: str
    hired_at: date | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        department_id: int,
        full_name: str,
        position: str,
        oid: int | None = None,
        hired_at: date | None = None,
    ) -> Employee:
        now = datetime.now(UTC)

        # TODO: Value object w/ _validate

        clean_full_name = full_name.strip()
        clean_position = position.strip()

        if not clean_full_name:
            raise EmployeeValidationError("ФИО сотрудника не может быть пустым.")
        if not clean_position:
            raise EmployeeValidationError("Должность не может быть пустой.")
        if department_id <= 0:
            raise EmployeeValidationError("Некорректный ID подразделения.")

        return cls(
            oid=oid,
            department_id=department_id,
            full_name=clean_full_name,
            position=clean_position,
            hired_at=hired_at,
            created_at=now,
        )

    def change_position(self, position: str) -> None:
        normalized = position.strip()

        if not normalized:
            raise EmployeePositionEmptyError

        self.position = normalized
