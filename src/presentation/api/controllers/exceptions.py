import logging

from collections.abc import Awaitable, Callable
from functools import partial

from fastapi import FastAPI
from starlette import status
from starlette.requests import Request

from src.application.department.exceptions import DepartmentNotFoundError
from src.domain.common.exceptions import AppError
from src.domain.employee.exceptions import EmployeePositionEmptyError, EmployeeValidationError
from src.presentation.api.controllers.responses import ErrorResponse
from src.presentation.api.controllers.responses.base import ErrorData
from src.presentation.api.controllers.responses.orjson import ORJSONResponse


logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, error_handler(500))
    app.add_exception_handler(EmployeePositionEmptyError, error_handler(500))
    app.add_exception_handler(EmployeeValidationError, error_handler(500))
    app.add_exception_handler(DepartmentNotFoundError, error_handler(404))
    app.add_exception_handler(Exception, unknown_exception_handler)


def error_handler(status_code: int) -> Callable[..., Awaitable[ORJSONResponse]]:
    return partial(app_error_handler, status_code=status_code)


async def app_error_handler(request: Request, err: AppError, status_code: int) -> ORJSONResponse:
    return await handle_error(
        request=request,
        err=err,
        err_data=ErrorData(title=err.title, data=err),
        status=err.status,
        status_code=status_code,
    )


async def handle_error(
    request: Request,
    err: Exception,
    err_data: ErrorData,
    status: int,
    status_code: int,
) -> ORJSONResponse:
    logger.error("Handle error", exc_info=err, extra={"error": err})
    return ORJSONResponse(
        ErrorResponse(error=err_data, status=status_code),
        status_code=status_code,
    )


async def unknown_exception_handler(request: Request, err: Exception) -> ORJSONResponse:
    logger.error("Handle error", exc_info=err, extra={"error": err})
    logger.exception("Unknown error occurred", exc_info=err, extra={"error": err})
    return ORJSONResponse(
        ErrorResponse(error=ErrorData(data=err)),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
