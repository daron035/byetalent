import logging

from typing import NoReturn

from sqlalchemy.exc import DBAPIError, IntegrityError

from src.application.common.core.exceptions import RepoError
from src.application.department.exceptions import DepartmentNotFoundError
from src.application.employee.exceptions import EmployeeIdAlreadyExistsError
from src.application.employee.interfaces import EmployeeRepo
from src.domain.employee import entities as ent
from src.infrastructure.persistence.postgres import models as orm

from .base import SQLAlchemyRepo


logger = logging.getLogger(__name__)


class EmployeeRepoImpl(SQLAlchemyRepo, EmployeeRepo):
    async def add(self, employee: ent.Employee) -> None:
        orm_emp = orm.Employee(
            department_id=employee.department_id,
            full_name=employee.full_name,
            position=employee.position,
            hired_at=employee.hired_at,
        )
        self.session.add(orm_emp)
        try:
            await self.session.flush((orm_emp,))
        except IntegrityError as err:
            self._parse_error(err, employee)
        employee.oid = orm_emp.id
        employee.created_at = orm_emp.created_at

    def _parse_error(self, err: DBAPIError, employee: ent.Employee) -> NoReturn:
        orig = err.orig
        driver_error = getattr(orig, "__cause__", None)

        constraint_name = getattr(driver_error, "constraint_name", None)

        match constraint_name:
            case "pk_employees":
                assert employee.oid is not None
                raise EmployeeIdAlreadyExistsError(employee.oid) from err
            case "fk_employees_department_id_departments":
                assert employee.department_id is not None
                raise DepartmentNotFoundError(employee.department_id) from err
            case _:
                logger.error("Unexpected integrity error: %s", constraint_name)
                raise RepoError from err

    def _parse_error2(self, err: DBAPIError, employee: ent.Employee) -> NoReturn:
        orig = err.orig
        driver_error = getattr(orig, "__cause__", None)

        sqlstate = getattr(driver_error, "sqlstate", None)

        match sqlstate:
            # foreign_key_violation
            case "23503":
                raise DepartmentNotFoundError(employee.department_id) from err

            # unique_violation
            case "23505":
                assert employee.oid is not None
                raise EmployeeIdAlreadyExistsError(employee.oid) from err

            case _:
                logger.error(
                    "Unexpected integrity error. sqlstate=%s error=%r",
                    sqlstate,
                    driver_error,
                )
                raise RepoError from err
