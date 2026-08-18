from decimal import Decimal

from core.database import SessionLocal
from models.app_settings import AppSettings


def get_settings() -> tuple[dict, str | None]:
    """Load payroll application settings."""

    session = SessionLocal()

    try:
        settings = session.get(
            AppSettings,
            1,
        )

        if settings is None:
            return {
                "company_name": "PayrollPro",
                "default_tax_rate": 15.0,
                "default_retirement_rate": 5.0,
                "default_insurance": 100.0,
            }, None

        return {
            "company_name": settings.company_name,
            "default_tax_rate": float(
                settings.default_tax_rate
            ),
            "default_retirement_rate": float(
                settings.default_retirement_rate
            ),
            "default_insurance": float(
                settings.default_insurance
            ),
        }, None

    except Exception as error:
        return {}, f"Could not load settings: {error}"

    finally:
        session.close()


def save_settings(
    company_name: str,
    default_tax_rate: Decimal,
    default_retirement_rate: Decimal,
    default_insurance: Decimal,
) -> tuple[bool, str]:
    """Save payroll application settings."""

    company_name = company_name.strip()

    if not company_name:
        return False, "Company name is required."

    if default_tax_rate < 0 or default_tax_rate > 100:
        return False, (
            "Tax rate must be between 0 and 100."
        )

    if (
        default_retirement_rate < 0
        or default_retirement_rate > 100
    ):
        return False, (
            "Retirement rate must be between 0 and 100."
        )

    if default_insurance < 0:
        return False, (
            "Insurance deduction cannot be negative."
        )

    session = SessionLocal()

    try:
        settings = session.get(
            AppSettings,
            1,
        )

        if settings is None:
            settings = AppSettings(
                id=1,
                company_name=company_name,
                default_tax_rate=default_tax_rate,
                default_retirement_rate=(
                    default_retirement_rate
                ),
                default_insurance=default_insurance,
            )

            session.add(settings)

        else:
            settings.company_name = company_name
            settings.default_tax_rate = (
                default_tax_rate
            )
            settings.default_retirement_rate = (
                default_retirement_rate
            )
            settings.default_insurance = (
                default_insurance
            )

        session.commit()

        return True, "Settings saved successfully."

    except Exception as error:
        session.rollback()

        return False, (
            f"Could not save settings: {error}"
        )

    finally:
        session.close()