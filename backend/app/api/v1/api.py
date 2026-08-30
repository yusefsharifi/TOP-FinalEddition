"""
API v1 Router — TOP WorX ERP System
Registers all module routers under /api/v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, inventory, finance, hr, crm, procurement,
    bi, report, sales, customer, order, pricing,
    product, sales_representative, subscription, support,
    hse, tasks, documents, contracts, settings, messages,
    quality, projects, budget,
)
from app.api.v1.endpoints import ai, ai_analytics, ai_reports, ai_automation, ai_assistant, ai_module_integration, ai_workflow_automation, ai_scheduler
from app.api.v1.endpoints import ai_module_integration as ai_integration

api_router = APIRouter()

# ── Core ─────────────────────────────────────────────────────────────────────
api_router.include_router(auth.router,              prefix="/auth",              tags=["Auth"])
api_router.include_router(users.router,             prefix="/users",            tags=["Users"])
api_router.include_router(inventory.router,         prefix="/inventory",         tags=["Inventory"])
api_router.include_router(finance.router,           prefix="/accounting",        tags=["Accounting"])
api_router.include_router(hr.router,                prefix="/hr",                tags=["HR"])
api_router.include_router(crm.router,               prefix="/crm",               tags=["CRM"])
api_router.include_router(procurement.router,       prefix="/procurement",       tags=["Procurement"])

# ── Sales & Commerce ────────────────────────────────────────────────────────
api_router.include_router(sales.router,             prefix="/sales",             tags=["Sales"])
api_router.include_router(customer.router,          prefix="/customers",         tags=["Customers"])
api_router.include_router(order.router,             prefix="/orders",            tags=["Orders"])
api_router.include_router(pricing.router,           prefix="/pricing",           tags=["Pricing"])
api_router.include_router(product.router,           prefix="/products",          tags=["Products"])
api_router.include_router(sales_representative.router, prefix="/sales-reps",     tags=["Sales Representatives"])

# ── Analytics & Reporting ────────────────────────────────────────────────────
api_router.include_router(bi.router,                prefix="/bi",                tags=["BI"])
api_router.include_router(report.router,            prefix="/reports",           tags=["Reports"])

# ── Services ─────────────────────────────────────────────────────────────────
api_router.include_router(subscription.router,     prefix="/subscriptions",     tags=["Subscriptions"])
api_router.include_router(support.router,           prefix="/support",           tags=["Support"])

# ── Operations ───────────────────────────────────────────────────────────────
api_router.include_router(hse.router,               prefix="/hse",               tags=["HSE"])
api_router.include_router(tasks.router,             prefix="/tasks",             tags=["Tasks"])
api_router.include_router(ai.router,               prefix="/ai",                tags=["AI"])
api_router.include_router(ai_analytics.router,      prefix="/ai",                tags=["AI Analytics"])
api_router.include_router(ai_reports.router,        prefix="/ai",                tags=["AI Reports"])
api_router.include_router(ai_automation.router,     prefix="/ai",                tags=["AI Automation"])
api_router.include_router(ai_assistant.router,     prefix="/ai",                tags=["AI Assistant"])
api_router.include_router(ai_module_integration.router, prefix="/ai",                tags=["AI Module Integration"])
api_router.include_router(ai_workflow_automation.router, prefix="/ai",            tags=["AI Workflow Automation"])
api_router.include_router(ai_scheduler.router,                   prefix="/ai",            tags=["AI Scheduler"])
api_router.include_router(ai_integration.router,       prefix="/ai",            tags=["AI Module Integration"])
api_router.include_router(documents.router,         prefix="/documents",         tags=["Documents"])
api_router.include_router(contracts.router,         prefix="/contracts",         tags=["Contracts"])

# ── Administration ───────────────────────────────────────────────────────────
api_router.include_router(settings.router,          prefix="/settings",          tags=["Settings"])
api_router.include_router(messages.router,          prefix="/messages",          tags=["Messages"])
api_router.include_router(quality.router,           prefix="/quality",           tags=["Quality"])

# ── Projects & Budget ────────────────────────────────────────────────────────
api_router.include_router(projects.router,          prefix="/projects",         tags=["Projects"])
api_router.include_router(budget.router,            prefix="/budget",           tags=["Budget"])
