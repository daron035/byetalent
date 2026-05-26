from dataclasses import dataclass

from src.domain.common.exceptions.base import DomainError


@dataclass(eq=False)
class EmployeeValidationError(DomainError):
    _text: str

    @property
    def title(self) -> str:
        return self._text


@dataclass(eq=False)
class EmployeePositionEmptyError(DomainError):
    @property
    def title(self) -> str:
        return "Должность сотрудника не может быть пустой"
