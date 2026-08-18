from decimal import Decimal

import streamlit as st

from services.settings_service import (
    get_settings,
    save_settings,
)

st.title("⚙️ Payroll Settings")
st.info("Tax and deduction rules will be configured here.")


st.divider()

# ---------------------------------------------------------
# COMPANY INFORMATION
# ---------------------------------------------------------
st.subheader("🏢 Company Information")
settings, settings_error = get_settings()

if settings_error:
    st.error(settings_error)
    st.stop()

company_name = st.text_input(
    "Company Name",
    value=settings["company_name"],
)


# ---------------------------------------------------------
# PAYROLL DEFAULTS
# ---------------------------------------------------------
st.subheader("💰 Payroll Defaults")

tax_column, retirement_column, insurance_column = (
    st.columns(3)
)

with tax_column:
    default_tax_rate = st.number_input(
        "Default Tax Rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=settings["default_tax_rate"],
        step=1.0,
    )

with retirement_column:
    default_retirement_rate = st.number_input(
        "Default Retirement (%)",
        min_value=0.0,
        max_value=100.0,
        value=settings["default_retirement_rate"],
        step=1.0,
    )

with insurance_column:
    default_insurance = st.number_input(
        "Default Insurance ($)",
        min_value=0.0,
        value=settings["default_insurance"],
        step=25.0,
    )


st.divider()

save_clicked = st.button(
    "💾 Save Settings",
    type="primary",
)

if save_clicked:
    success, message = save_settings(
        company_name=company_name,
        default_tax_rate=Decimal(
            str(default_tax_rate)
        ),
        default_retirement_rate=Decimal(
            str(default_retirement_rate)
        ),
        default_insurance=Decimal(
            str(default_insurance)
        ),
    )

    if success:
        st.success(message)

    else:
        st.error(message)