from decimal import Decimal
from datetime import date
import pandas as pd
import streamlit as st


from services.employee_service import get_all_employees
from services.payroll_service import calculate_payroll
from services.payroll_service import get_payroll_records
from services.payroll_service import save_processed_payroll
from services.settings_service import get_settings


st.title("💰 Payroll Processing")

st.caption(
    "Calculate employee salary, overtime, bonuses, "
    "deductions, and net pay."
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
        "Add an employee before processing payroll."
    )

else:
    st.subheader("Payroll Calculator")

    employee_options = {
        (
            f'{record["Employee Code"]} - '
            f'{record["Full Name"]}'
        ): record
        for record in employee_records
    }

    selected_employee_label = st.selectbox(
        "Employee *",
        list(employee_options.keys()),
    )

    selected_employee = employee_options[
        selected_employee_label
    ]

    annual_salary = Decimal(
        str(selected_employee["Annual Salary"])
    )

    salary_column, department_column = st.columns(2)

    salary_column.metric(
        "Annual Salary",
        f"${annual_salary:,.2f}",
    )

    department_column.metric(
        "Department",
        selected_employee["Department"],
    )

    st.divider()
    settings, settings_error = get_settings()

    if settings_error:
        st.error(settings_error)
        st.stop()

    st.subheader("Payroll Inputs")


    # -----------------------------------------------------
    # WORK AND BONUS INPUTS
    # -----------------------------------------------------
    overtime_column, absence_column, bonus_column = (
        st.columns(3)
    )

    with overtime_column:
        overtime_hours = st.number_input(
            "Overtime Hours",
            min_value=0.0,
            value=0.0,
            step=0.5,
        )

    with absence_column:
        unpaid_absence_days = st.number_input(
            "Unpaid Absence Days",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

    with bonus_column:
        bonus = st.number_input(
            "Bonus ($)",
            min_value=0.0,
            value=0.0,
            step=100.0,
        )


    # -----------------------------------------------------
    # PERCENTAGE DEDUCTIONS
    # -----------------------------------------------------
    tax_column, retirement_column = st.columns(2)

    with tax_column:
        tax_rate = st.number_input(
            "Tax Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=settings["default_tax_rate"],
            step=1.0,
        )

    with retirement_column:
        retirement_rate = st.number_input(
            "Retirement Contribution (%)",
            min_value=0.0,
            max_value=100.0,
            value=settings["default_retirement_rate"],
            step=1.0,
        )


    # -----------------------------------------------------
    # FIXED DEDUCTIONS
    # -----------------------------------------------------
    insurance_column, other_column = st.columns(2)

    with insurance_column:
        insurance_deduction = st.number_input(
            "Insurance Deduction ($)",
            min_value=0.0,
            value=settings["default_insurance"],
            step=25.0,
        )

    with other_column:
        other_deduction = st.number_input(
            "Other Deduction ($)",
            min_value=0.0,
            value=0.0,
            step=25.0,
        )
    # -----------------------------------------------------
    # PAYROLL PERIOD
    # -----------------------------------------------------
    st.subheader("Payroll Period")

    period_column_1, period_column_2 = st.columns(2)

    with period_column_1:
        period_start = st.date_input(
            "Period Start *",
            value=date.today().replace(day=1),
            format="MM/DD/YYYY",
        )

    with period_column_2:
        period_end = st.date_input(
            "Period End *",
            value=date.today(),
            format="MM/DD/YYYY",
        )

    calculate_clicked = st.button(
        "Calculate Payroll",
        type="primary",
    )


    # -----------------------------------------------------
    # CALCULATE PAYROLL
    # -----------------------------------------------------
    if calculate_clicked:
        try:
            payroll_result = calculate_payroll(
                annual_salary=annual_salary,
                overtime_hours=Decimal(
                    str(overtime_hours)
                ),
                unpaid_absence_days=Decimal(
                    str(unpaid_absence_days)
                ),
                bonus=Decimal(
                    str(bonus)
                ),
                tax_rate=Decimal(
                    str(tax_rate)
                ),
                retirement_rate=Decimal(
                    str(retirement_rate)
                ),
                insurance_deduction=Decimal(
                    str(insurance_deduction)
                ),
                other_deduction=Decimal(
                    str(other_deduction)
                ),
            )



            st.session_state["payroll_preview"] = payroll_result

            st.session_state["payroll_employee_code"] = (
                selected_employee["Employee Code"]
            )

            st.session_state["payroll_employee_name"] = (
                selected_employee["Full Name"]
            )

            st.session_state["payroll_annual_salary"] = annual_salary

            st.session_state["payroll_period_start"] = period_start
            st.session_state["payroll_period_end"] = period_end

            st.divider()

            st.subheader("Payroll Preview")


            # -------------------------------------------------
            # EARNINGS
            # -------------------------------------------------
            base_column, overtime_pay_column, bonus_pay_column = (
                st.columns(3)
            )

            base_column.metric(
                "Monthly Base Pay",
                (
                    f"${payroll_result['monthly_base_pay']:,.2f}"
                ),
            )

            overtime_pay_column.metric(
                "Overtime Pay",
                f"${payroll_result['overtime_pay']:,.2f}",
            )

            bonus_pay_column.metric(
                "Bonus",
                f"${payroll_result['bonus']:,.2f}",
            )


            gross_column, absence_column = st.columns(2)

            gross_column.metric(
                "Gross Pay",
                f"${payroll_result['gross_pay']:,.2f}",
            )

            absence_column.metric(
                "Absence Deduction",
                (
                    f"-${payroll_result['absence_deduction']:,.2f}"
                ),
            )


            # -------------------------------------------------
            # DEDUCTIONS
            # -------------------------------------------------
            st.subheader("Deductions")

            tax_result_column, retirement_result_column = (
                st.columns(2)
            )

            tax_result_column.metric(
                "Tax",
                f"-${payroll_result['tax_amount']:,.2f}",
            )

            retirement_result_column.metric(
                "Retirement",
                (
                    f"-${payroll_result['retirement_amount']:,.2f}"
                ),
            )

            insurance_result_column, other_result_column = (
                st.columns(2)
            )

            insurance_result_column.metric(
                "Insurance",
                (
                    f"-${payroll_result['insurance_deduction']:,.2f}"
                ),
            )

            other_result_column.metric(
                "Other Deductions",
                (
                    f"-${payroll_result['other_deduction']:,.2f}"
                ),
            )


            # -------------------------------------------------
            # FINAL PAY
            # -------------------------------------------------
            st.divider()

            deduction_column, net_column = st.columns(2)

            deduction_column.metric(
                "Total Deductions",
                (
                    f"-${payroll_result['total_deductions']:,.2f}"
                ),
            )

            net_column.metric(
                "Net Pay",
                f"${payroll_result['net_pay']:,.2f}",
            )

            st.write(
                f"**Hourly Rate:** "
                f"${payroll_result['hourly_rate']:,.2f}"
            )

            st.write(
                f"**Overtime Rate:** "
                f"${payroll_result['overtime_rate']:,.2f}"
            )

        except ValueError as error:
            st.error(str(error))

    # -----------------------------------------------------
    # FINALIZE PAYROLL
    # -----------------------------------------------------
    if "payroll_preview" in st.session_state:
        st.divider()

        st.subheader("Finalize Payroll")

        st.info(
            "Review the payroll information before "
            "saving it permanently."
        )

        st.write(
            f"**Employee:** "
            f"{st.session_state['payroll_employee_name']}"
        )

        st.write(
            f"**Payroll Period:** "
            f"{st.session_state['payroll_period_start']:%m/%d/%Y}"
            f" to "
            f"{st.session_state['payroll_period_end']:%m/%d/%Y}"
        )

        process_clicked = st.button(
            "Process Payroll",
            type="primary",
        )

        if process_clicked:
            success, message = save_processed_payroll(
                employee_code=(
                    st.session_state[
                        "payroll_employee_code"
                    ]
                ),
                period_start=(
                    st.session_state[
                        "payroll_period_start"
                    ]
                ),
                period_end=(
                    st.session_state[
                        "payroll_period_end"
                    ]
                ),
                annual_salary=(
                    st.session_state[
                        "payroll_annual_salary"
                    ]
                ),
                payroll_result=(
                    st.session_state[
                        "payroll_preview"
                    ]
                ),
            )

            if success:
                st.success(message)

                del st.session_state[
                    "payroll_preview"
                ]

            else:
                st.error(message)

    ##################################################
    # PAYROLL HISTORY
    ##################################################
    st.divider()

    st.subheader("📋 Payroll History")

    payroll_records, payroll_error = get_payroll_records()

    if payroll_error:
        st.error(payroll_error)

    elif not payroll_records:
        st.info(
            "No payroll records have been processed yet."
        )

    else:
        payroll_df = pd.DataFrame(payroll_records)
        # -------------------------------------------------
        # PAYROLL HISTORY FILTERS
        # -------------------------------------------------
        filter_employee_column, filter_status_column = (
            st.columns(2)
        )

        employee_names = [
            "All Employees"
        ] + sorted(
            payroll_df["Employee Name"]
            .unique()
            .tolist()
        )

        statuses = [
            "All Statuses"
        ] + sorted(
            payroll_df["Status"]
            .unique()
            .tolist()
        )

        with filter_employee_column:
            selected_history_employee = st.selectbox(
                "Filter by Employee",
                employee_names,
            )

        with filter_status_column:
            selected_history_status = st.selectbox(
                "Filter by Status",
                statuses,
            )

        filtered_payroll_df = payroll_df.copy()

        if selected_history_employee != "All Employees":
            filtered_payroll_df = filtered_payroll_df[
                filtered_payroll_df["Employee Name"]
                == selected_history_employee
            ]

        if selected_history_status != "All Statuses":
            filtered_payroll_df = filtered_payroll_df[
                filtered_payroll_df["Status"]
                == selected_history_status
            ]


        total_gross_pay = filtered_payroll_df[
            "Gross Pay"
        ].sum()

        total_net_pay = filtered_payroll_df[
            "Net Pay"
        ].sum()

        record_column, gross_column, net_column = (
            st.columns(3)
        )

        record_column.metric(
            "Processed Payrolls",
            len(filtered_payroll_df),
        )

        gross_column.metric(
            "Total Gross Pay",
            f"${total_gross_pay:,.2f}",
        )

        net_column.metric(
            "Total Net Pay",
            f"${total_net_pay:,.2f}",
        )

        display_payroll_df = (
            filtered_payroll_df.copy()
        )
        # -------------------------------------------------
        # FORMAT DATES FOR DISPLAY
        # -------------------------------------------------
        display_payroll_df["Period Start"] = (
            pd.to_datetime(
                display_payroll_df["Period Start"]
            ).dt.strftime("%m/%d/%Y")
        )

        display_payroll_df["Period End"] = (
            pd.to_datetime(
                display_payroll_df["Period End"]
            ).dt.strftime("%m/%d/%Y")
        )

        display_payroll_df["Processed At"] = (
            pd.to_datetime(
                display_payroll_df["Processed At"]
            ).dt.strftime(
                "%m/%d/%Y %I:%M %p"
            )
        )
        # -------------------------------------------------
        # FORMAT MONEY FOR DISPLAY
        # -------------------------------------------------
        money_columns = [
            "Gross Pay",
            "Total Deductions",
            "Net Pay",
        ]

        for column in money_columns:
            display_payroll_df[column] = (
                display_payroll_df[column]
                .apply(
                    lambda value: f"${value:,.2f}"
                )
            )
        display_columns = [
            "Employee Code",
            "Employee Name",
            "Period Start",
            "Period End",
            "Gross Pay",
            "Total Deductions",
            "Net Pay",
            "Status",
            "Processed At",
        ]
        st.dataframe(
        display_payroll_df[display_columns],
        width="stretch",
        hide_index=True,
        )