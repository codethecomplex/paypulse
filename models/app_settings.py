from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        default=1,
    )

    company_name: Mapped[str] = mapped_column(
        String(100),
        default="PayrollPro",
        nullable=False,
    )

    default_tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=15,
        nullable=False,
    )

    default_retirement_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=5,
        nullable=False,
    )

    default_insurance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=100,
        nullable=False,
    )