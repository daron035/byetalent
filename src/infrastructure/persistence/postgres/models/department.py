from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import TimedBaseModel


if TYPE_CHECKING:
    from src.infrastructure.persistence.postgres.models import Employee


class Department(TimedBaseModel):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)

    parent: Mapped[Department | None] = relationship("Department", remote_side=[id], back_populates="children")
    children: Mapped[list[Department]] = relationship(
        "Department", back_populates="parent", cascade="all, delete-orphan"
    )

    employees: Mapped[list[Employee]] = relationship(
        "Employee",
        back_populates="department",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            "parent_id",
            postgresql_nulls_not_distinct=True,
        ),
    )
