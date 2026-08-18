from decimal import Decimal

from services.payroll_service import calculate_payroll


def test_basic_monthly_salary():
    result = calculate_payroll(
        annual_salary=Decimal("60000"),
    )

    assert result["monthly_base_pay"] == Decimal("5000.00")


def test_overtime_increases_pay():
    result = calculate_payroll(
        annual_salary=Decimal("60000"),
        overtime_hours=Decimal("5"),
    )

    assert result["overtime_pay"] > Decimal("0.00")


def test_deductions_reduce_net_pay():
    result = calculate_payroll(
        annual_salary=Decimal("60000"),
        tax_rate=Decimal("15"),
    )

    assert result["net_pay"] < result["gross_pay"]


def test_negative_salary_rejected():
    try:
        calculate_payroll(
            annual_salary=Decimal("-100"),
        )

        assert False

    except ValueError:
        assert True