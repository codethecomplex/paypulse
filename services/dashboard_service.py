from datetime import date

from sqlalchemy import func, select

from core.database import SessionLocal
from models.attendance import Attendance
from models.employee import Employee
from models.payroll import Payroll


def get_dashboard_stats() -> tuple[dict, str | None]:
    """Return summary statistics for the dashboard."""

    session = SessionLocal()

    try:
        total_employees = session.scalar(
            select(func.count(Employee.id))
        ) or 0

        active_employees = session.scalar(
            select(func.count(Employee.id)).where(
                Employee.status == "Active"
            )
        ) or 0

        working_today = session.scalar(
            select(func.count(Attendance.id)).where(
                Attendance.attendance_date == date.today(),
                Attendance.status.in_(["Present", "Remote"]),
            )
        ) or 0

        payrolls_processed = session.scalar(
            select(func.count(Payroll.id))
        ) or 0

        total_net_payroll = session.scalar(
            select(func.sum(Payroll.net_pay))
        ) or 0

        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "working_today": working_today,
            "payrolls_processed": payrolls_processed,
            "total_net_payroll": float(total_net_payroll),
        }, None

    except Exception as error:
        return {}, f"Could not load dashboard: {error}"

    finally:
        session.close()