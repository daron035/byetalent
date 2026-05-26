# tests/domain/department/test_department.py

from datetime import UTC, datetime

import pytest

from src.domain.department.entities import Department
from src.domain.department.exceptions import (
    DepartmentNameEmptyError,
    DepartmentNameTooLongError,
    DepartmentSelfParentError,
)


def test_create_department_trims_name_and_sets_fields() -> None:
    before = datetime.now(UTC)

    dept = Department.create(
        name="  Backend  ",
        parent_id=10,
        oid=1,
    )

    after = datetime.now(UTC)

    assert dept.oid == 1
    assert dept.name == "Backend"
    assert dept.parent_id == 10
    assert dept.created_at.tzinfo == UTC
    assert before <= dept.created_at <= after
    assert dept.employees == []
    assert dept.children == []


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("", DepartmentNameEmptyError),
        ("   ", DepartmentNameEmptyError),
        ("\n\t ", DepartmentNameEmptyError),
    ],
)
def test_create_department_rejects_empty_name(name: str, expected: type[Exception]) -> None:
    with pytest.raises(expected):
        Department.create(name=name)


def test_create_department_rejects_too_long_name() -> None:
    name = "a" * 201

    with pytest.raises(DepartmentNameTooLongError):
        Department.create(name=name)


def test_rename_trims_and_updates_name() -> None:
    dept = Department.create(name="Backend")

    dept.rename("  Platform  ")

    assert dept.name == "Platform"


@pytest.mark.parametrize(
    "name",
    ["", "   ", "\n\t "],
)
def test_rename_rejects_empty_name(name: str) -> None:
    dept = Department.create(name="Backend")

    with pytest.raises(DepartmentNameEmptyError):
        dept.rename(name)


def test_rename_rejects_too_long_name() -> None:
    dept = Department.create(name="Backend")
    name = "a" * 201

    with pytest.raises(DepartmentNameTooLongError):
        dept.rename(name)


def test_move_to_changes_parent_id() -> None:
    dept = Department.create(name="Backend", oid=1, parent_id=10)

    dept.move_to(20)

    assert dept.parent_id == 20


def test_move_to_allows_root_parent() -> None:
    dept = Department.create(name="Backend", oid=1, parent_id=10)

    dept.move_to(None)

    assert dept.parent_id is None


def test_move_to_raises_on_self_parent() -> None:
    dept = Department.create(name="Backend", oid=1, parent_id=10)

    with pytest.raises(DepartmentSelfParentError):
        dept.move_to(1)


def test_move_to_does_not_raise_when_oid_is_none() -> None:
    dept = Department.create(name="Backend", oid=None, parent_id=10)

    dept.move_to(10)

    assert dept.parent_id == 10
