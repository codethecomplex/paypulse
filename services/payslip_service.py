from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import select

from core.database import SessionLocal
from models.employee import Employee
from models.payroll import Payroll


def generate_payslip_pdf(
    payroll_id: int,
) -> tuple[bytes | None, str | None]:
    """Generate a PDF payslip for one processed payroll."""

    session = SessionLocal()

    try:
        # -------------------------------------------------
        # FIND PAYROLL AND EMPLOYEE
        # -------------------------------------------------
        statement = (
            select(Payroll, Employee)
            .join(
                Employee,
                Payroll.employee_id == Employee.id,
            )
            .where(
                Payroll.id == payroll_id
            )
        )

        result = session.execute(statement).first()

        if result is None:
            return None, (
                "Payroll record could not be found."
            )

        payroll, employee = result

        # -------------------------------------------------
        # CREATE PDF IN MEMORY
        # -------------------------------------------------
        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=LETTER,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "PayslipTitle",
            parent=styles["Title"],
            fontSize=20,
            leading=24,
            alignment=1,
        )

        story = []

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------
        story.append(
            Paragraph(
                "PayrollPro",
                title_style,
            )
        )

        story.append(
            Paragraph(
                "Employee Payslip",
                styles["Heading2"],
            )
        )

        story.append(
            Spacer(1, 16)
        )

        # -------------------------------------------------
        # EMPLOYEE INFORMATION
        # -------------------------------------------------
        employee_data = [
            [
                "Employee",
                employee.full_name,
                "Employee Code",
                employee.employee_code,
            ],
            [
                "Department",
                employee.department,
                "Job Title",
                employee.job_title,
            ],
            [
                "Payroll Period",
                (
                    f"{payroll.period_start:%m/%d/%Y}"
                    f" - "
                    f"{payroll.period_end:%m/%d/%Y}"
                ),
                "Status",
                payroll.status,
            ],
        ]

        employee_table = Table(
            employee_data,
            colWidths=[
                90,
                150,
                90,
                150,
            ],
        )

        employee_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "BACKGROUND",
                        (2, 0),
                        (2, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (2, 0),
                        (2, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(employee_table)

        story.append(
            Spacer(1, 20)
        )

        # -------------------------------------------------
        # EARNINGS
        # -------------------------------------------------
        story.append(
            Paragraph(
                "Earnings",
                styles["Heading2"],
            )
        )

        earnings_data = [
            [
                "Description",
                "Amount",
            ],
            [
                "Monthly Base Pay",
                f"${payroll.monthly_base_pay:,.2f}",
            ],
            [
                "Overtime Pay",
                f"${payroll.overtime_pay:,.2f}",
            ],
            [
                "Bonus",
                f"${payroll.bonus:,.2f}",
            ],
            [
                "Gross Pay",
                f"${payroll.gross_pay:,.2f}",
            ],
        ]

        earnings_table = Table(
            earnings_data,
            colWidths=[
                330,
                150,
            ],
        )

        earnings_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (0, -1),
                        (-1, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (1, -1),
                        "RIGHT",
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(earnings_table)

        story.append(
            Spacer(1, 20)
        )

        # -------------------------------------------------
        # DEDUCTIONS
        # -------------------------------------------------
        story.append(
            Paragraph(
                "Deductions",
                styles["Heading2"],
            )
        )

        deductions_data = [
            [
                "Description",
                "Amount",
            ],
            [
                "Absence Deduction",
                f"${payroll.absence_deduction:,.2f}",
            ],
            [
                "Tax",
                f"${payroll.tax_amount:,.2f}",
            ],
            [
                "Retirement",
                f"${payroll.retirement_amount:,.2f}",
            ],
            [
                "Insurance",
                f"${payroll.insurance_deduction:,.2f}",
            ],
            [
                "Other Deductions",
                f"${payroll.other_deduction:,.2f}",
            ],
            [
                "Total Deductions",
                f"${payroll.total_deductions:,.2f}",
            ],
        ]

        deductions_table = Table(
            deductions_data,
            colWidths=[
                330,
                150,
            ],
        )

        deductions_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (0, -1),
                        (-1, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (1, -1),
                        "RIGHT",
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(deductions_table)

        story.append(
            Spacer(1, 24)
        )

        # -------------------------------------------------
        # NET PAY
        # -------------------------------------------------
        net_pay_data = [
            [
                "NET PAY",
                f"${payroll.net_pay:,.2f}",
            ]
        ]

        net_pay_table = Table(
            net_pay_data,
            colWidths=[
                330,
                150,
            ],
        )

        net_pay_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        13,
                    ),
                    (
                        "ALIGN",
                        (1, 0),
                        (1, 0),
                        "RIGHT",
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.grey,
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                ]
            )
        )

        story.append(net_pay_table)

        # -------------------------------------------------
        # BUILD PDF
        # -------------------------------------------------
        document.build(story)

        pdf_bytes = buffer.getvalue()

        buffer.close()

        return pdf_bytes, None

    except Exception as error:
        return None, (
            f"Could not generate payslip: {error}"
        )

    finally:
        session.close()