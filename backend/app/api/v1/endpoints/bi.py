"""
BI Module — FastAPI Router
TOP WorX ERP System

INTEGRATION POINT: Register in api.py:
    from app.api.api_v1.endpoints.bi import router as bi_router
    api_router.include_router(bi_router, prefix="/bi", tags=["business-intelligence"])
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import select

from app.models.bi import AlertEvent, AlertRule, KPISnapshot, ReportTemplate
from app.services.alert_service import alert_service
from app.services.dashboard_service import dashboard_service, report_builder
from app.services.etl_service import etl_service
from app.services.kpi_service import kpi_service

# ---------------------------------------------------------------------------
# Real dependencies from centralized deps module
# ---------------------------------------------------------------------------
from app.api.deps import DBDep, CurrentUser as CU

router = APIRouter()


# ===========================================================================
# DASHBOARDS
# ===========================================================================
@router.get("/dashboard/ceo")
async def ceo_dashboard(
    db: DBDep, cu: CU,
    year: int = Query(1403), month: int = Query(1, ge=1, le=12),
) -> dict:
    """Executive summary dashboard — KPIs, revenue trend, expense breakdown, cash forecast."""
    # TODO: require_role(cu, ["admin", "ceo", "board"])
    return await dashboard_service.ceo_dashboard(db, year, month)


@router.get("/dashboard/cfo")
async def cfo_dashboard(
    db: DBDep, cu: CU,
    year: int = Query(1403), month: int = Query(1, ge=1, le=12),
) -> dict:
    """CFO financial deep dive — balance sheet, P&L, working capital, AR/AP aging."""
    # TODO: require_role(cu, ["admin", "cfo", "finance_manager"])
    return await dashboard_service.cfo_dashboard(db, year, month)


@router.get("/dashboard/sales")
async def sales_dashboard(
    db: DBDep, cu: CU,
    year: int = Query(1403), month: int = Query(1, ge=1, le=12),
) -> dict:
    """Sales manager — funnel, top customers, product performance."""
    return await dashboard_service.sales_dashboard(db, year, month)


@router.get("/dashboard/inventory")
async def inventory_dashboard(db: DBDep, cu: CU) -> dict:
    """Inventory manager — stock levels, ABC analysis, reorder suggestions."""
    return await dashboard_service.inventory_dashboard(db)


@router.get("/dashboard/hr")
async def hr_dashboard(
    db: DBDep, cu: CU,
    year: int = Query(1403), month: int = Query(1, ge=1, le=12),
) -> dict:
    """HR manager — headcount, payroll costs, attendance."""
    return await dashboard_service.hr_dashboard(db, year, month)


# ===========================================================================
# KPIs
# ===========================================================================
@router.get("/kpis")
async def get_all_kpis(
    db: DBDep, cu: CU,
    year: int = Query(1403), month: int = Query(1, ge=1, le=12),
) -> dict:
    """All current KPI values with health indicators."""
    kpis = await kpi_service.get_all_kpis(db, year, month)
    return {
        k: {
            "name": k, "value": float(v.value), "unit": v.unit,
            "label": v.label, "health": v.health,
            "change_pct": v.change_pct, "metadata": v.metadata,
        }
        for k, v in kpis.items()
    }


@router.get("/kpis/{kpi_name}/history")
async def kpi_history(
    kpi_name: str, db: DBDep, cu: CU,
    days: int = Query(90, ge=7, le=365),
) -> list[dict]:
    """Time-series history for a specific KPI from snapshots table."""
    since = datetime.utcnow().replace(hour=0, minute=0, second=0) - __import__("datetime").timedelta(days=days)
    rows = (await db.execute(
        select(KPISnapshot)
        .where(KPISnapshot.kpi_name == kpi_name, KPISnapshot.snapshot_at >= since)
        .order_by(KPISnapshot.snapshot_at.asc())
    )).scalars().all()
    return [{"snapshot_at": r.snapshot_at.isoformat(), "value": float(r.value), "period_label": r.period_label}
            for r in rows]


# ===========================================================================
# ALERTS
# ===========================================================================
@router.get("/alerts")
async def list_alerts(db: DBDep, cu: CU, unacknowledged_only: bool = False) -> list[dict]:
    """Active alerts for current user."""
    q = select(AlertEvent).order_by(AlertEvent.triggered_at.desc()).limit(100)
    if unacknowledged_only:
        q = q.where(AlertEvent.acknowledged.is_(False))
    rows = (await db.execute(q)).scalars().all()
    return [{"id": r.id, "rule_id": r.rule_id, "triggered_at": r.triggered_at.isoformat(),
             "metric_value": float(r.metric_value), "threshold_value": float(r.threshold_value),
             "message": r.message, "acknowledged": r.acknowledged} for r in rows]


@router.post("/alerts/rules", status_code=201)
async def create_alert_rule(data: dict, db: DBDep, cu: CU) -> dict:
    """Create a new alert rule."""
    # TODO: require_role(cu, ["admin", "finance_manager"])
    rule = AlertRule(
        name=data["name"],
        description=data.get("description"),
        metric=data["metric"],
        condition=data["condition"],
        threshold=Decimal(str(data["threshold"])),
        severity=data.get("severity", "warning"),
        channels=data.get("channels", ["in_app"]),
        recipient_user_ids=data.get("recipient_user_ids", []),
        cooldown_minutes=data.get("cooldown_minutes", 60),
        created_by_id=cu.id,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return {"id": rule.id, "name": rule.name, "metric": rule.metric}


@router.put("/alerts/rules/{rule_id}")
async def update_alert_rule(rule_id: int, data: dict, db: DBDep, cu: CU) -> dict:
    rule = await db.get(AlertRule, rule_id)
    if not rule:
        raise HTTPException(404, "Alert rule not found")
    for field in ["name", "threshold", "condition", "severity", "is_active", "channels", "cooldown_minutes"]:
        if field in data:
            val = data[field]
            if field == "threshold":
                val = Decimal(str(val))
            setattr(rule, field, val)
    await db.commit()
    return {"id": rule.id, "name": rule.name, "is_active": rule.is_active}


@router.post("/alerts/{event_id}/acknowledge")
async def acknowledge_alert(event_id: int, db: DBDep, cu: CU) -> dict:
    event = await db.get(AlertEvent, event_id)
    if not event:
        raise HTTPException(404, "Alert event not found")
    event.acknowledged = True
    event.acknowledged_by_id = cu.id
    event.acknowledged_at = datetime.utcnow()
    await db.commit()
    return {"acknowledged": True}


# ===========================================================================
# REPORTS
# ===========================================================================
@router.post("/reports/build")
async def build_report(data: dict, db: DBDep, cu: CU) -> dict:
    """Ad-hoc report builder — specify base_table, dimensions, measures, filters."""
    try:
        result = await report_builder.build_report(
            db,
            base_table=data.get("base_table", "sales"),
            dimensions=data.get("dimensions", []),
            measures=data.get("measures", ["total_amount"]),
            filters=data.get("filters", {}),
            sort_by=data.get("sort_by", []),
            limit=min(data.get("limit", 1000), 5000),
        )
        return result
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc))


@router.get("/reports/templates")
async def list_report_templates(db: DBDep, cu: CU) -> list[dict]:
    """List system + user-saved report templates."""
    system = report_builder.get_system_templates()
    user_r = await db.execute(
        select(ReportTemplate)
        .where((ReportTemplate.is_public.is_(True)) | (ReportTemplate.created_by_id == cu.id))
        .order_by(ReportTemplate.run_count.desc())
    )
    user_templates = [
        {"id": t.id, "name": t.name, "config": t.config, "is_system": False, "run_count": t.run_count}
        for t in user_r.scalars().all()
    ]
    return system + user_templates


@router.post("/reports/save")
async def save_report_template(data: dict, db: DBDep, cu: CU) -> dict:
    tmpl = await report_builder.save_template(
        db, name=data["name"], config=data["config"],
        user_id=cu.id, is_public=data.get("is_public", False)
    )
    await db.commit()
    return {"id": tmpl.id, "name": tmpl.name}


# ===========================================================================
# ETL & DATA WAREHOUSE
# ===========================================================================
@router.post("/etl/run")
async def trigger_etl(db: DBDep, cu: CU, full: bool = False) -> dict:
    """Manually trigger ETL. Use Celery for scheduled runs in production."""
    # TODO: require_role(cu, ["admin"])
    if full:
        count = await etl_service.populate_dim_date(db)
        dim_counts = await etl_service.sync_dimensions(db)
        await db.commit()
        return {"dim_date_rows": count, "dimensions": dim_counts}
    else:
        run = await etl_service.run_incremental(db)
        await db.commit()
        return {"status": run.status, "rows_inserted": run.rows_inserted,
                "duration_seconds": run.duration_seconds}


@router.post("/etl/init-dates")
async def init_date_dimension(db: DBDep, cu: CU) -> dict:
    """One-time: populate DimDate for 2011–2036. Takes ~30 seconds."""
    # TODO: require_role(cu, ["admin"])
    count = await etl_service.populate_dim_date(db, start_year=2011, end_year=2036)
    await db.commit()
    return {"rows_inserted": count}


# ===========================================================================
# EXPORT
# ===========================================================================
@router.get("/export/excel")
async def export_excel(
    db: DBDep, cu: CU,
    report: str = "sales_by_customer",
    year: int = 1403, month: int = 1,
) -> Response:
    """Export report data as Excel. Requires openpyxl."""
    try:
        import openpyxl
        from io import BytesIO

        template = next((t for t in report_builder.get_system_templates() if t["id"] == report), None)
        if not template:
            raise HTTPException(404, f"Report template '{report}' not found")

        result = await report_builder.build_report(db, **template["config"])
        rows = result.get("data", [])

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = template["name"]

        if rows:
            headers = list(rows[0].keys())
            ws.append(headers)
            for row in rows:
                ws.append([str(v) if v is not None else "" for v in row.values()])

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)

        return Response(
            content=buf.read(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{report}_{year}_{month:02d}.xlsx"'},
        )
    except ImportError:
        raise HTTPException(501, "Excel export requires: pip install openpyxl")
