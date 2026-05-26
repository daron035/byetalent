from src.domain.common.exceptions.base import DomainError


class DepartmentNameEmptyError(DomainError):
    @property
    def title(self) -> str:
        return "Название подразделения не может быть пустым"


class DepartmentNameTooLongError(DomainError):
    @property
    def title(self) -> str:
        return "Название подразделения не может быть длиннее 200 символов"


class DepartmentSelfParentError(DomainError):
    @property
    def title(self) -> str:
        return "Подразделение не может быть родителем самому себе"
