"""Enhanced User, RBAC, Sessions, Audit — complete schema.

Revision ID: 0008_rbac_module
Revises: 0007_crm_module
Create Date: 2024-01-01 00:00:00

Note: This migration REPLACES the basic users table from 0001_initial_schema.
If upgrading an existing deployment, run a data migration first.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008_rbac_module"
down_revision = "0007_crm_module"
branch_labels = None
depends_on = None

# ── Permission catalogue (module: action: description) ───────────────────
PERMISSIONS = [
    # Inventory
    ("inventory:view",          "View Inventory",         "inventory", "view",   None,         "operational"),
    ("inventory:create",        "Create Items",           "inventory", "create", None,         "operational"),
    ("inventory:edit",          "Edit Items",             "inventory", "edit",   None,         "operational"),
    ("inventory:delete",        "Delete Items",           "inventory", "delete", None,         "operational"),
    ("inventory:adjust",        "Adjust Stock",           "inventory", "adjust", None,         "operational"),
    ("inventory:view:cost",     "View Item Costs",        "inventory", "view",   "cost",       "administrative"),

    # Finance
    ("finance:view:all",        "View All Finance",       "finance",   "view",   "all",        "administrative"),
    ("finance:create:journal",  "Create Journal Entry",   "finance",   "create", "journal",    "operational"),
    ("finance:edit:draft",      "Edit Draft Entries",     "finance",   "edit",   "draft",      "operational"),
    ("finance:approve:journal", "Post Journal Entry",     "finance",   "approve","journal",    "administrative"),
    ("finance:view:payroll",    "View Payroll",           "finance",   "view",   "payroll",    "administrative"),
    ("finance:view:reports",    "View Finance Reports",   "finance",   "view",   "reports",    "operational"),
    ("finance:view:reports:sales","View Sales Reports",   "finance",   "view",   "reports:sales","operational"),

    # Sales
    ("sales:view:own",          "View Own Sales",         "sales",     "view",   "own",        "operational"),
    ("sales:view:department",   "View Dept Sales",        "sales",     "view",   "department", "operational"),
    ("sales:view:all",          "View All Sales",         "sales",     "view",   "all",        "administrative"),
    ("sales:create",            "Create Invoices",        "sales",     "create", None,         "operational"),
    ("sales:edit:own",          "Edit Own Invoices",      "sales",     "edit",   "own",        "operational"),
    ("sales:issue",             "Issue Invoices",         "sales",     "issue",  None,         "administrative"),

    # Procurement
    ("procurement:view",        "View Procurement",       "procurement","view",  None,         "operational"),
    ("procurement:create",      "Create POs",             "procurement","create",None,         "operational"),
    ("procurement:approve",     "Approve PRs",            "procurement","approve",None,        "administrative"),

    # HR
    ("hr:view:all",             "View All HR",            "hr",        "view",   "all",        "administrative"),
    ("hr:view:attendance",      "View Attendance",        "hr",        "view",   "attendance", "operational"),
    ("hr:view:payroll",         "View Payroll Data",      "hr",        "view",   "payroll",    "administrative"),
    ("hr:edit:employee",        "Edit Employees",         "hr",        "edit",   "employee",   "administrative"),
    ("hr:approve:leave",        "Approve Leave Requests", "hr",        "approve","leave",      "operational"),

    # CRM
    ("crm:view:own",            "View Own CRM",           "crm",       "view",   "own",        "operational"),
    ("crm:view:department",     "View Dept CRM",          "crm",       "view",   "department", "operational"),
    ("crm:view:all",            "View All CRM",           "crm",       "view",   "all",        "administrative"),
    ("crm:send:sms",            "Send SMS",               "crm",       "send",   "sms",        "operational"),
    ("crm:manage:campaigns",    "Manage Campaigns",       "crm",       "manage", "campaigns",  "administrative"),

    # BI
    ("bi:dashboard:ceo",        "CEO Dashboard",          "bi",        "view",   "ceo",        "administrative"),
    ("bi:dashboard:cfo",        "CFO Dashboard",          "bi",        "view",   "cfo",        "administrative"),
    ("bi:dashboard:sales",      "Sales Dashboard",        "bi",        "view",   "sales",      "operational"),
    ("bi:dashboard:hr",         "HR Dashboard",           "bi",        "view",   "hr",         "operational"),
    ("bi:export",               "Export Reports",         "bi",        "export", None,         "operational"),

    # Admin
    ("admin:user:view",         "View Users",             "admin",     "view",   "user",       "administrative"),
    ("admin:user:manage",       "Manage Users",           "admin",     "manage", "user",       "system"),
    ("admin:role:manage",       "Manage Roles",           "admin",     "manage", "role",       "system"),
    ("admin:audit:view",        "View Audit Logs",        "admin",     "view",   "audit",      "administrative"),
    ("admin:settings:view",     "View Settings",          "admin",     "view",   "settings",   "administrative"),
    ("admin:settings:edit",     "Edit Settings",          "admin",     "edit",   "settings",   "system"),

    # Super
    ("*",                       "All Permissions",        "system",    "*",      None,         "system"),
]

# ── System roles + their permission codes ────────────────────────────────
SYSTEM_ROLES = [
    {
        "code": "super_admin", "name": "Super Administrator", "name_fa": "مدیر ارشد سیستم",
        "level": 0, "data_scope": "all", "role_type": "system",
        "permissions": ["*"],
        "default_dashboard": "admin",
    },
    {
        "code": "ceo", "name": "CEO", "name_fa": "مدیرعامل",
        "level": 1, "data_scope": "all", "role_type": "system",
        "permissions": ["bi:dashboard:ceo","finance:view:all","hr:view:all",
                        "sales:view:all","procurement:view","inventory:view",
                        "crm:view:all","admin:user:view","admin:settings:view"],
        "default_dashboard": "ceo",
    },
    {
        "code": "cfo", "name": "CFO", "name_fa": "مدیر مالی",
        "level": 2, "data_scope": "all", "role_type": "system",
        "permissions": ["bi:dashboard:cfo","finance:view:all","finance:create:journal",
                        "finance:edit:draft","finance:approve:journal",
                        "sales:view:all","procurement:view","hr:view:payroll",
                        "bi:export","admin:audit:view"],
        "default_dashboard": "cfo",
    },
    {
        "code": "sales_manager", "name": "Sales Manager", "name_fa": "مدیر فروش",
        "level": 3, "data_scope": "department", "role_type": "system",
        "permissions": ["bi:dashboard:sales","sales:view:all","sales:create","sales:issue",
                        "crm:view:department","crm:send:sms","crm:manage:campaigns",
                        "inventory:view","finance:view:reports:sales"],
        "default_dashboard": "sales",
    },
    {
        "code": "sales_rep", "name": "Sales Representative", "name_fa": "کارشناس فروش",
        "level": 4, "data_scope": "own", "role_type": "system",
        "permissions": ["sales:view:own","sales:create","sales:edit:own",
                        "crm:view:own","crm:send:sms","inventory:view"],
        "default_dashboard": "sales",
    },
    {
        "code": "inventory_manager", "name": "Inventory Manager", "name_fa": "مدیر انبار",
        "level": 3, "data_scope": "all", "role_type": "system",
        "permissions": ["inventory:view","inventory:create","inventory:edit",
                        "inventory:delete","inventory:adjust","inventory:view:cost",
                        "procurement:view","sales:view:all"],
        "default_dashboard": "inventory",
    },
    {
        "code": "accountant", "name": "Accountant", "name_fa": "حسابدار",
        "level": 3, "data_scope": "all", "role_type": "system",
        "permissions": ["finance:view:all","finance:create:journal","finance:edit:draft",
                        "sales:view:all","procurement:view","inventory:view",
                        "hr:view:payroll","bi:export"],
        "default_dashboard": "finance",
    },
    {
        "code": "hr_manager", "name": "HR Manager", "name_fa": "مدیر منابع انسانی",
        "level": 3, "data_scope": "all", "role_type": "system",
        "permissions": ["hr:view:all","hr:edit:employee","hr:approve:leave",
                        "hr:view:payroll","bi:dashboard:hr","finance:view:payroll"],
        "default_dashboard": "hr",
    },
    {
        "code": "procurement_manager", "name": "Procurement Manager", "name_fa": "مدیر خرید",
        "level": 3, "data_scope": "all", "role_type": "system",
        "permissions": ["procurement:view","procurement:create","procurement:approve",
                        "inventory:view","finance:view:reports"],
        "default_dashboard": "procurement",
    },
    {
        "code": "viewer", "name": "Read-Only Viewer", "name_fa": "مشاهده‌گر",
        "level": 5, "data_scope": "department", "role_type": "system",
        "permissions": ["inventory:view","sales:view:department",
                        "finance:view:reports","hr:view:attendance"],
        "default_dashboard": "dashboard",
    },
]


def upgrade() -> None:
    def e(values, name):
        return postgresql.ENUM(*values, name=name, create_type=True)

    user_status = e(["active","inactive","suspended","pending_verification"], "userstatus")
    device_type = e(["desktop","mobile","tablet","api"], "devicetype_auth")
    perm_cat = e(["operational","administrative","system"], "permissioncategory")
    role_type = e(["system","custom"], "roletype")
    data_scope = e(["own","department","branch","company","all"], "datascope")
    audit_action = e(["create","update","delete","view","login","logout","login_failed","export","approve","reject","suspend","activate","password_change","permission_change","session_revoke","system"], "auditaction")
    audit_status = e(["success","failure","denied"], "auditstatus")
    theme_enum = e(["light","dark","system"], "theme")

    # ── permissions ───────────────────────────────────────────────────────
    op.create_table("permissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("scope", sa.String(50), nullable=True),
        sa.Column("category", perm_cat, nullable=False, server_default="operational"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_index("ix_permissions_module", "permissions", ["module"])
    op.create_index("ix_permissions_code", "permissions", ["code"])

    # ── roles ──────────────────────────────────────────────────────────────
    op.create_table("roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_fa", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("role_type", role_type, nullable=False, server_default="custom"),
        sa.Column("level", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("data_scope", data_scope, nullable=False, server_default="own"),
        sa.Column("max_users", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("default_dashboard", sa.String(50), nullable=True),
        sa.Column("allowed_modules", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.CheckConstraint("level >= 0 AND level <= 10", name="chk_role_level"),
    )
    op.create_index("ix_roles_code", "roles", ["code"])

    # ── role_permissions ───────────────────────────────────────────────────
    op.create_table("role_permissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conditions", postgresql.JSON(), nullable=True),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("granted_by_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    # ── Augment existing users table with new columns ──────────────────────
    # (In a fresh install these columns are added; in upgrade they extend existing table)
    for col_def in [
        ("first_name_fa", sa.String(100), True),
        ("last_name_fa", sa.String(100), True),
        ("phone", sa.String(30), True),
        ("avatar_url", sa.String(500), True),
        ("employee_id", sa.Integer(), True),
        ("status", user_status, False),  # will add server_default
        ("email_verified", sa.Boolean(), False),
        ("phone_verified", sa.Boolean(), False),
        ("failed_login_attempts", sa.Integer(), False),
        ("locked_until", sa.DateTime(timezone=True), True),
        ("password_changed_at", sa.DateTime(timezone=True), True),
        ("password_expires_at", sa.DateTime(timezone=True), True),
        ("last_login_ip", sa.String(50), True),
        ("force_password_change", sa.Boolean(), False),
        ("mfa_enabled", sa.Boolean(), False),
        ("mfa_secret_encrypted", sa.Text(), True),
        ("backup_codes_hashed", postgresql.JSON(), True),
        ("language", sa.String(5), False),
        ("timezone", sa.String(50), False),
        ("theme", theme_enum, False),
        ("notification_preferences", postgresql.JSON(), True),
        ("deleted_at", sa.DateTime(timezone=True), True),
        ("deleted_by_id", sa.Integer(), True),
    ]:
        col_name, col_type, nullable = col_def
        try:
            op.add_column("users", sa.Column(col_name, col_type, nullable=nullable,
                server_default=("active" if col_name == "status" else
                               ("false" if col_name in ("email_verified","phone_verified","mfa_enabled","force_password_change") else
                               ("0" if col_name == "failed_login_attempts" else
                               ("fa" if col_name == "language" else
                               ("Asia/Tehran" if col_name == "timezone" else
                               ("system" if col_name == "theme" else None))))))))
        except Exception:
            pass  # Column may already exist in fresh installs

    # ── user_roles ─────────────────────────────────────────────────────────
    op.create_table("user_roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("assigned_by_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="true"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )

    # ── user_permission_overrides ──────────────────────────────────────────
    op.create_table("user_permission_overrides",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("override_type", sa.String(10), nullable=False),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("granted_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "permission_id", "override_type", name="uq_user_perm_override"),
        sa.CheckConstraint("override_type IN ('grant', 'deny')", name="chk_override_type"),
    )

    # ── user_sessions ──────────────────────────────────────────────────────
    op.create_table("user_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_jti", sa.String(100), nullable=False, unique=True),
        sa.Column("device_type", device_type, nullable=False, server_default="desktop"),
        sa.Column("device_name", sa.String(200), nullable=True),
        sa.Column("os", sa.String(100), nullable=True),
        sa.Column("browser", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoke_reason", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_sessions_jti", "user_sessions", ["token_jti"])
    op.create_index("ix_user_sessions_user_active", "user_sessions", ["user_id", "is_active"])

    # ── password_history ───────────────────────────────────────────────────
    op.create_table("password_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── user_invitations ───────────────────────────────────────────────────
    op.create_table("user_invitations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invited_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(200), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
    )

    # ── audit_logs ─────────────────────────────────────────────────────────
    op.create_table("audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("user_email", sa.String(200), nullable=True),
        sa.Column("action", audit_action, nullable=False),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("resource_description", sa.String(500), nullable=True),
        sa.Column("changes", postgresql.JSON(), nullable=True),
        sa.Column("old_values", postgresql.JSON(), nullable=True),
        sa.Column("new_values", postgresql.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("request_id", sa.String(100), nullable=True),
        sa.Column("status", audit_status, nullable=False, server_default="success"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("is_sensitive", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    for idx_cols in [["user_id"],["action"],["module"],["created_at"],["resource_type","resource_id"]]:
        op.create_index(f"ix_audit_logs_{'_'.join(idx_cols)[:30]}", "audit_logs", idx_cols)

    # ── Seed permissions ───────────────────────────────────────────────────
    perm_table = sa.table("permissions",
        sa.column("code", sa.String), sa.column("name", sa.String),
        sa.column("module", sa.String), sa.column("action", sa.String),
        sa.column("scope", sa.String), sa.column("category", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(perm_table, [
        {"code": p[0], "name": p[1], "module": p[2], "action": p[3],
         "scope": p[4], "category": p[5], "is_active": True}
        for p in PERMISSIONS
    ])

    # ── Seed roles ────────────────────────────────────────────────────────
    role_table = sa.table("roles",
        sa.column("code", sa.String), sa.column("name", sa.String),
        sa.column("name_fa", sa.String), sa.column("level", sa.Integer),
        sa.column("data_scope", sa.String), sa.column("role_type", sa.String),
        sa.column("default_dashboard", sa.String), sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(role_table, [
        {"code": r["code"], "name": r["name"], "name_fa": r.get("name_fa"),
         "level": r["level"], "data_scope": r["data_scope"], "role_type": r["role_type"],
         "default_dashboard": r.get("default_dashboard"), "is_active": True}
        for r in SYSTEM_ROLES
    ])

    # ── Seed role_permissions ─────────────────────────────────────────────
    # (Done via raw SQL after inserts to get IDs)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        CROSS JOIN permissions p
        JOIN (VALUES
    """ + ",\n    ".join(
        f"('{role['code']}', '{perm_code}')"
        for role in SYSTEM_ROLES
        for perm_code in role["permissions"]
    ) + """
        ) AS rp(role_code, perm_code) ON r.code = rp.role_code AND p.code = rp.perm_code
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    for tbl in ["audit_logs","user_invitations","password_history","user_sessions",
                "user_permission_overrides","user_roles","role_permissions","roles","permissions"]:
        op.drop_table(tbl)
    for col in ["first_name_fa","last_name_fa","phone","avatar_url","employee_id","status",
                "email_verified","phone_verified","failed_login_attempts","locked_until",
                "password_changed_at","password_expires_at","last_login_ip","force_password_change",
                "mfa_enabled","mfa_secret_encrypted","backup_codes_hashed",
                "language","timezone","theme","notification_preferences","deleted_at","deleted_by_id"]:
        try:
            op.drop_column("users", col)
        except Exception:
            pass
    for e in ["userstatus","devicetype_auth","permissioncategory","roletype","datascope","auditaction","auditstatus","theme"]:
        op.execute(f"DROP TYPE IF EXISTS {e}")
