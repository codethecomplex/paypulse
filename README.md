# 💼 PayPulse

**Smart Employee & Payroll Management**

PayPulse is a Streamlit-based payroll management system built with Python. It manages employees, attendance, payroll processing, deductions, payroll history, PDF payslips, authentication, and payroll settings through a clean web interface.

## ✨ Features

- Employee registration and management
- Employee search and filtering
- Attendance tracking
- Work-hour and overtime calculation
- Payroll processing
- Bonus and unpaid absence calculations
- Tax, retirement, insurance, and other deductions
- Gross pay and net pay calculation
- Payroll history with filters
- PDF payslip generation
- Secure admin login with bcrypt password hashing
- Configurable payroll defaults
- Live dashboard statistics
- Automated payroll tests

## 🛠 Tech Stack

- Python
- Streamlit
- SQLAlchemy
- SQLite
- Pandas
- ReportLab
- bcrypt
- pytest

## 📁 Project Structure

- `views/` — Streamlit pages
- `models/` — SQLAlchemy database models
- `services/` — business logic
- `core/` — database configuration
- `tests/` — automated tests

## 🔐 Security

Administrator passwords are verified using bcrypt password hashing.

Sensitive credentials are stored using Streamlit Secrets and are excluded from Git.

## 🧪 Testing

Run:

```bash
python -m pytest