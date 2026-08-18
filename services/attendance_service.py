from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.database import SessionLocal
from models.attendance import Attendance
from models.employee import Employee


def calculate_work_hours(
    attendance_date: date,
    check_in: time,
    check_out: time,
) -> tuple[Decimal, Decimal]:
    """
    Calculate total hours worked and overtime hours.

    Overtime is currently defined as any time worked
    beyond 8 hours in one day.
    """

    start_datetime = datetime.combine(
        attendance_date,
        check_in,
    )

    end_datetime = datetime.combine(
        attendance_date,
        check_out,
    )

    if end_datetime <= start_datetime:
        raise ValueError(
            "Check-out time must be later than check-in time."
        )

    worked_duration = (
        end_datetime - start_datetime
    )

    hours_worked = Decimal(
        str(
            worked_duration.total_seconds()
            / 3600
        )
    ).quantize(
        Decimal("0.01")
    )

    regular_day_hours = Decimal("8.00")

    overtime_hours = max(
        hours_worked - regular_day_hours,
        Decimal("0.00"),
    )

    return hours_worked, overtime_hours


def add_attendance(
    employee_code: str,
    attendance_date: date,
    status: str,
    check_in: time | None,
    check_out: time | None,
    notes: str,
) -> tuple[bool, str]:
    """Save one employee attendance record."""

    session = SessionLocal()

    try:
        # Find the employee using their employee code
        statement = select(Employee).where(
            Employee.employee_code
            == employee_code.strip().upper()
        )

        employee = session.scalar(statement)

        if employee is None:
            return False, "Employee could not be found."

        # Present and remote employees need working times
        if status in ["Present", "Remote"]:
            if check_in is None or check_out is None:
                return False, (
                    "Check-in and check-out times are required."
                )

            hours_worked, overtime_hours = (
                calculate_work_hours(
                    attendance_date=attendance_date,
                    check_in=check_in,
                    check_out=check_out,
                )
            )

        else:
            check_in = None
            check_out = None

            hours_worked = Decimal("0.00")
            overtime_hours = Decimal("0.00")

        attendance = Attendance(
            employee_id=employee.id,
            attendance_date=attendance_date,
            status=status,
            check_in=check_in,
            check_out=check_out,
            hours_worked=hours_worked,
            overtime_hours=overtime_hours,
            notes=notes.strip() or None,
        )

        session.add(attendance)

        session.commit()

        return (
            True,
            "Attendance recorded successfully."
        )

    except IntegrityError:
        session.rollback()

        return (
            False,
            "Attendance has already been recorded "
            "for this employee on this date."
        )

    except ValueError as error:
        session.rollback()

        return False, str(error)

    except Exception as error:
        session.rollback()

        return (
            False,
            f"Could not save attendance: {error}",
        )

    finally:
        session.close()

def get_attendance_records() -> tuple[list[dict], str | None]:
    """Return attendance records with employee information."""

    session = SessionLocal()

    try:
        statement = (
            select(Attendance, Employee)
            .join(
                Employee,
                Attendance.employee_id == Employee.id,
            )
            .order_by(
                Attendance.attendance_date.desc(),
                Employee.full_name,
            )
        )

        results = session.execute(statement).all()

        attendance_records = []

        for attendance, employee in results:
            attendance_records.append(
            {
                "Employee Code": employee.employee_code,
                "Employee Name": employee.full_name,
                "Date": attendance.attendance_date,
                "Status": attendance.status,
                "Check In": (
                    attendance.check_in.strftime(
                        "%I:%M %p"
                    )
                    if attendance.check_in
                    else ""
                ),
                "Check Out": (
                    attendance.check_out.strftime(
                        "%I:%M %p"
                    )
                    if attendance.check_out
                    else ""
                ),
                "Hours Worked": float(
                    attendance.hours_worked
                ),
                "Overtime Hours": float(
                    attendance.overtime_hours
                ),
                "Notes": attendance.notes or "",
            }
        )

        return attendance_records, None

    except Exception as error:
        return [], (
            f"Could not load attendance records: {error}"
        )
    finally:
        session.close()