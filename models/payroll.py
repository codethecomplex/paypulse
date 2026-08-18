from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class Payroll(Base):
    __tablename__ = "payroll"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "period_start",
            "period_end",
            name="uq_employee_payroll_period",
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

    period_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    period_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    annual_salary: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    monthly_base_pay: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    overtime_hours: Mapped[Decimal] = mapped_column(
        Numeric(7, 2),
        default=0,
        nullable=False,
    )

    overtime_pay: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    unpaid_absence_days: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    absence_deduction: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    bonus: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    gross_pay: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    retirement_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    retirement_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    insurance_deduction: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    other_deduction: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    total_deductions: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    net_pay: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Processed",
        nullable=False,
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )