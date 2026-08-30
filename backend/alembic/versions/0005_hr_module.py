"""HR module — departments, employees, employment_contracts, attendance_records,
leave_requests, payroll_periods, payroll_entries, payroll_components.

Revision ID: 0005_hr_module
Revises: 0004_procurement_module
Create Date: 2024-01-01 00:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_hr_module"
down_revision = "0004_procurement_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    def e(values, name):
        return postgresql.ENUM(*values, name=name, create_type=True)

    gender_enum = e(["male", "female"], "gender")
    marital_enum = e(["single", "married", "divorced", "widowed"], "maritalstatus")
    emp_type_enum = e(["full_time", "part_time", "contract", "intern"], "employmenttype")
    emp_status_enum = e(["active", "on_leave", "suspended", "terminated"], "employeestatus")
    work_sched_enum = e(["standard", "shift", "flexible"], "workschedule")
    contract_type_enum = e(["permanent", "fixed_term", "project_based"], "contracttype")
    contract_status_enum = e(["active", "expired", "terminated", "renewed"], "contractstatus")
    att_status_enum = e(["present", "absent", "leave", "sick", "remote", "holiday", "half_day"], "attendancestatus")
    leave_type_enum = e(["annual", "sick", "unpaid", "marriage", "bereavement", "maternity", "paternity", "hajj", "other"], "leavetype")
    leave_status_enum = e(["pending", "approved", "rejected", "cancelled"], "leavestatus")
    payroll_period_status_enum = e(["draft", "processing", "approved", "paid", "closed"], "payrollperiodstatus")
    payroll_entry_status_enum = e(["draft", "approved", "paid"], "payrollentrystatus")
    comp_type_enum = e(["earning", "deduction"], "componenttype")
    comp_cat_enum = e(["fixed", "variable", "calculated"], "componentcategory")
    calc_method_enum = e(["flat_amount", "percentage_of_base", "percentage_of_gross", "formula"], "calculationmethod")
    device_type_enum = e(["fingerprint", "card", "face", "pin"], "devicetype")

    # ── departments ───────────────────────────────────────────────────────
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(30), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("manager_id", sa.Integer(), nullable=True),  # FK added after employees
        sa.Column("cost_center_code", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_departments_code", "departments", ["code"])

    # ── employees ─────────────────────────────────────────────────────────
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("first_name_fa", sa.String(100), nullable=True),
        sa.Column("last_name_fa", sa.String(100), nullable=True),
        sa.Column("national_id", sa.String(10), nullable=False, unique=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("gender", gender_enum, nullable=False, server_default="male"),
        sa.Column("marital_status", marital_enum, nullable=False, server_default="single"),
        sa.Column("employee_code", sa.String(20), nullable=False, unique=True),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("job_title", sa.String(200), nullable=True),
        sa.Column("employment_type", emp_type_enum, nullable=False, server_default="full_time"),
        sa.Column("join_date", sa.Date(), nullable=False),
        sa.Column("leave_date", sa.Date(), nullable=True),
        sa.Column("status", emp_status_enum, nullable=False, server_default="active"),
        sa.Column("base_salary", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("salary_bank_account", sa.String(30), nullable=True),
        sa.Column("bank_name", sa.String(100), nullable=True),
        sa.Column("bank_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("insurance_exempt", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("tax_exempt", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("children_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("default_cost_center", sa.String(50), nullable=True),
        sa.Column("work_schedule", work_sched_enum, nullable=False, server_default="standard"),
        sa.Column("annual_leave_balance", sa.Integer(), nullable=False, server_default="26"),
        sa.Column("sick_leave_balance", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("base_salary >= 0", name="chk_employee_salary"),
        sa.CheckConstraint("children_count >= 0", name="chk_employee_children"),
    )
    op.create_index("ix_employees_employee_code", "employees", ["employee_code"])
    op.create_index("ix_employees_national_id", "employees", ["national_id"])
    op.create_index("ix_employees_status", "employees", ["status"])
    op.create_index("ix_employees_department_id", "employees", ["department_id"])

    # Now add FK from departments.manager_id → employees
    op.create_foreign_key("fk_departments_manager_id", "departments", "employees", ["manager_id"], ["id"], ondelete="SET NULL")

    # ── employment_contracts ──────────────────────────────────────────────
    op.create_table(
        "employment_contracts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contract_type", contract_type_enum, nullable=False, server_default="permanent"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("base_salary", sa.Numeric(18, 4), nullable=False),
        sa.Column("benefits_description", sa.Text(), nullable=True),
        sa.Column("notice_period_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("termination_clause", sa.Text(), nullable=True),
        sa.Column("contract_file_url", sa.String(500), nullable=True),
        sa.Column("signed_date", sa.Date(), nullable=True),
        sa.Column("status", contract_status_enum, nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("base_salary > 0", name="chk_contract_salary"),
    )
    op.create_index("ix_employment_contracts_employee_id", "employment_contracts", ["employee_id"])

    # ── attendance_devices ────────────────────────────────────────────────
    op.create_table(
        "attendance_devices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("device_type", device_type_enum, nullable=False),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("port", sa.Integer(), nullable=False, server_default="4370"),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("last_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── attendance_records ────────────────────────────────────────────────
    op.create_table(
        "attendance_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("check_in", sa.Time(), nullable=True),
        sa.Column("check_out", sa.Time(), nullable=True),
        sa.Column("work_hours", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("overtime_hours", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("night_hours", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("status", att_status_enum, nullable=False, server_default="present"),
        sa.Column("approved_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("device_record_id", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("employee_id", "record_date", name="uq_attendance_employee_date"),
        sa.CheckConstraint("work_hours >= 0", name="chk_attendance_hours"),
    )
    op.create_index("ix_attendance_employee_date", "attendance_records", ["employee_id", "record_date"])

    # ── leave_requests ────────────────────────────────────────────────────
    op.create_table(
        "leave_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("leave_type", leave_type_enum, nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("days_requested", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("attachment_url", sa.String(500), nullable=True),
        sa.Column("status", leave_status_enum, nullable=False, server_default="pending"),
        sa.Column("approver_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("balance_after", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("end_date >= start_date", name="chk_leave_dates"),
        sa.CheckConstraint("days_requested > 0", name="chk_leave_days"),
    )
    op.create_index("ix_leave_requests_employee_id", "leave_requests", ["employee_id"])
    op.create_index("ix_leave_requests_status", "leave_requests", ["status"])

    # ── payroll_components ────────────────────────────────────────────────
    op.create_table(
        "payroll_components",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=False),
        sa.Column("type", comp_type_enum, nullable=False),
        sa.Column("category", comp_cat_enum, nullable=False),
        sa.Column("calculation_method", calc_method_enum, nullable=False),
        sa.Column("default_value", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("percentage", sa.Numeric(5, 4), nullable=False, server_default="0"),
        sa.Column("formula", sa.Text(), nullable=True),
        sa.Column("debit_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("credit_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_taxable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_insurable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── payroll_periods ───────────────────────────────────────────────────
    op.create_table(
        "payroll_periods",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", payroll_period_status_enum, nullable=False, server_default="draft"),
        sa.Column("total_employees", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_gross", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_net", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_tax", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_insurance_employee", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("total_insurance_employer", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("journal_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("payment_batch_id", sa.String(50), nullable=True),
        sa.Column("approved_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("year", "month", name="uq_payroll_period_year_month"),
        sa.CheckConstraint("month BETWEEN 1 AND 12", name="chk_payroll_month"),
    )
    op.create_index("ix_payroll_periods_status", "payroll_periods", ["status"])

    # ── payroll_entries ───────────────────────────────────────────────────
    def _num(name, default="0"):
        return sa.Column(name, sa.Numeric(18, 4), nullable=False, server_default=default)

    op.create_table(
        "payroll_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("payroll_periods.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False),
        _num("base_salary"), _num("overtime_pay"), _num("bonus"),
        _num("housing_allowance"), _num("food_allowance"), _num("childcare_allowance"),
        _num("other_earnings"), _num("total_earnings"),
        sa.Column("working_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overtime_hours", sa.Numeric(6, 2), nullable=False, server_default="0"),
        sa.Column("absent_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("leave_days", sa.Integer(), nullable=False, server_default="0"),
        _num("insurance_employee"), _num("insurance_employer"), _num("tax"),
        _num("advance_deduction"), _num("loan_deduction"), _num("other_deductions"),
        _num("total_deductions"), _num("net_salary"),
        sa.Column("cost_center", sa.String(50), nullable=True),
        sa.Column("department_code", sa.String(30), nullable=True),
        sa.Column("status", payroll_entry_status_enum, nullable=False, server_default="draft"),
        sa.Column("payment_reference", sa.String(100), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("individual_je_id", sa.Integer(), sa.ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("period_id", "employee_id", name="uq_payroll_entry_period_employee"),
        sa.CheckConstraint("total_earnings >= 0", name="chk_payroll_earnings"),
        sa.CheckConstraint("net_salary >= 0", name="chk_payroll_net"),
    )
    op.create_index("ix_payroll_entries_period_id", "payroll_entries", ["period_id"])
    op.create_index("ix_payroll_entries_employee_id", "payroll_entries", ["employee_id"])

    # ── Seed departments ──────────────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "departments",
            sa.column("code", sa.String), sa.column("name", sa.String),
            sa.column("name_fa", sa.String), sa.column("cost_center_code", sa.String),
            sa.column("is_active", sa.Boolean),
        ),
        [
            {"code": "MGMT", "name": "Management",         "name_fa": "مدیریت",            "cost_center_code": "MGMT", "is_active": True},
            {"code": "FIN",  "name": "Finance",            "name_fa": "مالی",              "cost_center_code": "FIN",  "is_active": True},
            {"code": "HR",   "name": "Human Resources",    "name_fa": "منابع انسانی",      "cost_center_code": "HR",   "is_active": True},
            {"code": "IT",   "name": "Information Technology","name_fa": "فناوری اطلاعات", "cost_center_code": "IT",   "is_active": True},
            {"code": "SALES","name": "Sales",              "name_fa": "فروش",              "cost_center_code": "SALES","is_active": True},
            {"code": "PURCH","name": "Procurement",        "name_fa": "خرید",              "cost_center_code": "PURCH","is_active": True},
            {"code": "WARE", "name": "Warehouse",          "name_fa": "انبار",             "cost_center_code": "WARE", "is_active": True},
        ]
    )

    # ── Seed payroll components ───────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "payroll_components",
            sa.column("code", sa.String), sa.column("name", sa.String),
            sa.column("name_fa", sa.String), sa.column("type", sa.String),
            sa.column("category", sa.String), sa.column("calculation_method", sa.String),
            sa.column("percentage", sa.Numeric), sa.column("is_taxable", sa.Boolean),
            sa.column("is_insurable", sa.Boolean), sa.column("display_order", sa.Integer),
            sa.column("is_active", sa.Boolean),
        ),
        [
            # Earnings
            {"code": "BASE",     "name": "Base Salary",          "name_fa": "حقوق پایه",          "type": "earning",   "category": "fixed",      "calculation_method": "flat_amount",         "percentage": "0",    "is_taxable": True,  "is_insurable": True,  "display_order": 1, "is_active": True},
            {"code": "HOUSING",  "name": "Housing Allowance",    "name_fa": "حق مسکن",            "type": "earning",   "category": "fixed",      "calculation_method": "flat_amount",         "percentage": "0",    "is_taxable": True,  "is_insurable": True,  "display_order": 2, "is_active": True},
            {"code": "FOOD",     "name": "Food Allowance",       "name_fa": "حق خوار و بار",      "type": "earning",   "category": "fixed",      "calculation_method": "flat_amount",         "percentage": "0",    "is_taxable": True,  "is_insurable": True,  "display_order": 3, "is_active": True},
            {"code": "CHILD",    "name": "Childcare Allowance",  "name_fa": "کمک هزینه اولاد",    "type": "earning",   "category": "calculated", "calculation_method": "formula",             "percentage": "0",    "is_taxable": False, "is_insurable": False, "display_order": 4, "is_active": True},
            {"code": "OT",       "name": "Overtime Pay",         "name_fa": "اضافه‌کاری",         "type": "earning",   "category": "variable",   "calculation_method": "percentage_of_base",  "percentage": "0.4",  "is_taxable": True,  "is_insurable": True,  "display_order": 5, "is_active": True},
            {"code": "BONUS",    "name": "Bonus",                "name_fa": "پاداش",              "type": "earning",   "category": "variable",   "calculation_method": "flat_amount",         "percentage": "0",    "is_taxable": True,  "is_insurable": False, "display_order": 6, "is_active": True},
            # Deductions
            {"code": "INS_EMP",  "name": "Employee Insurance",   "name_fa": "حق بیمه کارمند",     "type": "deduction", "category": "calculated", "calculation_method": "percentage_of_gross", "percentage": "0.07", "is_taxable": False, "is_insurable": False, "display_order": 10, "is_active": True},
            {"code": "TAX",      "name": "Income Tax",           "name_fa": "مالیات بر درآمد",    "type": "deduction", "category": "calculated", "calculation_method": "formula",             "percentage": "0",    "is_taxable": False, "is_insurable": False, "display_order": 11, "is_active": True},
            {"code": "ADVANCE",  "name": "Advance Deduction",    "name_fa": "کسور مساعده",        "type": "deduction", "category": "variable",   "calculation_method": "flat_amount",         "percentage": "0",    "is_taxable": False, "is_insurable": False, "display_order": 12, "is_active": True},
        ]
    )


def downgrade() -> None:
    op.drop_constraint("fk_departments_manager_id", "departments", type_="foreignkey")
    for tbl in ["payroll_entries", "payroll_periods", "payroll_components",
                "leave_requests", "attendance_records", "attendance_devices",
                "employment_contracts", "employees", "departments"]:
        op.drop_table(tbl)
    for e in ["gender", "maritalstatus", "employmenttype", "employeestatus",
              "workschedule", "contracttype", "contractstatus", "attendancestatus",
              "leavetype", "leavestatus", "payrollperiodstatus", "payrollentrystatus",
              "componenttype", "componentcategory", "calculationmethod", "devicetype"]:
        op.execute(f"DROP TYPE IF EXISTS {e}")
