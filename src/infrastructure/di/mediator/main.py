import logging

from dishka import AsyncContainer
from memediator import Mediator, MediatorImpl
from memediator.ioc import DishkaIoc
from memediator.middlewares.logging import LoggingMiddleware

from src.application.department.commands import (
    CreateDepartment,
    CreateDepartmentHandler,
    DeleteDepartment,
    DeleteDepartmentHandler,
    UpdateDepartment,
    UpdateDepartmentHandler,
)
from src.application.department.queries import GetDepartmentById, GetDepartmentByIdHandler
from src.application.employee.commands import CreateEmployee, CreateEmployeeHandler
from src.domain.common.events import Event
from src.infrastructure.log.event_handler import EventLogger


async def build_mediator(container: AsyncContainer) -> Mediator:
    middlewares = (LoggingMiddleware(level=logging.DEBUG),)
    mediator = MediatorImpl(ioc=DishkaIoc(container), middlewares=middlewares)

    # Commands
    mediator.register_request_handler(CreateDepartment, CreateDepartmentHandler)
    mediator.register_request_handler(UpdateDepartment, UpdateDepartmentHandler)
    mediator.register_request_handler(DeleteDepartment, DeleteDepartmentHandler)

    mediator.register_request_handler(CreateEmployee, CreateEmployeeHandler)

    # Queries
    mediator.register_request_handler(GetDepartmentById, GetDepartmentByIdHandler)

    # Events
    mediator.register_event_handler(Event, EventLogger)

    return mediator
