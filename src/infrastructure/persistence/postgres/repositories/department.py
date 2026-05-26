import logging

from typing import NoReturn

from sqlalchemy import delete, literal, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from src.application.common.core.exceptions import RepoError
from src.application.department.dto import DepartmentTree as DepartmentTreeDTO
from src.application.department.exceptions import (
    DepartmentIdAlreadyExistsError,
    DepartmentNameExistsError,
    DepartmentNotFoundError,
    ParentDepartmentNotFoundError,
)
from src.application.department.interfaces import DepartmentReader, DepartmentRepo
from src.application.employee.dto import Employee as EmployeeDTO
from src.domain.department import entities as ent
from src.infrastructure.persistence.postgres import models as orm

from .base import SQLAlchemyRepo


logger = logging.getLogger(__name__)


class DepartmentReaderImpl(SQLAlchemyRepo, DepartmentReader):
    async def get_tree(self, department_id: int, depth: int, include_employees: bool) -> DepartmentTreeDTO | None:
        root_cte = (
            select(
                orm.Department.id,
                orm.Department.name,
                orm.Department.parent_id,
                orm.Department.created_at,
                literal(1).label("current_depth"),
            )
            .where(orm.Department.id == department_id)
            .cte(name="dept_tree", recursive=True)
        )

        recursive_part = (
            select(
                orm.Department.id,
                orm.Department.name,
                orm.Department.parent_id,
                orm.Department.created_at,
                (root_cte.c.current_depth + 1).label("current_depth"),
            )
            .join(orm.Department, orm.Department.parent_id == root_cte.c.id)
            .where(root_cte.c.current_depth < depth)
        )

        statement = select(root_cte.union_all(recursive_part))
        result = await self.session.execute(statement)
        rows = result.all()

        if not rows:
            return None

        dept_map: dict[int, DepartmentTreeDTO] = {}
        root_node = None

        for row in rows:
            dto = DepartmentTreeDTO(id=row.id, name=row.name, parent_id=row.parent_id, created_at=row.created_at)
            dept_map[dto.id] = dto
            if dto.id == department_id:
                root_node = dto

        if include_employees and dept_map:
            emp_stmt = select(orm.Employee).where(orm.Employee.department_id.in_(dept_map.keys()))
            emp_res = await self.session.execute(emp_stmt)

            for emp_row in emp_res.scalars():
                emp_dto = EmployeeDTO(
                    id=emp_row.id,
                    department_id=emp_row.department_id,
                    full_name=emp_row.full_name,
                    position=emp_row.position,
                    hired_at=emp_row.hired_at,
                    created_at=emp_row.created_at,
                )
                dept_map[emp_row.department_id].employees.append(emp_dto)

            for d in dept_map.values():
                d.employees.sort(key=lambda e: e.full_name)

        for dto in dept_map.values():
            if dto.parent_id in dept_map:
                dept_map[dto.parent_id].children.append(dto)

        return root_node


class DepartmentRepoImpl(SQLAlchemyRepo, DepartmentRepo):
    async def acquire_by_id(self, department_id: int) -> ent.Department:
        dept = await self.session.get(orm.Department, department_id)
        if dept is None:
            raise DepartmentNotFoundError(department_id)
        return ent.Department(oid=dept.id, name=dept.name, parent_id=dept.parent_id, created_at=dept.created_at)

    async def is_cyclical(self, department_id: int, new_parent_id: int) -> bool:
        """Проверяет, не приведет ли перенос департамента к образованию цикла."""
        if department_id == new_parent_id:
            return True

        cte = (
            select(orm.Department.id, orm.Department.parent_id)
            .where(orm.Department.id == new_parent_id)
            .cte(name="parent_chain", recursive=True)
        )

        recursive_part = select(orm.Department.id, orm.Department.parent_id).join(
            cte, orm.Department.id == cte.c.parent_id
        )

        statement = select(cte.union_all(recursive_part))
        res = await self.session.execute(statement)
        parent_ids = [row.id for row in res.all()]

        return department_id in parent_ids

    async def add(self, department: ent.Department) -> None:
        orm_dept = orm.Department(name=department.name, parent_id=department.parent_id)
        self.session.add(orm_dept)
        try:
            await self.session.flush((orm_dept,))
        except IntegrityError as err:
            self._parse_error(err, department)
        department.oid = orm_dept.id
        department.created_at = orm_dept.created_at

    async def update(self, department: ent.Department) -> ent.Department:
        stmt = (
            update(orm.Department)
            .where(orm.Department.id == department.oid)
            .values(name=department.name, parent_id=department.parent_id)
            .returning(orm.Department.created_at)
        )
        try:
            res = await self.session.execute(stmt)
        except IntegrityError as err:
            self._parse_error(err, department)

        row = res.fetchone()

        if row:
            department.oid = row.id
            department.created_at = row.created_at

        return department

    async def delete_cascade(self, department_id: int) -> None:
        stmt = delete(orm.Department).where(orm.Department.id == department_id)
        await self.session.execute(stmt)

    async def delete_and_reassign(self, department_id: int, reassign_to_id: int) -> None:
        """Удаляет департамент, предварительно переведя сотрудников в другой департамент."""
        move_emp_stmt = (
            update(orm.Employee)
            .where(orm.Employee.department_id == department_id)
            .values(department_id=reassign_to_id)
        )
        await self.session.execute(move_emp_stmt)

        current_dept = await self.session.get(orm.Department, department_id)
        new_parent = current_dept.parent_id if current_dept else None

        move_dept_stmt = (
            update(orm.Department)
            .where(orm.Department.parent_id == department_id)
            .values(parent_id=new_parent)
        )
        await self.session.execute(move_dept_stmt)

        await self.session.execute(
            delete(orm.Department)
            .where(orm.Department.id == department_id)
        )

    def _parse_error(self, err: DBAPIError, department: ent.Department) -> NoReturn:
        orig = err.orig
        driver_error = getattr(orig, "__cause__", None)

        constraint_name = getattr(driver_error, "constraint_name", None)

        match constraint_name:
            case "pk_departments":
                assert department.oid is not None
                raise DepartmentIdAlreadyExistsError(department.oid) from err
            case "fk_departments_parent_id_departments":
                assert department.parent_id is not None
                raise ParentDepartmentNotFoundError(department.parent_id) from err
            case "uq_departments_name_parent_id":
                raise DepartmentNameExistsError(
                    name=department.name,
                    parent_id=department.parent_id,
                ) from err
            case _:
                logger.error("Unexpected integrity error: %s", constraint_name)
                raise RepoError from err
