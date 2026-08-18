from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.database import SessionLocal
from models.employee import Employee


def add_employee(
    employee_code: str,
    full_name: str,
    email: str,
    phone: str,
    department: str,
    job_title: str,
    employment_type: str,
    hire_date: date,
    base_salary: Decimal,
) -> tuple[bool, str]:
    """Save a new employee in the database."""

    session = SessionLocal()

    try:
        employee = Employee(
            employee_code=employee_code.strip().upper(),
            full_name=full_name.strip(),
            email=email.strip().lower(),
            phone=phone.strip() or None,
            department=department,
            job_title=job_title.strip(),
            employment_type=employment_type,
            hire_date=hire_date,
            base_salary=base_salary,
            status="Active",
        )

        session.add(employee)
        session.commit()

        return True, "Employee added successfully."

    except IntegrityError:
        session.rollback()

        return False, (
            "Employee code or email already exists."
        )

    except Exception as error:
        session.rollback()

        return False, f"Could not add employee: {error}"

    finally:
        session.close()


    #open the database, collect all saved employees, and bring them back to the Streamlit page.
def get_all_employees() -> tuple[list[dict], str | None]:
    """Return all employees stored in the database."""

    session = SessionLocal()

    try:
        statement = select(Employee).order_by(Employee.full_name)

        employees = session.scalars(statement).all()

        employee_records = []

        for employee in employees:
            employee_records.append(
                {
                    "Employee Code": employee.employee_code,
                    "Full Name": employee.full_name,
                    "Email": employee.email,
                    "Department": employee.department,
                    "Job Title": employee.job_title,
                    "Employment Type": employee.employment_type,
                    "Hire Date": employee.hire_date,
                    "Annual Salary": float(employee.base_salary),
                    "Status": employee.status,
                }
            )

        return employee_records, None

    except Exception as error:
        return [], f"Could not load employees: {error}"

    finally:
        session.close()