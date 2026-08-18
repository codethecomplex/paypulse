import streamlit as st
from services.auth_service import verify_password
# ---------------------------------------------------------
# Beautify section
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    /* Main app background */
    .stApp {
        background: linear-gradient(
            135deg,
            #eef4ff 0%,
            #f5f0ff 50%,
            #eefbff 100%
        );
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #172554,
            #312e81
        );
    }

    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: white;
    }

    /* Sidebar Logout button */
    [data-testid="stSidebar"] .stButton > button {
        background: #4338ca;
        color: white !important;
        border: 1px solid #6366f1;
        border-radius: 10px;
        font-weight: 600;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: #4f46e5;
        color: white !important;
        border-color: #818cf8;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.88);
        border-radius: 14px;
        padding: 18px;
        border: 1px solid rgba(100, 116, 139, 0.15);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    /* Dataframe / form areas */
    [data-testid="stDataFrame"] {
        background: white;
        border-radius: 12px;
    }

    /* Headings */
    h1 {
        color: #172554;
    }

    h2, h3 {
        color: #312e81;
    }

    /* Main font */
    html, body, [class*="css"] {
    font-family: "Segoe UI", Arial, sans-serif;

    h1, h2, h3 {
    font-family: "Segoe UI", Arial, sans-serif;
    font-weight: 700;
    }

    p, label, div {
    font-family: "Segoe UI", Arial, sans-serif;
    }

    /* Streamlit top header */
    [data-testid="stHeader"] {
        background: linear-gradient(
            90deg,
            #172554 0%,
            #312e81 55%,
            #4338ca 100%
        );
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
    }

    /* Top toolbar text and icons */
    [data-testid="stToolbar"] {
        color: white;
    }

    [data-testid="stToolbar"] button {
        color: white !important;
        border-radius: 8px;
    }
    }
    .payroll-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        background: linear-gradient(
            90deg,
            #172554,
            #312e81,
            #4338ca
        );

        padding: 20px 28px;
        border-radius: 16px;
        margin-bottom: 25px;

        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
    }

    .payroll-title {
        font-size: 27px;
        font-weight: 800;
        color: white;
        letter-spacing: 1px;
    }

    .payroll-subtitle {
        font-size: 14px;
        color: #dbeafe;
        margin-top: 3px;
    }

    .payroll-welcome {
        color: white;
        font-size: 16px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:

    st.title("🔐 PayPulse Admin Login")

    st.caption(
        "Sign in to access the payroll management system."
    )

    st.divider()

    with st.form("login_form"):
        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password",
        )

        login_clicked = st.form_submit_button(
            "Login",
            type="primary",
        )

    if login_clicked:
        saved_username = st.secrets[
            "admin"
        ]["username"]

        saved_password_hash = st.secrets[
            "admin"
        ]["password_hash"]

        username_correct = (
            username.strip() == saved_username
        )

        password_correct = verify_password(
            password,
            saved_password_hash,
        )

        if username_correct and password_correct:
            st.session_state["authenticated"] = True

            st.success(
                "Login successful."
            )

            st.rerun()

        else:
            st.error(
                "Incorrect username or password."
            )

    st.stop()
# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
with st.sidebar:
    with st.expander("🔐 Admin Session"):
        st.write("Signed in as Admin")

        if st.button("Logout", width="stretch"):
            st.session_state["authenticated"] = False
            st.rerun()

# ---------------------------------------------------------
# PAYPULSE HEADER
# ---------------------------------------------------------
st.html(
    """
    <div class="payroll-header">
        <div>
            <div class="payroll-title">💼 PAYPULSE</div>
            <div class="payroll-subtitle">
                Smart Employee &amp; Payroll Management
            </div>
        </div>

        <div class="payroll-welcome">
            Welcome, Admin
        </div>
    </div>
    """
)

st.set_page_config(
    page_title="PayPulse",
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