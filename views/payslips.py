import streamlit as st

from services.payroll_service import get_payroll_records
from services.payslip_service import generate_payslip_pdf


st.title("📄 Employee Payslips")

st.caption(
    "Generate and download payslips from "
    "processed payroll records."
)

st.divider()


# ---------------------------------------------------------
# LOAD PROCESSED PAYROLL
# ---------------------------------------------------------
payroll_records, payroll_error = get_payroll_records()


if payroll_error:
    st.error(payroll_error)

elif not payroll_records:
    st.info(
        "No processed payroll records are available."
    )

else:
    # -----------------------------------------------------
    # PAYROLL SELECTION
    # -----------------------------------------------------
    payroll_options = {
        (
            f'{record["Employee Code"]} - '
            f'{record["Employee Name"]} - '
            f'{record["Period Start"]:%m/%d/%Y} '
            f'to '
            f'{record["Period End"]:%m/%d/%Y}'
        ): record
        for record in payroll_records
    }

    selected_payroll_label = st.selectbox(
        "Select Payroll *",
        list(payroll_options.keys()),
    )

    selected_payroll = payroll_options[
        selected_payroll_label
    ]

    st.divider()

    # -----------------------------------------------------
    # PAYSLIP SUMMARY
    # -----------------------------------------------------
    st.subheader("Payslip Summary")

    employee_column, net_pay_column = st.columns(2)

    employee_column.metric(
        "Employee",
        selected_payroll["Employee Name"],
    )

    net_pay_column.metric(
        "Net Pay",
        f'${selected_payroll["Net Pay"]:,.2f}',
    )

    st.write(
        f"**Payroll Period:** "
        f'{selected_payroll["Period Start"]:%m/%d/%Y}'
        f" to "
        f'{selected_payroll["Period End"]:%m/%d/%Y}'
    )

    st.write(
        f"**Status:** {selected_payroll['Status']}"
    )

    # -----------------------------------------------------
    # GENERATE PDF
    # -----------------------------------------------------
    pdf_bytes, pdf_error = generate_payslip_pdf(
        selected_payroll["Payroll ID"]
    )

    if pdf_error:
        st.error(pdf_error)

    else:
        file_name = (
            f'{selected_payroll["Employee Code"]}_'
            f'{selected_payroll["Period Start"]:%Y_%m}_'
            f'payslip.pdf'
        )

        st.download_button(
            label="⬇️ Download Payslip PDF",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf",
            type="primary",
        )