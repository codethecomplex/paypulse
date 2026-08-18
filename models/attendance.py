from datetime import date, time
from decimal import Decimal

from sqlalchemy import (
    Date,
    ForeignKey,
    Numeric,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "attendance_date",
            name="uq_employee_attendance_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    attendance_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    check_in: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    check_out: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    hours_worked: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    overtime_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )