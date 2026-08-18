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
def get_employee_by_code(
    employee_code: str,
) -> tuple[dict | None, str | None]:
    """Return one employee using their employee code."""

    session = SessionLocal()

    try:
        statement = select(Employee).where(
            Employee.employee_code
            == employee_code.strip().upper()
        )

        employee = session.scalar(statement)

        if employee is None:
            return None, "Employee could not be found."

        employee_record = {
            "employee_code": employee.employee_code,
            "full_name": employee.full_name,
            "email": employee.email,
            "phone": employee.phone or "",
            "department": employee.department,
            "job_title": employee.job_title,
            "employment_type": employee.employment_type,
            "hire_date": employee.hire_date,
            "base_salary": float(employee.base_salary),
            "status": employee.status,
        }

        return employee_record, None

    except Exception as error:
        return None, f"Could not load employee: {error}"

    finally:
        session.close()


def update_employee(
    employee_code: str,
    full_name: str,
    email: str,
    phone: str,
    department: str,
    job_title: str,
    employment_type: str,
    hire_date: date,
    base_salary: Decimal,
    status: str,
) -> tuple[bool, str]:
    """Update an existing employee's information."""

    session = SessionLocal()

    try:
        statement = select(Employee).where(
            Employee.employee_code
            == employee_code.strip().upper()
        )

        employee = session.scalar(statement)

        if employee is None:
            return False, "Employee could not be found."

        employee.full_name = full_name.strip()
        employee.email = email.strip().lower()
        employee.phone = phone.strip() or None
        employee.department = department
        employee.job_title = job_title.strip()
        employee.employment_type = employment_type
        employee.hire_date = hire_date
        employee.base_salary = base_salary
        employee.status = status

        session.commit()

        return True, "Employee updated successfully."

    except IntegrityError:
        session.rollback()

        return False, (
            "That email address already belongs to another employee."
        )

    except Exception as error:
        session.rollback()

        return False, f"Could not update employee: {error}"

    finally:
        session.close()