from typing import Annotated, Any

from fastapi import APIRouter, Body, Path, Query, status

from src.application.department import dto
from src.application.department.commands import CreateDepartment, DeleteDepartment, UpdateDepartment
from src.application.department.commands.delete_department import DeleteMode
from src.application.department.dto import DepartmentTree as DepartmentTreeDTO
from src.application.department.queries import GetDepartmentById
from src.application.department.use_cases import CreateDepartmentUseCase
from src.infrastructure.di import mediator
from src.infrastructure.di.proxy import use_case
from src.presentation.api.controllers.requests import CreateDepartmentRequest, DepartmentUpdatePatch


department_router = APIRouter(
    tags=["departments"],
)


@department_router.post(
    "/departments",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new department",
    description="Creates a new department using the provided payload.",
)
async def create_department(
    data: Annotated[
        CreateDepartmentRequest,
        Body(description="Data required to create a new department"),
    ],
) -> dto.CreatedDepartment:
    command = CreateDepartment(**data.model_dump())

    return await use_case.execute(CreateDepartmentUseCase, command)


@department_router.get(
    "/departments/{id}",
    response_model=DepartmentTreeDTO,
    summary="Get department tree",
    description="Returns department details, its employees, and all nested subtrees up to the specified depth.",
)
async def get_department_tree(
    id: Annotated[int, Path(description="The unique identifier of the department")],
    depth: Annotated[int, Query(description="Depth of the nested sub-departments in the response", ge=1, le=5)] = 1,
    include_employees: Annotated[
        bool, Query(description="Whether to include the list of employees for each department")
    ] = True,
) -> DepartmentTreeDTO:
    command = GetDepartmentById(id=id, depth=depth, include_employees=include_employees)
    department = await mediator.send(command)

    return department


@department_router.patch(
    "/departments/{id}",
    response_model=DepartmentTreeDTO,
    response_model_exclude={"employees", "children"},
    summary="Update department details",
    description="Partially updates an existing department's information.",
)
async def update_department(
    id: Annotated[int, Path(description="The unique identifier of the department to update")],
    payload: Annotated[DepartmentUpdatePatch, Body(description="Fields to update within the department")],
) -> Any:
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        # If no fields are changed, we can either raise an exception
        # or return the current department state via a separate Query.
        pass

    command = UpdateDepartment(id, **update_data)
    department = await mediator.send(command)

    return department


@department_router.delete(
    "/departments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a department",
    description="Deletes a department. Can either cascade the deletion to everything inside or reassign employees to another department.",
)
async def delete_department(
    id: Annotated[int, Path(description="The unique identifier of the department to delete")],
    mode: Annotated[
        DeleteMode,
        Query(description="Deletion mode: 'cascade' (delete all nested elements) or 'reassign' (transfer employees)"),
    ],
    reassign_to_department_id: Annotated[
        int | None,
        Query(description="Target department ID for transferred employees (required if mode is 'reassign')"),
    ] = None,
) -> None:
    command = DeleteDepartment(id=id, mode=mode, reassign_to_id=reassign_to_department_id)

    await mediator.send(command)
