"""Add Projects, Budget, and Document tables

Revision ID: 001_add_projects_budget_document
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_add_projects_budget_document'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === PROJECTS TABLES ===
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='planning'),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('actual_start_date', sa.Date(), nullable=True),
        sa.Column('actual_end_date', sa.Date(), nullable=True),
        sa.Column('budget', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('actual_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('progress', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('manager_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_projects_code', 'projects', ['code'])
    op.create_index('ix_projects_status', 'projects', ['status'])
    op.create_index('ix_projects_priority', 'projects', ['priority'])
    op.create_index('ix_projects_manager', 'projects', ['manager_id'])

    # Project Milestones
    op.create_table(
        'project_milestones',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_milestones_project', 'project_milestones', ['project_id'])

    # Project Resources
    op.create_table(
        'project_resources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False, server_default='1'),
        sa.Column('unit_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('availability', sa.Numeric(5, 2), nullable=False, server_default='100'),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_resources_project', 'project_resources', ['project_id'])

    # Project Risks
    op.create_table(
        'project_risks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('probability', sa.Numeric(5, 2), nullable=False, server_default='50'),
        sa.Column('impact', sa.Numeric(5, 2), nullable=False, server_default='50'),
        sa.Column('mitigation_plan', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='open'),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_risks_project', 'project_risks', ['project_id'])

    # === BUDGET TABLES ===
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('period', sa.String(20), nullable=False),
        sa.Column('fiscal_year', sa.String(10), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_budgets_code', 'budgets', ['code'])
    op.create_index('ix_budgets_type', 'budgets', ['type'])
    op.create_index('ix_budgets_fiscal_year', 'budgets', ['fiscal_year'])
    op.create_index('ix_budgets_status', 'budgets', ['status'])

    # Budget Lines
    op.create_table(
        'budget_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('budget_id', sa.Integer(), sa.ForeignKey('budgets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('accounts.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_lines_budget', 'budget_lines', ['budget_id'])

    # Budget Revisions
    op.create_table(
        'budget_revisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('budget_id', sa.Integer(), sa.ForeignKey('budgets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('revision_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_revisions_budget', 'budget_revisions', ['budget_id'])

    # Budget Performance
    op.create_table(
        'budget_performance',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('budget_id', sa.Integer(), sa.ForeignKey('budgets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('accounts.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('period', sa.String(10), nullable=False),
        sa.Column('budget_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('actual_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('variance_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('variance_percentage', sa.Numeric(8, 2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_performance_budget', 'budget_performance', ['budget_id'])

    # === DOCUMENT TABLES ===
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(20), nullable=False, server_default='general'),
        sa.Column('file_path', sa.String(1000), nullable=True),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_documents_category', 'documents', ['category'])

    # Document Versions
    op.create_table(
        'document_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.Integer(), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('change_notes', sa.Text(), nullable=True),
        sa.Column('uploaded_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_document_versions_document', 'document_versions', ['document_id'])


def downgrade() -> None:
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('budget_performance')
    op.drop_table('budget_revisions')
    op.drop_table('budget_lines')
    op.drop_table('budgets')
    op.drop_table('project_risks')
    op.drop_table('project_resources')
    op.drop_table('project_milestones')
    op.drop_table('projects')
