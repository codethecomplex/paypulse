import pandas as pd
from datetime import date, time

import streamlit as st

from services.attendance_service import (
    add_attendance,
    get_attendance_records,
)
from services.employee_service import get_all_employees


st.title("📅 Attendance Management")

st.caption(
    "Record daily employee attendance, working hours, "
    "and overtime."
)

st.divider()


# ---------------------------------------------------------
# LOAD EMPLOYEES
# ---------------------------------------------------------
employee_records, employee_error = get_all_employees()


if employee_error:
    st.error(employee_error)

elif not employee_records:
    st.info(
        "No employees are available. "
        "Add an employee before recording attendance."
    )

else:
    st.subheader("Record Attendance")

    # Show employee name and code together
    employee_options = {
        (
            f'{record["Employee Code"]} - '
            f'{record["Full Name"]}'
        ): record["Employee Code"]
        for record in employee_records
    }

    selected_employee_label = st.selectbox(
        "Employee *",
        list(employee_options.keys()),
    )

    selected_employee_code = employee_options[
        selected_employee_label
    ]

    attendance_date = st.date_input(
        "Attendance Date *",
        value=date.today(),
    )

    attendance_status = st.selectbox(
        "Attendance Status *",
        [
            "Present",
            "Remote",
            "Absent",
            "On Leave",
        ],
    )

    # Default values
    check_in = None
    check_out = None

    # Only working employees need check-in/out times
    if attendance_status in ["Present", "Remote"]:
        time_column_1, time_column_2 = st.columns(2)

        with time_column_1:
            check_in = st.time_input(
                "Check In *",
                value=time(9, 0),
            )

        with time_column_2:
            check_out = st.time_input(
                "Check Out *",
                value=time(17, 0),
            )

    notes = st.text_area(
        "Notes",
        placeholder=(
            "Optional note about attendance, leave, "
            "late arrival, etc."
        ),
    )

    submitted = st.button(
        "Save Attendance",
        type="primary",
    )

    if submitted:
        success, message = add_attendance(
            employee_code=selected_employee_code,
            attendance_date=attendance_date,
            status=attendance_status,
            check_in=check_in,
            check_out=check_out,
            notes=notes or "",
        )

        if success:
            st.success(message)

        else:
            st.error(message)


#-------------------------------------------------------------
#               Read Attendance Record/History
#-------------------------------------------------------------

st.divider()

st.subheader("📋 Attendance History")

st.write(
    "Review employee attendance, working hours, "
    "and overtime records."
)

attendance_records, attendance_error = (
    get_attendance_records()
)

if attendance_error:
    st.error(attendance_error)

elif not attendance_records:
    st.info(
        "No attendance records have been saved yet."
    )

else:
    attendance_dataframe = pd.DataFrame(
        attendance_records
    )

    filtered_attendance = (
        attendance_dataframe.copy()
    )

    employee_options = [
        "All Employees"
    ] + sorted(
        attendance_dataframe["Employee Name"]
        .dropna()
        .unique()
        .tolist()
    )

    status_options = [
        "All Statuses"
    ] + sorted(
        attendance_dataframe["Status"]
        .dropna()
        .unique()
        .tolist()
    )

    employee_filter_column, status_filter_column = (
        st.columns(2)
    )

    with employee_filter_column:
        selected_employee = st.selectbox(
            "Filter by Employee",
            employee_options,
            key="attendance_employee_filter",
        )

    with status_filter_column:
        selected_status = st.selectbox(
            "Filter by Status",
            status_options,
            key="attendance_status_filter",
        )

    if selected_employee != "All Employees":
        filtered_attendance = filtered_attendance[
            filtered_attendance["Employee Name"]
            == selected_employee
        ]

    if selected_status != "All Statuses":
        filtered_attendance = filtered_attendance[
            filtered_attendance["Status"]
            == selected_status
        ]

    matching_records = len(filtered_attendance)

    total_hours = filtered_attendance[
        "Hours Worked"
    ].sum()

    overtime_hours = filtered_attendance[
        "Overtime Hours"
    ].sum()

    record_column, hours_column, overtime_column = (
        st.columns(3)
    )

    record_column.metric(
        "Matching Records",
        matching_records,
    )

    hours_column.metric(
        "Total Hours",
        f"{total_hours:.2f}",
    )

    overtime_column.metric(
        "Overtime Hours",
        f"{overtime_hours:.2f}",
    )

    if filtered_attendance.empty:
        st.warning(
            "No attendance records match these filters."
        )

    else:
        st.dataframe(
            filtered_attendance,
            width="stretch",
            hide_index=True,
            column_config={
                "Date": st.column_config.DateColumn(
                    "Date",
                    format="MM/DD/YYYY",
                ),
                "Hours Worked":
                    st.column_config.NumberColumn(
                        "Hours Worked",
                        format="%.2f",
                    ),
                "Overtime Hours":
                    st.column_config.NumberColumn(
                        "Overtime Hours",
                        format="%.2f",
                    ),
            },
        )