import streamlit as st


st.set_page_config(
    page_title="PayrollPro",
    page_icon="💼",
    layout="wide",
)


pages = {
    "Overview": [
        st.Page(
            "views/dashboard.py",
            title="Dashboard",
            icon="📊",
            default=True,
        )
    ],
    "Payroll Operations": [
        st.Page(
            "views/employees.py",
            title="Employees",
            icon="👥",
        ),
        st.Page(
            "views/attendance.py",
            title="Attendance",
            icon="📅",
        ),
        st.Page(
            "views/payroll.py",
            title="Process Payroll",
            icon="💰",
        ),
        st.Page(
            "views/payslips.py",
            title="Payslips",
            icon="📄",
        ),
    ],
    "Administration": [
        st.Page(
            "views/settings.py",
            title="Settings",
            icon="⚙️",
        )
    ],
}


navigation = st.navigation(pages)
navigation.run()