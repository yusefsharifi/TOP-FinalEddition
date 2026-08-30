"""
Standalone migration script for TOP WorX ERP new modules.

Usage:
    DATABASE_URL=postgresql://user:pass@localhost/topworx_db python run_migration.py
    python run_migration.py --sqlite

Creates tables for: HSE, Tasks, Contracts, Messages, Settings.
Uses raw SQL extracted from the Alembic migration 0010_operations_modules.py.
"""
import os
import argparse
from sqlalchemy import create_engine, text


# SQL statements extracted from alembic/versions/0010_operations_modules.py
# Adapted to work with both PostgreSQL and SQLite

POSTGRESQL_MIGRATION = """
-- ============================================================================
-- HSE MODULE
-- ============================================================================

CREATE TYPE IF NOT EXISTS incidentseverity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE IF NOT EXISTS incidentstatus AS ENUM ('open', 'under_investigation', 'resolved', 'closed');
CREATE TYPE IF NOT EXISTS checkliststatus AS ENUM ('pending', 'in_progress', 'passed', 'failed');

CREATE TABLE IF NOT EXISTS hse_incidents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    description TEXT NOT NULL,
    severity incidentseverity NOT NULL,
    status incidentstatus NOT NULL DEFAULT 'open',
    location VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    injured_persons INTEGER NOT NULL DEFAULT 0,
    witnesses JSONB,
    immediate_actions TEXT,
    assigned_to_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    investigation_notes TEXT,
    root_cause TEXT,
    corrective_actions TEXT,
    reported_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_status_severity ON hse_incidents (status, severity);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_created_at ON hse_incidents (created_at);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_department ON hse_incidents (department);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_reported_by ON hse_incidents (reported_by_id);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_assigned_to ON hse_incidents (assigned_to_id);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_resolved_at ON hse_incidents (resolved_at);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_dept_status_date ON hse_incidents (department, status, created_at);

CREATE TABLE IF NOT EXISTS hse_checklists (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    location VARCHAR(200) NOT NULL,
    status checkliststatus NOT NULL DEFAULT 'pending',
    inspector_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_hse_checklists_location ON hse_checklists (location);
CREATE INDEX IF NOT EXISTS ix_hse_checklists_created_at ON hse_checklists (created_at);
CREATE INDEX IF NOT EXISTS ix_hse_checklists_inspector ON hse_checklists (inspector_id);
CREATE INDEX IF NOT EXISTS ix_hse_checklists_status_created ON hse_checklists (status, created_at);

CREATE TABLE IF NOT EXISTS hse_checklist_items (
    id SERIAL PRIMARY KEY,
    checklist_id INTEGER NOT NULL REFERENCES hse_checklists(id) ON DELETE CASCADE,
    text VARCHAR(500) NOT NULL,
    status checkliststatus NOT NULL DEFAULT 'pending',
    notes TEXT,
    photo_url VARCHAR(500)
);
CREATE INDEX IF NOT EXISTS ix_hse_checklist_items_checklist_id ON hse_checklist_items (checklist_id);
CREATE INDEX IF NOT EXISTS ix_hse_checklist_items_status ON hse_checklist_items (status);

CREATE TABLE IF NOT EXISTS hse_alerts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    message TEXT NOT NULL,
    severity incidentseverity NOT NULL,
    target_department VARCHAR(100),
    created_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_hse_alerts_severity ON hse_alerts (severity);
CREATE INDEX IF NOT EXISTS ix_hse_alerts_created_at ON hse_alerts (created_at);
CREATE INDEX IF NOT EXISTS ix_hse_alerts_target_dept ON hse_alerts (target_department);

-- ============================================================================
-- TASKS MODULE
-- ============================================================================

CREATE TYPE IF NOT EXISTS taskpriority AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE IF NOT EXISTS projecttaskstatus AS ENUM ('pending', 'in_progress', 'completed', 'cancelled', 'blocked');

CREATE TABLE IF NOT EXISTS project_tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300) NOT NULL,
    description TEXT,
    status projecttaskstatus NOT NULL DEFAULT 'pending',
    priority taskpriority NOT NULL DEFAULT 'medium',
    assigned_to_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    due_date TIMESTAMPTZ,
    parent_task_id INTEGER REFERENCES project_tasks(id) ON DELETE SET NULL,
    created_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_project_tasks_status_priority ON project_tasks (status, priority);
CREATE INDEX IF NOT EXISTS ix_project_tasks_assigned ON project_tasks (assigned_to_id, status);
CREATE INDEX IF NOT EXISTS ix_project_tasks_due ON project_tasks (due_date);
CREATE INDEX IF NOT EXISTS ix_project_tasks_created_by ON project_tasks (created_by_id);
CREATE INDEX IF NOT EXISTS ix_project_tasks_parent ON project_tasks (parent_task_id);
CREATE INDEX IF NOT EXISTS ix_project_tasks_created_at ON project_tasks (created_at);
CREATE INDEX IF NOT EXISTS ix_project_tasks_assigned_due ON project_tasks (assigned_to_id, due_date);

CREATE TABLE IF NOT EXISTS task_project_comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES project_tasks(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_task_project_comments_task_id ON task_project_comments (task_id);
CREATE INDEX IF NOT EXISTS ix_task_comments_created_by ON task_project_comments (created_by_id);
CREATE INDEX IF NOT EXISTS ix_task_comments_created_at ON task_project_comments (created_at);

-- ============================================================================
-- CONTRACTS MODULE
-- ============================================================================

CREATE TYPE IF NOT EXISTS contracttype AS ENUM ('sales', 'purchase', 'employment', 'service', 'lease', 'nda', 'other');
CREATE TYPE IF NOT EXISTS contractstatus AS ENUM ('draft', 'pending_approval', 'approved', 'active', 'expired', 'terminated', 'renewed');

CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    contract_type contracttype NOT NULL,
    status contractstatus NOT NULL DEFAULT 'draft',
    counterparty_name VARCHAR(200) NOT NULL,
    counterparty_contact VARCHAR(200),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    value FLOAT,
    currency VARCHAR(10) NOT NULL DEFAULT 'IRR',
    terms TEXT,
    auto_renew BOOLEAN NOT NULL DEFAULT FALSE,
    renewal_days_notice INTEGER NOT NULL DEFAULT 30,
    created_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    approved_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_contracts_status_type ON contracts (status, contract_type);
CREATE INDEX IF NOT EXISTS ix_contracts_end_date ON contracts (end_date);
CREATE INDEX IF NOT EXISTS ix_contracts_counterparty ON contracts (counterparty_name);
CREATE INDEX IF NOT EXISTS ix_contracts_created_by ON contracts (created_by_id);
CREATE INDEX IF NOT EXISTS ix_contracts_approved_by ON contracts (approved_by_id);
CREATE INDEX IF NOT EXISTS ix_contracts_start_date ON contracts (start_date);
CREATE INDEX IF NOT EXISTS ix_contracts_value ON contracts (value);
CREATE INDEX IF NOT EXISTS ix_contracts_auto_renew_expiry ON contracts (auto_renew, end_date);
CREATE INDEX IF NOT EXISTS ix_contracts_status_end_date ON contracts (status, end_date);

CREATE TABLE IF NOT EXISTS contract_attachments (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    file_name VARCHAR(300) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_contract_attachments_contract_id ON contract_attachments (contract_id);
CREATE INDEX IF NOT EXISTS ix_contract_attachments_uploader ON contract_attachments (uploaded_by_id);

CREATE TABLE IF NOT EXISTS contract_history (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    notes TEXT,
    performed_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_contract_history_contract_id ON contract_history (contract_id);
CREATE INDEX IF NOT EXISTS ix_contract_history_action ON contract_history (action);
CREATE INDEX IF NOT EXISTS ix_contract_history_performed_at ON contract_history (performed_at);
CREATE INDEX IF NOT EXISTS ix_contract_history_performed_by ON contract_history (performed_by_id);

-- ============================================================================
-- MESSAGES MODULE
-- ============================================================================

CREATE TYPE IF NOT EXISTS messagepriority AS ENUM ('low', 'normal', 'high', 'urgent');
CREATE TYPE IF NOT EXISTS notificationseverity AS ENUM ('info', 'warning', 'error', 'success');

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    is_group BOOLEAN NOT NULL DEFAULT FALSE,
    created_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_conversations_created ON conversations (created_at);
CREATE INDEX IF NOT EXISTS ix_conversations_is_group ON conversations (is_group);
CREATE INDEX IF NOT EXISTS ix_conversations_created_by ON conversations (created_by_id);

CREATE TABLE IF NOT EXISTS conversation_participants (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    last_read_at TIMESTAMPTZ,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_muted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(conversation_id, user_id)
);
CREATE INDEX IF NOT EXISTS ix_conversation_participants_conversation_id ON conversation_participants (conversation_id);
CREATE INDEX IF NOT EXISTS ix_conversation_participants_user_id ON conversation_participants (user_id);
CREATE INDEX IF NOT EXISTS ix_conv_participants_last_read ON conversation_participants (last_read_at);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    priority messagepriority NOT NULL DEFAULT 'normal',
    parent_message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_messages_conversation_created ON messages (conversation_id, created_at);
CREATE INDEX IF NOT EXISTS ix_messages_sender ON messages (sender_id);
CREATE INDEX IF NOT EXISTS ix_messages_priority ON messages (priority);

CREATE TABLE IF NOT EXISTS message_read_receipts (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    read_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(message_id, user_id)
);
CREATE INDEX IF NOT EXISTS ix_message_read_receipts_message_id ON message_read_receipts (message_id);
CREATE INDEX IF NOT EXISTS ix_read_receipts_user ON message_read_receipts (user_id);
CREATE INDEX IF NOT EXISTS ix_read_receipts_read_at ON message_read_receipts (read_at);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(300) NOT NULL,
    message TEXT NOT NULL,
    severity notificationseverity NOT NULL DEFAULT 'info',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at TIMESTAMPTZ,
    source_module VARCHAR(50),
    source_id INTEGER
);
CREATE INDEX IF NOT EXISTS ix_notifications_user_unread ON notifications (user_id, is_read);
CREATE INDEX IF NOT EXISTS ix_notifications_created ON notifications (created_at);
CREATE INDEX IF NOT EXISTS ix_notifications_severity ON notifications (severity);
CREATE INDEX IF NOT EXISTS ix_notifications_source ON notifications (source_module, source_id);

-- ============================================================================
-- SETTINGS MODULE
-- ============================================================================

CREATE TYPE IF NOT EXISTS settingcategory AS ENUM ('general', 'security', 'email', 'notification', 'integration', 'ui', 'finance', 'hr', 'inventory');
CREATE TYPE IF NOT EXISTS moduleauditaction AS ENUM ('create', 'update', 'delete', 'view', 'login', 'logout', 'login_failed', 'export', 'import', 'approve', 'reject');

CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT NOT NULL,
    value_type VARCHAR(20) NOT NULL DEFAULT 'string',
    description VARCHAR(500),
    category settingcategory NOT NULL DEFAULT 'general',
    is_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    is_readonly BOOLEAN NOT NULL DEFAULT FALSE,
    updated_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_system_settings_key ON system_settings (key);
CREATE INDEX IF NOT EXISTS ix_system_settings_category ON system_settings (category);
CREATE INDEX IF NOT EXISTS ix_system_settings_sensitive ON system_settings (is_sensitive);
CREATE INDEX IF NOT EXISTS ix_system_settings_value_type ON system_settings (value_type);

CREATE TABLE IF NOT EXISTS module_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    user_email VARCHAR(200),
    action moduleauditaction NOT NULL,
    module VARCHAR(50) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id INTEGER,
    resource_description VARCHAR(500),
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_module_audit_user_id ON module_audit_logs (user_id);
CREATE INDEX IF NOT EXISTS ix_module_audit_action ON module_audit_logs (action);
CREATE INDEX IF NOT EXISTS ix_module_audit_module ON module_audit_logs (module);
CREATE INDEX IF NOT EXISTS ix_module_audit_resource ON module_audit_logs (resource_type, resource_id);
CREATE INDEX IF NOT EXISTS ix_module_audit_created ON module_audit_logs (created_at);
CREATE INDEX IF NOT EXISTS ix_module_audit_user_date ON module_audit_logs (user_id, created_at);

CREATE TABLE IF NOT EXISTS system_notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    target_roles JSONB,
    expires_at TIMESTAMPTZ,
    created_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_system_notifications_active ON system_notifications (is_active, created_at);
CREATE INDEX IF NOT EXISTS ix_system_notifications_severity ON system_notifications (severity);
CREATE INDEX IF NOT EXISTS ix_system_notifications_expires ON system_notifications (expires_at);
"""

SQLITE_MIGRATION = """
-- ============================================================================
-- HSE MODULE (SQLite)
-- ============================================================================
CREATE TABLE IF NOT EXISTS hse_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(300) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    location VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    injured_persons INTEGER NOT NULL DEFAULT 0,
    witnesses TEXT,
    immediate_actions TEXT,
    assigned_to_id INTEGER REFERENCES users(id),
    investigation_notes TEXT,
    root_cause TEXT,
    corrective_actions TEXT,
    reported_by_id INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME
);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_status_severity ON hse_incidents (status, severity);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_created_at ON hse_incidents (created_at);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_department ON hse_incidents (department);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_reported_by ON hse_incidents (reported_by_id);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_assigned_to ON hse_incidents (assigned_to_id);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_resolved_at ON hse_incidents (resolved_at);
CREATE INDEX IF NOT EXISTS ix_hse_incidents_dept_status_date ON hse_incidents (department, status, created_at);

CREATE TABLE IF NOT EXISTS hse_checklists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    location VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    inspector_id INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);
CREATE INDEX IF NOT EXISTS ix_hse_checklists_location ON hse_checklists (location);
CREATE INDEX IF NOT EXISTS ix_hse_checklists_created_at ON hse_checklists (created_at);
CREATE INDEX IF NOT EXISTS ix_hse_checklists_inspector ON hse_checklists (inspector_id);
CREATE INDEX IF NOT EXISTS ix_hse_checklists_status_created ON hse_checklists (status, created_at);

CREATE TABLE IF NOT EXISTS hse_checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checklist_id INTEGER NOT NULL REFERENCES hse_checklists(id) ON DELETE CASCADE,
    text VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT,
    photo_url VARCHAR(500)
);
CREATE INDEX IF NOT EXISTS ix_hse_checklist_items_checklist_id ON hse_checklist_items (checklist_id);
CREATE INDEX IF NOT EXISTS ix_hse_checklist_items_status ON hse_checklist_items (status);

CREATE TABLE IF NOT EXISTS hse_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(300) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    target_department VARCHAR(100),
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_hse_alerts_severity ON hse_alerts (severity);
CREATE INDEX IF NOT EXISTS ix_hse_alerts_created_at ON hse_alerts (created_at);
CREATE INDEX IF NOT EXISTS ix_hse_alerts_target_dept ON hse_alerts (target_department);

-- ============================================================================
-- TASKS MODULE (SQLite)
-- ============================================================================
CREATE TABLE IF NOT EXISTS project_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(300) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    assigned_to_id INTEGER REFERENCES users(id),
    due_date DATETIME,
    parent_task_id INTEGER REFERENCES project_tasks(id),
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME
);
CREATE INDEX IF NOT EXISTS ix_project_tasks_status_priority ON project_tasks (status, priority);
CREATE INDEX IF NOT EXISTS ix_project_tasks_assigned ON project_tasks (assigned_to_id, status);
CREATE INDEX IF NOT EXISTS ix_project_tasks_due ON project_tasks (due_date);
CREATE INDEX IF NOT EXISTS ix_project_tasks_created_by ON project_tasks (created_by_id);
CREATE INDEX IF NOT EXISTS ix_project_tasks_parent ON project_tasks (parent_task_id);
CREATE INDEX IF NOT EXISTS ix_project_tasks_created_at ON project_tasks (created_at);
CREATE INDEX IF NOT EXISTS ix_project_tasks_assigned_due ON project_tasks (assigned_to_id, due_date);

CREATE TABLE IF NOT EXISTS task_project_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES project_tasks(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_task_project_comments_task_id ON task_project_comments (task_id);
CREATE INDEX IF NOT EXISTS ix_task_comments_created_by ON task_project_comments (created_by_id);
CREATE INDEX IF NOT EXISTS ix_task_comments_created_at ON task_project_comments (created_at);

-- ============================================================================
-- CONTRACTS MODULE (SQLite)
-- ============================================================================
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    contract_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    counterparty_name VARCHAR(200) NOT NULL,
    counterparty_contact VARCHAR(200),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    value FLOAT,
    currency VARCHAR(10) NOT NULL DEFAULT 'IRR',
    terms TEXT,
    auto_renew BOOLEAN NOT NULL DEFAULT 0,
    renewal_days_notice INTEGER NOT NULL DEFAULT 30,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    approved_by_id INTEGER REFERENCES users(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME
);
CREATE INDEX IF NOT EXISTS ix_contracts_status_type ON contracts (status, contract_type);
CREATE INDEX IF NOT EXISTS ix_contracts_end_date ON contracts (end_date);
CREATE INDEX IF NOT EXISTS ix_contracts_counterparty ON contracts (counterparty_name);
CREATE INDEX IF NOT EXISTS ix_contracts_created_by ON contracts (created_by_id);
CREATE INDEX IF NOT EXISTS ix_contracts_approved_by ON contracts (approved_by_id);
CREATE INDEX IF NOT EXISTS ix_contracts_start_date ON contracts (start_date);
CREATE INDEX IF NOT EXISTS ix_contracts_value ON contracts (value);
CREATE INDEX IF NOT EXISTS ix_contracts_auto_renew_expiry ON contracts (auto_renew, end_date);
CREATE INDEX IF NOT EXISTS ix_contracts_status_end_date ON contracts (status, end_date);

CREATE TABLE IF NOT EXISTS contract_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    file_name VARCHAR(300) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by_id INTEGER NOT NULL REFERENCES users(id),
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_contract_attachments_contract_id ON contract_attachments (contract_id);
CREATE INDEX IF NOT EXISTS ix_contract_attachments_uploader ON contract_attachments (uploaded_by_id);

CREATE TABLE IF NOT EXISTS contract_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    notes TEXT,
    performed_by_id INTEGER NOT NULL REFERENCES users(id),
    performed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_contract_history_contract_id ON contract_history (contract_id);
CREATE INDEX IF NOT EXISTS ix_contract_history_action ON contract_history (action);
CREATE INDEX IF NOT EXISTS ix_contract_history_performed_at ON contract_history (performed_at);
CREATE INDEX IF NOT EXISTS ix_contract_history_performed_by ON contract_history (performed_by_id);

-- ============================================================================
-- MESSAGES MODULE (SQLite)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200),
    is_group BOOLEAN NOT NULL DEFAULT 0,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_conversations_created ON conversations (created_at);
CREATE INDEX IF NOT EXISTS ix_conversations_is_group ON conversations (is_group);
CREATE INDEX IF NOT EXISTS ix_conversations_created_by ON conversations (created_by_id);

CREATE TABLE IF NOT EXISTS conversation_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    last_read_at DATETIME,
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_muted BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE(conversation_id, user_id)
);
CREATE INDEX IF NOT EXISTS ix_conversation_participants_conversation_id ON conversation_participants (conversation_id);
CREATE INDEX IF NOT EXISTS ix_conversation_participants_user_id ON conversation_participants (user_id);
CREATE INDEX IF NOT EXISTS ix_conv_participants_last_read ON conversation_participants (last_read_at);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    priority VARCHAR(10) NOT NULL DEFAULT 'normal',
    parent_message_id INTEGER REFERENCES messages(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_messages_conversation_created ON messages (conversation_id, created_at);
CREATE INDEX IF NOT EXISTS ix_messages_sender ON messages (sender_id);
CREATE INDEX IF NOT EXISTS ix_messages_priority ON messages (priority);

CREATE TABLE IF NOT EXISTS message_read_receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    read_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(message_id, user_id)
);
CREATE INDEX IF NOT EXISTS ix_message_read_receipts_message_id ON message_read_receipts (message_id);
CREATE INDEX IF NOT EXISTS ix_read_receipts_user ON message_read_receipts (user_id);
CREATE INDEX IF NOT EXISTS ix_read_receipts_read_at ON message_read_receipts (read_at);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(300) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(10) NOT NULL DEFAULT 'info',
    is_read BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_at DATETIME,
    source_module VARCHAR(50),
    source_id INTEGER
);
CREATE INDEX IF NOT EXISTS ix_notifications_user_unread ON notifications (user_id, is_read);
CREATE INDEX IF NOT EXISTS ix_notifications_created ON notifications (created_at);
CREATE INDEX IF NOT EXISTS ix_notifications_severity ON notifications (severity);
CREATE INDEX IF NOT EXISTS ix_notifications_source ON notifications (source_module, source_id);

-- ============================================================================
-- SETTINGS MODULE (SQLite)
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT NOT NULL,
    value_type VARCHAR(20) NOT NULL DEFAULT 'string',
    description VARCHAR(500),
    category VARCHAR(20) NOT NULL DEFAULT 'general',
    is_sensitive BOOLEAN NOT NULL DEFAULT 0,
    is_readonly BOOLEAN NOT NULL DEFAULT 0,
    updated_by_id INTEGER REFERENCES users(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_system_settings_key ON system_settings (key);
CREATE INDEX IF NOT EXISTS ix_system_settings_category ON system_settings (category);
CREATE INDEX IF NOT EXISTS ix_system_settings_sensitive ON system_settings (is_sensitive);
CREATE INDEX IF NOT EXISTS ix_system_settings_value_type ON system_settings (value_type);

CREATE TABLE IF NOT EXISTS module_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    user_email VARCHAR(200),
    action VARCHAR(20) NOT NULL,
    module VARCHAR(50) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id INTEGER,
    resource_description VARCHAR(500),
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_module_audit_user_id ON module_audit_logs (user_id);
CREATE INDEX IF NOT EXISTS ix_module_audit_action ON module_audit_logs (action);
CREATE INDEX IF NOT EXISTS ix_module_audit_module ON module_audit_logs (module);
CREATE INDEX IF NOT EXISTS ix_module_audit_resource ON module_audit_logs (resource_type, resource_id);
CREATE INDEX IF NOT EXISTS ix_module_audit_created ON module_audit_logs (created_at);
CREATE INDEX IF NOT EXISTS ix_module_audit_user_date ON module_audit_logs (user_id, created_at);

CREATE TABLE IF NOT EXISTS system_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(300) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    target_roles TEXT,
    expires_at DATETIME,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_system_notifications_active ON system_notifications (is_active, created_at);
CREATE INDEX IF NOT EXISTS ix_system_notifications_severity ON system_notifications (severity);
CREATE INDEX IF NOT EXISTS ix_system_notifications_expires ON system_notifications (expires_at);
"""


def main():
    parser = argparse.ArgumentParser(description="Apply TOP WorX new module migrations")
    parser.add_argument("--sqlite", action="store_true", help="Use SQLite instead of PostgreSQL")
    parser.add_argument("--check", action="store_true", help="Check which tables exist")
    args = parser.parse_args()

    if args.sqlite:
        db_url = "sqlite:///./migration_test.db"
    else:
        db_url = os.environ.get("DATABASE_URL", "")
        if not db_url:
            user = os.environ.get("POSTGRES_USER", "topworx")
            password = os.environ.get("POSTGRES_PASSWORD", "")
            host = os.environ.get("POSTGRES_SERVER", "localhost")
            port = os.environ.get("POSTGRES_PORT", "5432")
            db = os.environ.get("POSTGRES_DB", "topworx_db")
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    print(f"Database: {db_url.split('@')[-1] if '@' in db_url else db_url}")

    engine = create_engine(db_url)

    # Check existing tables
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
            if not args.sqlite else
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ))
        existing = {row[0] for row in result}

    new_tables = [
        "hse_incidents", "hse_checklists", "hse_checklist_items", "hse_alerts",
        "project_tasks", "task_project_comments",
        "contracts", "contract_attachments", "contract_history",
        "conversations", "conversation_participants", "messages",
        "message_read_receipts", "notifications",
        "system_settings", "module_audit_logs", "system_notifications",
    ]

    already_exist = [t for t in new_tables if t in existing]
    to_create = [t for t in new_tables if t not in existing]

    print(f"\nAlready exist: {len(already_exist)}")
    print(f"To create: {len(to_create)}")

    if already_exist:
        print("\nExisting tables:")
        for t in already_exist:
            print(f"  ✓ {t}")

    if to_create:
        print("\nCreating tables:")
        for t in to_create:
            print(f"  + {t}")

        sql = SQLITE_MIGRATION if args.sqlite else POSTGRESQL_MIGRATION
        # Remove comment lines and split on semicolons
        lines = []
        for line in sql.split(chr(10)):
            stripped = line.strip()
            if stripped.startswith('--') or stripped == '':
                continue
            lines.append(line)
        clean_sql = chr(10).join(lines)
        statements = [s.strip() for s in clean_sql.split(';') if s.strip()]
        with engine.connect() as conn:
            if args.sqlite:
                conn.execute(text('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT)'))
                conn.execute(text('PRAGMA foreign_keys = OFF'))  # Disable FK checks for creation
            succeeded = 0
            failed = 0
            for stmt in statements:
                try:
                    conn.execute(text(stmt))
                    succeeded += 1
                except Exception as e:
                    failed += 1
                    print(f"  FAILED: {str(e)[:120]}")
                    print(f"  SQL: {stmt[:80]}...")
            if args.sqlite:
                conn.execute(text('PRAGMA foreign_keys = ON'))
            conn.commit()
            print(f"\nStatements: {succeeded} succeeded, {failed} failed")

        print("\nMigration complete!")
    else:
        print("\nAll tables already exist. Nothing to do.")


if __name__ == "__main__":
    main()
