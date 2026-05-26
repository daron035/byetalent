from dataclasses import dataclass

from src.application.common.core.exceptions import ApplicationError


@dataclass(eq=False)
class DepartmentNotFoundError(ApplicationError):
    department_id: int

    @property
    def title(self) -> str:
        return f"Department with id={self.department_id} not found"


@dataclass(eq=False)
class DepartmentNameExistsError(ApplicationError):
    name: str
    parent_id: int | None

    @property
    def title(self) -> str:
        return "Department with this name already exists in the target parent."


@dataclass(eq=False)
class DepartmentIdAlreadyExistsError(ApplicationError):
    department_id: int

    @property
    def title(self) -> str:
        return f'A department with the "{self.department_id}" department_id already exists'


@dataclass(eq=False)
class ParentDepartmentNotFoundError(ApplicationError):
    parent_id: int

    @property
    def title(self) -> str:
        return f"Parent department not found: {self.parent_id}"


@dataclass(eq=False)
class CyclicalDepartmentError(ApplicationError):
    @property
    def title(self) -> str:
        return "The move operation would create a cycle"


@dataclass(eq=False)
class MissingReassignDepartmentIdError(ApplicationError):
    @property
    def title(self) -> str:
        return "The 'reassign_to_department_id' parameter is required when using 'reassign' mode"


@dataclass(eq=False)
class InvalidReassignTargetError(ApplicationError):
    @property
    def title(self) -> str:
        return "Employees cannot be reassigned to the department being deleted"
