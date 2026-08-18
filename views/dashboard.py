import streamlit as st


st.title("💼 PayrollPro")

st.caption(
    "Employee records, attendance, payroll processing, "
    "deductions, and payslip management"
)

st.divider()

employee_column, attendance_column, payroll_column, cost_column = st.columns(4)

employee_column.metric(
    label="Total Employees",
    value=0,
)

attendance_column.metric(
    label="Present Today",
    value=0,
)

payroll_column.metric(
    label="Payroll Status",
    value="Not Processed",
)

cost_column.metric(
    label="Monthly Payroll",
    value="$0.00",
)

st.subheader("System Overview")

st.info(
    "The project foundation is ready. "
    "Employee management will be added in the next milestone."
)