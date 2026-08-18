from datetime import date
from decimal import Decimal

import pandas as pd
import streamlit as st

from services.employee_service import (
    add_employee,
    get_all_employees,
    get_employee_by_code,
    update_employee,
)


st.title("👥 Employee Records")

st.caption(
    "Register employees and manage their employment information."
)
if "employee_update_message" in st.session_state:
    st.success(
        st.session_state["employee_update_message"]
    )

    del st.session_state["employee_update_message"]
st.divider()


# ---------------------------------------------------------
# ADD A NEW EMPLOYEE
# ---------------------------------------------------------
st.subheader("Add New Employee")

st.write(
    "Enter the employee's information below. "
    "Fields marked with * are required."
)

with st.form("employee_registration_form"):
    employee_code = st.text_input(
        "Employee Code *",
        placeholder="Example: EMP-1001",
    )

    full_name = st.text_input(
        "Full Name *",
        placeholder="Example: Sarah Johnson",
    )

    email = st.text_input(
        "Email Address *",
        placeholder="Example: sarah@company.com",
    )

    phone = st.text_input(
        "Phone Number",
        placeholder="Example: 302-555-1234",
    )

    department = st.selectbox(
        "Department *",
        [
            "Human Resources",
            "Finance",
            "Information Technology",
            "Marketing",
            "Operations",
            "Sales",
        ],
    )

    job_title = st.text_input(
        "Job Title *",
        placeholder="Example: Data Analyst",
    )

    employment_type = st.selectbox(
        "Employment Type *",
        [
            "Full-time",
            "Part-time",
            "Contract",
        ],
    )

    hire_date = st.date_input(
        "Hire Date *",
        value=date.today(),
    )

    base_salary = st.number_input(
        "Annual Base Salary ($) *",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
    )

    submitted = st.form_submit_button(
        "Save Employee",
        type="primary",
    )


if submitted:
    if not employee_code.strip():
        st.error("Employee code is required.")

    elif not full_name.strip():
        st.error("Full name is required.")

    elif not email.strip():
        st.error("Email address is required.")

    elif "@" not in email or "." not in email:
        st.error("Please enter a valid email address.")

    elif not job_title.strip():
        st.error("Job title is required.")

    elif base_salary <= 0:
        st.error("Base salary must be greater than zero.")

    else:
        success, message = add_employee(
            employee_code=employee_code,
            full_name=full_name,
            email=email,
            phone=phone,
            department=department,
            job_title=job_title,
            employment_type=employment_type,
            hire_date=hire_date,
            base_salary=Decimal(str(base_salary)),
        )

        if success:
            st.success(message)
        else:
            st.error(message)


# ---------------------------------------------------------
# EMPLOYEE DIRECTORY
# ---------------------------------------------------------
st.divider()

st.subheader("📋 Employee Directory")

st.write(
    "Search, filter, and view employees stored in the payroll system."
)

employee_records, error = get_all_employees()


if error:
    st.error(error)

elif not employee_records:
    st.info(
        "No employees have been registered yet. "
        "Use the form above to create the first record."
    )

else:
    employee_dataframe = pd.DataFrame(employee_records)

    # Keep the original employee table unchanged
    filtered_dataframe = employee_dataframe.copy()

    # Build filter option lists from the employee records
    department_options = [
        "All Departments"
    ] + sorted(
        employee_dataframe["Department"]
        .dropna()
        .unique()
        .tolist()
    )

    status_options = [
        "All Statuses"
    ] + sorted(
        employee_dataframe["Status"]
        .dropna()
        .unique()
        .tolist()
    )

    # Display search and filter controls
    search_column, department_column, status_column = st.columns(3)

    with search_column:
        search_text = st.text_input(
            "Search Employees",
            placeholder="Name, code, email, or job title",
            key="employee_search",
        )

    with department_column:
        selected_department = st.selectbox(
            "Filter by Department",
            department_options,
            key="employee_department_filter",
        )

    with status_column:
        selected_status = st.selectbox(
            "Filter by Status",
            status_options,
            key="employee_status_filter",
        )

    # Search across several employee columns
    if search_text.strip():
        search_columns = [
            "Employee Code",
            "Full Name",
            "Email",
            "Job Title",
        ]

        search_mask = (
            employee_dataframe[search_columns]
            .astype(str)
            .apply(
                lambda column: column.str.contains(
                    search_text.strip(),
                    case=False,
                    na=False,
                )
            )
            .any(axis=1)
        )

        filtered_dataframe = filtered_dataframe[
            search_mask
        ]

    # Apply department filter
    if selected_department != "All Departments":
        filtered_dataframe = filtered_dataframe[
            filtered_dataframe["Department"]
            == selected_department
        ]

    # Apply status filter
    if selected_status != "All Statuses":
        filtered_dataframe = filtered_dataframe[
            filtered_dataframe["Status"]
            == selected_status
        ]

    # Calculate directory statistics
    total_employees = len(employee_dataframe)

    active_employees = int(
        (
            employee_dataframe["Status"] == "Active"
        ).sum()
    )

    matching_employees = len(filtered_dataframe)

    # Display employee statistics
    total_column, active_column, matching_column = st.columns(3)

    total_column.metric(
        "Total Employees",
        total_employees,
    )

    active_column.metric(
        "Active Employees",
        active_employees,
    )

    matching_column.metric(
        "Matching Employees",
        matching_employees,
    )

    # Display filtered employee records
    if filtered_dataframe.empty:
        st.warning(
            "No employees match your current search and filters."
        )

    else:
        st.dataframe(
            filtered_dataframe,
            width="stretch",
            hide_index=True,
            column_config={
                "Annual Salary": st.column_config.NumberColumn(
                    "Annual Salary",
                    format="dollar",
                ),
                "Hire Date": st.column_config.DateColumn(
                    "Hire Date",
                    format="MM/DD/YYYY",
                ),
            },
        )

    st.divider()

    st.subheader("✏️ Edit Employee")

    st.write(
        "Choose an employee and update their employment information."
    )

    employee_code_options = [
        record["Employee Code"]
        for record in employee_records
    ]

    selected_employee_code = st.selectbox(
        "Choose Employee",
        employee_code_options,
        key="edit_employee_selector",
    )

    employee_to_edit, employee_error = get_employee_by_code(
        selected_employee_code
    )

    if employee_error:
        st.error(employee_error)

    elif employee_to_edit:
        department_choices = [
            "Human Resources",
            "Finance",
            "Information Technology",
            "Marketing",
            "Operations",
            "Sales",
        ]

        employment_type_choices = [
            "Full-time",
            "Part-time",
            "Contract",
        ]

        status_choices = [
            "Active",
            "Inactive",
            "On Leave",
        ]

        with st.form("edit_employee_form"):
            st.text_input(
                "Employee Code",
                value=employee_to_edit["employee_code"],
                disabled=True,
            )

            edited_full_name = st.text_input(
                "Full Name *",
                value=employee_to_edit["full_name"],
            )

            edited_email = st.text_input(
                "Email Address *",
                value=employee_to_edit["email"],
            )

            edited_phone = st.text_input(
                "Phone Number",
                value=employee_to_edit["phone"],
            )

            edited_department = st.selectbox(
                "Department *",
                department_choices,
                index=(
                    department_choices.index(
                        employee_to_edit["department"]
                    )
                    if employee_to_edit["department"]
                    in department_choices
                    else 0
                ),
            )

            edited_job_title = st.text_input(
                "Job Title *",
                value=employee_to_edit["job_title"],
            )

            edited_employment_type = st.selectbox(
                "Employment Type *",
                employment_type_choices,
                index=(
                    employment_type_choices.index(
                        employee_to_edit["employment_type"]
                    )
                    if employee_to_edit["employment_type"]
                    in employment_type_choices
                    else 0
                ),
            )

            edited_hire_date = st.date_input(
                "Hire Date *",
                value=employee_to_edit["hire_date"],
            )

            edited_base_salary = st.number_input(
                "Annual Base Salary ($) *",
                min_value=0.0,
                value=employee_to_edit["base_salary"],
                step=1000.0,
                format="%.2f",
            )

            edited_status = st.selectbox(
                "Employee Status *",
                status_choices,
                index=(
                    status_choices.index(
                        employee_to_edit["status"]
                    )
                    if employee_to_edit["status"]
                    in status_choices
                    else 0
                ),
            )

            update_submitted = st.form_submit_button(
                "Update Employee",
                type="primary",
            )

        if update_submitted:
            selected_employee_code = selected_employee_code or ""
            edited_phone = edited_phone or ""
            edited_full_name = edited_full_name or ""
            edited_email = edited_email or ""
            edited_job_title = edited_job_title or ""
            if not edited_full_name.strip():
                st.error("Full name is required.")

            elif (
                not edited_email.strip()
                or "@" not in edited_email
                or "." not in edited_email
            ):
                st.error(
                    "Please enter a valid email address."
                )

            elif not edited_job_title.strip():
                st.error("Job title is required.")

            elif edited_base_salary <= 0:
                st.error(
                    "Base salary must be greater than zero."
                )

            else:
                success, message = update_employee(
                    employee_code=selected_employee_code,
                    full_name=edited_full_name,
                    email=edited_email,
                    phone=edited_phone,
                    department=edited_department,
                    job_title=edited_job_title,
                    employment_type=edited_employment_type,
                    hire_date=edited_hire_date,
                    base_salary=Decimal(
                        str(edited_base_salary)
                    ),
                    status=edited_status,
                )

                if success:
                    st.session_state[
                        "employee_update_message"
                    ] = message

                    st.rerun()

                else:
                    st.error(message)