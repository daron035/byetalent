from fastapi import FastAPI

from .default import default_router
from .departments import department_router
from .employee import employee_router
from .exceptions import setup_exception_handlers
from .healthcheck import healthcheck_router


def setup_controllers(app: FastAPI) -> None:
    app.include_router(default_router)
    app.include_router(healthcheck_router)
    app.include_router(department_router)
    app.include_router(employee_router)

    setup_exception_handlers(app)
