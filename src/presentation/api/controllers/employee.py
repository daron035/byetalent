from typing import Annotated

from fastapi import APIRouter, Body, Path, status

from src.application.employee import dto
from src.application.employee.commands import CreateEmployee
from src.application.employee.use_cases import CreateEmployeeUseCase
from src.infrastructure.di.proxy import use_case
from src.presentation.api.controllers.requests import CreateEmployeeRequest


employee_router = APIRouter(
    tags=["employees"],
)


@employee_router.post(
    "/{id}/employees",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
    description="Creates a new employee and assigns them to the specified department.",
)
async def create_employee(
    id: Annotated[int, Path(description="The ID of the department where the employee will be assigned")],
    data: Annotated[CreateEmployeeRequest, Body(description="Data required to create a new employee")],
) -> dto.CreatedEmployee:
    command = CreateEmployee(**data.model_dump(), department_id=id)

    return await use_case.execute(CreateEmployeeUseCase, command)
