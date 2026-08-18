import pandas as pd
import streamlit as st

from services.dashboard_service import get_dashboard_stats
from services.payroll_service import get_payroll_records


st.title("📊 Dashboard")

st.caption(
    "Live overview of employees, attendance, and payroll activity."
)

st.divider()


# ---------------------------------------------------------
# DASHBOARD METRICS
# ---------------------------------------------------------
stats, stats_error = get_dashboard_stats()

if stats_error:
    st.error(stats_error)

else:
    column1, column2, column3 = st.columns(3)

    column1.metric(
        "Total Employees",
        stats["total_employees"],
    )

    column2.metric(
        "Active Employees",
        stats["active_employees"],
    )

    column3.metric(
        "Working Today",
        stats["working_today"],
    )

    column4, column5 = st.columns(2)

    column4.metric(
        "Payrolls Processed",
        stats["payrolls_processed"],
    )

    column5.metric(
        "Total Net Payroll",
        f'${stats["total_net_payroll"]:,.2f}',
    )


# ---------------------------------------------------------
# RECENT PAYROLL ACTIVITY
# ---------------------------------------------------------
st.divider()

st.subheader("Recent Payroll Activity")

payroll_records, payroll_error = get_payroll_records()

if payroll_error:
    st.error(payroll_error)

elif not payroll_records:
    st.info("No payroll has been processed yet.")

else:
    payroll_df = pd.DataFrame(payroll_records)

    recent_payroll_df = payroll_df[
        [
            "Employee Name",
            "Period Start",
            "Period End",
            "Net Pay",
            "Status",
        ]
    ].copy()

    recent_payroll_df["Period Start"] = pd.to_datetime(
        recent_payroll_df["Period Start"]
    ).dt.strftime("%m/%d/%Y")

    recent_payroll_df["Period End"] = pd.to_datetime(
        recent_payroll_df["Period End"]
    ).dt.strftime("%m/%d/%Y")

    recent_payroll_df["Net Pay"] = (
        recent_payroll_df["Net Pay"]
        .apply(lambda value: f"${value:,.2f}")
    )

    st.dataframe(
        recent_payroll_df.head(5),
        width="stretch",
        hide_index=True,
    )