from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.database import SessionLocal
from models.employee import Employee
from models.payroll import Payroll

from decimal import Decimal, ROUND_HALF_UP


MONEY_PLACES = Decimal("0.01")

MONTHS_PER_YEAR = Decimal("12")
WORK_HOURS_PER_YEAR = Decimal("2080")
WORK_DAYS_PER_YEAR = Decimal("260")
OVERTIME_MULTIPLIER = Decimal("1.5")
PERCENT = Decimal("100")


def money(value: Decimal) -> Decimal:
    """Round a Decimal value to two money places."""

    return value.quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP,
    )


def calculate_payroll(
    annual_salary: Decimal,
    overtime_hours: Decimal = Decimal("0.00"),
    unpaid_absence_days: Decimal = Decimal("0.00"),
    bonus: Decimal = Decimal("0.00"),
    tax_rate: Decimal = Decimal("0.00"),
    retirement_rate: Decimal = Decimal("0.00"),
    insurance_deduction: Decimal = Decimal("0.00"),
    other_deduction: Decimal = Decimal("0.00"),
) -> dict:
    """
    Calculate monthly employee payroll.

    Includes base pay, overtime, bonus, absence deductions,
    tax, retirement, insurance, other deductions, and net pay.
    """

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------
    if annual_salary < 0:
        raise ValueError(
            "Annual salary cannot be negative."
        )

    if overtime_hours < 0:
        raise ValueError(
            "Overtime hours cannot be negative."
        )

    if unpaid_absence_days < 0:
        raise ValueError(
            "Unpaid absence days cannot be negative."
        )

    if bonus < 0:
        raise ValueError(
            "Bonus cannot be negative."
        )

    if tax_rate < 0 or tax_rate > 100:
        raise ValueError(
            "Tax rate must be between 0 and 100."
        )

    if retirement_rate < 0 or retirement_rate > 100:
        raise ValueError(
            "Retirement rate must be between 0 and 100."
        )

    if insurance_deduction < 0:
        raise ValueError(
            "Insurance deduction cannot be negative."
        )

    if other_deduction < 0:
        raise ValueError(
            "Other deduction cannot be negative."
        )

    # -----------------------------------------------------
    # BASE PAY
    # -----------------------------------------------------
    monthly_base_pay = money(
        annual_salary / MONTHS_PER_YEAR
    )

    hourly_rate = money(
        annual_salary / WORK_HOURS_PER_YEAR
    )

    # -----------------------------------------------------
    # OVERTIME
    # -----------------------------------------------------
    overtime_rate = money(
        hourly_rate * OVERTIME_MULTIPLIER
    )

    overtime_pay = money(
        overtime_hours * overtime_rate
    )

    # -----------------------------------------------------
    # ABSENCE DEDUCTION
    # -----------------------------------------------------
    daily_rate = money(
        annual_salary / WORK_DAYS_PER_YEAR
    )

    absence_deduction = money(
        unpaid_absence_days * daily_rate
    )

    # -----------------------------------------------------
    # GROSS PAY
    # -----------------------------------------------------
    gross_pay = money(
        monthly_base_pay
        + overtime_pay
        + bonus
        - absence_deduction
    )

    gross_pay = max(
        gross_pay,
        Decimal("0.00"),
    )

    # -----------------------------------------------------
    # TAX AND OTHER DEDUCTIONS
    # -----------------------------------------------------
    tax_amount = money(
        gross_pay
        * tax_rate
        / PERCENT
    )

    retirement_amount = money(
        gross_pay
        * retirement_rate
        / PERCENT
    )

    insurance_deduction = money(
        insurance_deduction
    )

    other_deduction = money(
        other_deduction
    )

    total_deductions = money(
        tax_amount
        + retirement_amount
        + insurance_deduction
        + other_deduction
    )

    # -----------------------------------------------------
    # NET PAY
    # -----------------------------------------------------
    net_pay = money(
        gross_pay - total_deductions
    )

    net_pay = max(
        net_pay,
        Decimal("0.00"),
    )

    # -----------------------------------------------------
    # RETURN PAYROLL RESULTS
    # -----------------------------------------------------
    return {
        "monthly_base_pay": monthly_base_pay,
        "hourly_rate": hourly_rate,
        "overtime_rate": overtime_rate,
        "overtime_hours": overtime_hours,
        "overtime_pay": overtime_pay,
        "daily_rate": daily_rate,
        "unpaid_absence_days": unpaid_absence_days,
        "absence_deduction": absence_deduction,
        "bonus": money(bonus),
        "gross_pay": gross_pay,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "retirement_rate": retirement_rate,
        "retirement_amount": retirement_amount,
        "insurance_deduction": insurance_deduction,
        "other_deduction": other_deduction,
        "total_deductions": total_deductions,
        "net_pay": net_pay,
    }
    # -----------------------------------------------------
    # SAVE PAYROLL RESULTS
    # -----------------------------------------------------

def save_processed_payroll(
    employee_code: str,
    period_start: date,
    period_end: date,
    annual_salary: Decimal,
    payroll_result: dict,
) -> tuple[bool, str]:
    """Save one completed payroll record."""

    if period_end < period_start:
        return False, (
            "Payroll period end date cannot be "
            "before the start date."
        )

    session = SessionLocal()

    try:
        statement = select(Employee).where(
            Employee.employee_code
            == employee_code.strip().upper()
        )

        employee = session.scalar(statement)

        if employee is None:
            return False, "Employee could not be found."

        payroll = Payroll(
            employee_id=employee.id,
            period_start=period_start,
            period_end=period_end,
            annual_salary=money(annual_salary),
            monthly_base_pay=payroll_result[
                "monthly_base_pay"
            ],
            overtime_hours=payroll_result[
                "overtime_hours"
            ],
            overtime_pay=payroll_result[
                "overtime_pay"
            ],
            unpaid_absence_days=payroll_result[
                "unpaid_absence_days"
            ],
            absence_deduction=payroll_result[
                "absence_deduction"
            ],
            bonus=payroll_result["bonus"],
            gross_pay=payroll_result["gross_pay"],
            tax_rate=payroll_result["tax_rate"],
            tax_amount=payroll_result["tax_amount"],
            retirement_rate=payroll_result[
                "retirement_rate"
            ],
            retirement_amount=payroll_result[
                "retirement_amount"
            ],
            insurance_deduction=payroll_result[
                "insurance_deduction"
            ],
            other_deduction=payroll_result[
                "other_deduction"
            ],
            total_deductions=payroll_result[
                "total_deductions"
            ],
            net_pay=payroll_result["net_pay"],
            status="Processed",
        )

        session.add(payroll)
        session.commit()

        return True, "Payroll processed successfully."

    except IntegrityError:
        session.rollback()

        return False, (
            "Payroll has already been processed "
            "for this employee and period."
        )

    except KeyError as error:
        session.rollback()

        return False, (
            f"Payroll calculation is missing: {error}"
        )

    except Exception as error:
        session.rollback()

        return False, (
            f"Could not process payroll: {error}"
        )

    finally:
        session.close()

###############################################
# Date payroll record out of database
###############################################

def get_payroll_records() -> tuple[list[dict], str | None]:
    """Return processed payroll records with employee information."""

    session = SessionLocal()

    try:
        statement = (
            select(Payroll, Employee)
            .join(
                Employee,
                Payroll.employee_id == Employee.id,
            )
            .order_by(
                Payroll.processed_at.desc()
            )
        )

        results = session.execute(statement).all()

        payroll_records = []

        for payroll, employee in results:
            payroll_records.append(
                {
                    "Employee Code": employee.employee_code,
                    "Employee Name": employee.full_name,
                    "Payroll ID": payroll.id,
                    "Period Start": payroll.period_start,
                    "Period End": payroll.period_end,
                    "Gross Pay": float(payroll.gross_pay),
                    "Total Deductions": float(
                        payroll.total_deductions
                    ),
                    "Net Pay": float(payroll.net_pay),
                    "Status": payroll.status,
                    "Processed At": payroll.processed_at,
                }
            )

        return payroll_records, None

    except Exception as error:
        return [], (
            f"Could not load payroll records: {error}"
        )

    finally:
        session.close()