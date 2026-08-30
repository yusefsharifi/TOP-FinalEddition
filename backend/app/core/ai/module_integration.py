"""
AI Module Integration — Core Integration Layer
TOP WorX ERP System

Provides AI capabilities for each module:
- Predictive analytics
- Anomaly detection
- Natural language insights
- Smart recommendations
"""
from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.engine import AIEngine, get_ai_engine
from app.models.ai_core import InsightType, InsightSeverity


class AIModuleIntegration:
    """Central AI integration service for all ERP modules."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = get_ai_engine(db)
    
    # ══════════════════════════════════════════════════════════════════════════
    # INVENTORY AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def inventory_stockout_prediction(self, user_id: int) -> dict:
        """Predict potential stockouts based on historical movement patterns."""
        from app.models.inventory import InventoryItem, StockLevel, InventoryMovement
        
        # Get items with low stock
        low_stock_items = (await self.db.execute(
            select(InventoryItem, StockLevel)
            .join(StockLevel, StockLevel.item_id == InventoryItem.id)
            .where(StockLevel.quantity_on_hand <= StockLevel.reorder_point)
            .where(InventoryItem.is_active.is_(True))
        )).all()
        
        insights = []
        for item, stock in low_stock_items:
            # Calculate days of stock remaining based on average daily usage
            avg_daily_usage = await self._get_avg_daily_usage(item.id)
            days_remaining = stock.quantity_on_hand / avg_daily_usage if avg_daily_usage > 0 else float('inf')
            
            severity = InsightSeverity.CRITICAL if days_remaining < 3 else InsightSeverity.WARNING
            insights.append({
                "item_id": item.id,
                "item_name": item.name,
                "sku": item.sku,
                "current_stock": float(stock.quantity_on_hand),
                "reorder_point": float(stock.reorder_point),
                "avg_daily_usage": float(avg_daily_usage),
                "days_remaining": round(days_remaining, 1),
                "severity": severity.value,
            })
        
        return {
            "type": "stockout_prediction",
            "total_items_at_risk": len(insights),
            "critical_items": [i for i in insights if i["severity"] == "critical"],
            "warning_items": [i for i in insights if i["severity"] == "warning"],
        }
    
    async def inventory_smart_reorder_suggestions(self, user_id: int) -> dict:
        """Suggest optimal reorder points and quantities."""
        from app.models.inventory import InventoryItem, StockLevel
        
        items = (await self.db.execute(
            select(InventoryItem, StockLevel)
            .join(StockLevel, StockLevel.item_id == InventoryItem.id)
            .where(InventoryItem.is_active.is_(True))
        )).all()
        
        suggestions = []
        for item, stock in items:
            avg_daily_usage = await self._get_avg_daily_usage(item.id)
            if avg_daily_usage > 0:
                # Calculate EOQ (Economic Order Quantity) - simplified
                lead_time_days = 7  # Default lead time
                safety_stock = avg_daily_usage * 3  # 3 days safety stock
                reorder_point = (avg_daily_usage * lead_time_days) + safety_stock
                optimal_qty = avg_daily_usage * 30  # 30 days supply
                
                if stock.quantity_on_hand < reorder_point:
                    suggestions.append({
                        "item_id": item.id,
                        "item_name": item.name,
                        "sku": item.sku,
                        "current_stock": float(stock.quantity_on_hand),
                        "suggested_reorder_point": round(float(reorder_point), 2),
                        "suggested_order_qty": round(float(optimal_qty), 2),
                        "estimated_stockout_days": round(float(stock.quantity_on_hand / avg_daily_usage), 1),
                    })
        
        return {
            "type": "smart_reorder",
            "total_suggestions": len(suggestions),
            "suggestions": sorted(suggestions, key=lambda x: x["estimated_stockout_days"]),
        }
    
    async def inventory_anomaly_detection(self, user_id: int) -> dict:
        """Detect unusual inventory movements."""
        from app.models.inventory import InventoryMovement, MovementType
        
        # Get recent movements (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        movements = (await self.db.execute(
            select(InventoryMovement)
            .where(InventoryMovement.movement_date >= thirty_days_ago)
            .order_by(InventoryMovement.movement_date.desc())
        )).scalars().all()
        
        anomalies = []
        for movement in movements:
            # Check for unusually large quantities
            avg_qty = await self._get_avg_movement_quantity(movement.item_id, movement.movement_type)
            if movement.quantity > avg_qty * 3:  # 3x average is anomalous
                anomalies.append({
                    "movement_id": movement.id,
                    "item_id": movement.item_id,
                    "type": movement.movement_type.value,
                    "quantity": float(movement.quantity),
                    "avg_quantity": float(avg_qty),
                    "deviation_factor": round(float(movement.quantity / avg_qty), 2) if avg_qty > 0 else 0,
                    "date": movement.movement_date.isoformat(),
                })
        
        return {
            "type": "anomaly_detection",
            "total_anomalies": len(anomalies),
            "anomalies": anomalies[:10],  # Top 10
        }
    
    async def _get_avg_daily_usage(self, item_id: int) -> Decimal:
        """Get average daily usage for an item."""
        from app.models.inventory import InventoryMovement, MovementType
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        result = (await self.db.execute(
            select(func.coalesce(func.sum(InventoryMovement.quantity), Decimal("0")))
            .where(
                InventoryMovement.item_id == item_id,
                InventoryMovement.movement_type == MovementType.OUTBOUND,
                InventoryMovement.movement_date >= thirty_days_ago,
            )
        )).scalar()
        
        return result / 30 if result else Decimal("0")
    
    async def _get_avg_movement_quantity(self, item_id: int, movement_type) -> Decimal:
        """Get average quantity for a movement type."""
        from app.models.inventory import InventoryMovement
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        result = (await self.db.execute(
            select(func.coalesce(func.avg(InventoryMovement.quantity), Decimal("0")))
            .where(
                InventoryMovement.item_id == item_id,
                InventoryMovement.movement_type == movement_type,
                InventoryMovement.movement_date >= thirty_days_ago,
            )
        )).scalar()
        
        return result or Decimal("0")
    
    # ══════════════════════════════════════════════════════════════════════════
    # FINANCE AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def finance_cashflow_prediction(self, user_id: int) -> dict:
        """Predict future cash flow based on historical patterns."""
        from app.models.finance import Account, AccountType, JournalEntryLine, JournalEntry
        
        # Get cash accounts
        cash_accounts = (await self.db.execute(
            select(Account).where(
                Account.type == AccountType.ASSET,
                Account.subtype.in_(["cash", "bank"])
            )
        )).scalars().all()
        
        predictions = []
        for account in cash_accounts:
            # Get last 90 days of transactions
            ninety_days_ago = date.today() - timedelta(days=90)
            
            daily_flow = (await self.db.execute(
                select(
                    JournalEntry.entry_date,
                    func.sum(JournalEntryLine.debit - JournalEntryLine.credit).label("net_flow")
                )
                .join(JournalEntryLine, JournalEntryLine.journal_entry_id == JournalEntry.id)
                .where(
                    JournalEntryLine.account_id == account.id,
                    JournalEntry.entry_date >= ninety_days_ago,
                )
                .group_by(JournalEntry.entry_date)
                .order_by(JournalEntry.entry_date)
            )).all()
            
            if daily_flow:
                # Calculate average daily flow and trend
                flows = [float(row.net_flow) for row in daily_flow]
                avg_daily_flow = sum(flows) / len(flows) if flows else 0
                trend = self._calculate_trend(flows)
                
                # Project next 30 days
                projected_30_days = avg_daily_flow * 30 * (1 + trend)
                
                predictions.append({
                    "account_id": account.id,
                    "account_name": account.name,
                    "avg_daily_flow": round(avg_daily_flow, 2),
                    "trend": round(trend, 4),
                    "projected_30_days": round(projected_30_days, 2),
                })
        
        return {
            "type": "cashflow_prediction",
            "predictions": predictions,
            "total_projected_30_days": sum(p["projected_30_days"] for p in predictions),
        }
    
    async def finance_expense_anomaly_detection(self, user_id: int) -> dict:
        """Detect unusual expenses."""
        from app.models.finance import Account, AccountType, JournalEntryLine, JournalEntry
        
        # Get expense accounts
        expense_accounts = (await self.db.execute(
            select(Account).where(Account.type == AccountType.EXPENSE)
        )).scalars().all()
        
        anomalies = []
        for account in expense_accounts:
            # Get monthly totals for last 6 months
            six_months_ago = date.today() - timedelta(days=180)
            
            monthly_totals = (await self.db.execute(
                select(
                    func.date_trunc('month', JournalEntry.entry_date).label("month"),
                    func.sum(JournalEntryLine.debit).label("total")
                )
                .join(JournalEntryLine, JournalEntryLine.journal_entry_id == JournalEntry.id)
                .where(
                    JournalEntryLine.account_id == account.id,
                    JournalEntry.entry_date >= six_months_ago,
                )
                .group_by(func.date_trunc('month', JournalEntry.entry_date))
            )).all()
            
            if len(monthly_totals) >= 3:
                amounts = [float(row.total) for row in monthly_totals]
                avg_amount = sum(amounts) / len(amounts)
                std_dev = (sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
                
                # Check if latest month is anomalous (>2 std dev from mean)
                latest = amounts[-1]
                if abs(latest - avg_amount) > 2 * std_dev:
                    anomalies.append({
                        "account_id": account.id,
                        "account_name": account.name,
                        "latest_amount": latest,
                        "avg_amount": round(avg_amount, 2),
                        "deviation": round((latest - avg_amount) / std_dev, 2) if std_dev > 0 else 0,
                        "is_over": latest > avg_amount,
                    })
        
        return {
            "type": "expense_anomaly",
            "total_anomalies": len(anomalies),
            "anomalies": sorted(anomalies, key=lambda x: abs(x["deviation"]), reverse=True),
        }
    
    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend from a list of values."""
        if len(values) < 2:
            return 0.0
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope / y_mean if y_mean != 0 else 0.0
    
    # ══════════════════════════════════════════════════════════════════════════
    # HR AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def hr_attrition_prediction(self, user_id: int) -> dict:
        """Predict which employees might leave."""
        from app.models.hr import Employee, EmployeeStatus, AttendanceRecord, LeaveRequest
        
        # Get active employees
        employees = (await self.db.execute(
            select(Employee).where(Employee.status == EmployeeStatus.ACTIVE)
        )).scalars().all()
        
        predictions = []
        for emp in employees:
            risk_score = 0
            risk_factors = []
            
            # Check leave pattern (high sick leave usage)
            sick_leave_used = (await self.db.execute(
                select(func.count(LeaveRequest.id))
                .where(
                    LeaveRequest.employee_id == emp.id,
                    LeaveRequest.leave_type == "sick",
                    LeaveRequest.status == "approved",
                )
            )).scalar() or 0
            
            if sick_leave_used > 5:
                risk_score += 20
                risk_factors.append(f"High sick leave usage ({sick_leave_used} days)")
            
            # Check attendance pattern (frequent absences)
            recent_absences = (await self.db.execute(
                select(func.count(AttendanceRecord.id))
                .where(
                    AttendanceRecord.employee_id == emp.id,
                    AttendanceRecord.work_hours < 4,  # Half day or less
                )
            )).scalar() or 0
            
            if recent_absences > 3:
                risk_score += 15
                risk_factors.append(f"Recent absences ({recent_absences})")
            
            # Check tenure (new employees or employees near anniversary)
            if emp.join_date:
                years_of_service = (date.today() - emp.join_date).days / 365.25
                if years_of_service < 1:
                    risk_score += 10
                    risk_factors.append("New employee (< 1 year)")
                elif years_of_service % 1 < 0.1:  # Near anniversary
                    risk_score += 5
                    risk_factors.append("Approaching work anniversary")
            
            if risk_score > 0:
                predictions.append({
                    "employee_id": emp.id,
                    "employee_name": emp.full_name,
                    "department": emp.department_id,
                    "risk_score": min(risk_score, 100),
                    "risk_factors": risk_factors,
                })
        
        # Sort by risk score
        predictions.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return {
            "type": "attrition_prediction",
            "total_at_risk": len(predictions),
            "high_risk": [p for p in predictions if p["risk_score"] >= 50],
            "medium_risk": [p for p in predictions if 20 <= p["risk_score"] < 50],
        }
    
    # ══════════════════════════════════════════════════════════════════════════
    # SALES AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def sales_revenue_forecast(self, user_id: int) -> dict:
        """Forecast revenue for next quarter."""
        from app.models.sales import Invoice, InvoiceStatus
        
        # Get monthly revenue for last 12 months
        twelve_months_ago = date.today() - timedelta(days=365)
        
        monthly_revenue = (await self.db.execute(
            select(
                func.date_trunc('month', Invoice.invoice_date).label("month"),
                func.sum(Invoice.total_amount).label("revenue")
            )
            .where(
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PAID]),
                Invoice.invoice_date >= twelve_months_ago,
            )
            .group_by(func.date_trunc('month', Invoice.invoice_date))
            .order_by(func.date_trunc('month', Invoice.invoice_date))
        )).all()
        
        if not monthly_revenue:
            return {"type": "revenue_forecast", "forecast": [], "confidence": 0}
        
        revenues = [float(row.revenue) for row in monthly_revenue]
        avg_monthly = sum(revenues) / len(revenues)
        trend = self._calculate_trend(revenues)
        
        # Forecast next 3 months
        forecast = []
        for i in range(1, 4):
            projected = avg_monthly * (1 + trend * i)
            forecast.append({
                "month_offset": i,
                "projected_revenue": round(projected, 2),
            })
        
        return {
            "type": "revenue_forecast",
            "historical_avg_monthly": round(avg_monthly, 2),
            "trend": round(trend, 4),
            "forecast": forecast,
            "confidence": min(80, 50 + len(revenues) * 3),  # More data = higher confidence
        }
    
    async def sales_churn_prediction(self, user_id: int) -> dict:
        """Predict customers at risk of churning."""
        from app.models.sales import Customer, Invoice, InvoiceStatus
        from datetime import datetime
        
        # Get customers with no orders in last 90 days
        ninety_days_ago = date.today() - timedelta(days=90)
        
        active_customers = (await self.db.execute(
            select(Customer).where(Customer.is_active.is_(True))
        )).scalars().all()
        
        at_risk = []
        for customer in active_customers:
            # Check last order date
            last_order = (await self.db.execute(
                select(func.max(Invoice.invoice_date))
                .where(Invoice.customer_id == customer.id)
            )).scalar()
            
            if last_order:
                days_since_order = (date.today() - last_order).days
                if days_since_order > 90:
                    at_risk.append({
                        "customer_id": customer.id,
                        "customer_name": customer.name,
                        "last_order_date": last_order.isoformat(),
                        "days_inactive": days_since_order,
                        "risk_level": "high" if days_since_order > 180 else "medium",
                    })
            else:
                # Never ordered
                at_risk.append({
                    "customer_id": customer.id,
                    "customer_name": customer.name,
                    "last_order_date": None,
                    "days_inactive": None,
                    "risk_level": "high",
                    "note": "No orders on record",
                })
        
        return {
            "type": "churn_prediction",
            "total_customers": len(active_customers),
            "at_risk_count": len(at_risk),
            "at_risk_customers": sorted(at_risk, key=lambda x: x["risk_level"]),
        }
    
    # ══════════════════════════════════════════════════════════════════════════
    # CRM AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def crm_lead_scoring(self, lead_id: int) -> dict:
        """Score a lead based on multiple factors."""
        from app.models.crm import Lead, LeadStatus
        
        lead = await self.db.get(Lead, lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        score = 50  # Base score
        
        # Factor: Budget (higher = better)
        if lead.budget:
            if lead.budget > 100000000:  # > 100M IRR
                score += 20
            elif lead.budget > 10000000:  # > 10M IRR
                score += 10
        
        # Factor: Source quality
        high_quality_sources = ["referral", "website", "demo_request"]
        if lead.source in high_quality_sources:
            score += 15
        
        # Factor: Engagement (if we have interaction data)
        from app.models.crm import CustomerInteraction
        interaction_count = (await self.db.execute(
            select(func.count(CustomerInteraction.id))
            .where(CustomerInteraction.customer_id == lead.id)
        )).scalar() or 0
        
        if interaction_count > 5:
            score += 15
        elif interaction_count > 2:
            score += 10
        
        # Factor: Timeline urgency
        if lead.timeline:
            if "immediately" in lead.timeline.lower() or "asap" in lead.timeline.lower():
                score += 10
        
        return {
            "type": "lead_scoring",
            "lead_id": lead.id,
            "lead_name": lead.name,
            "score": min(score, 100),
            "factors": {
                "base_score": 50,
                "budget_factor": 20 if lead.budget and lead.budget > 100000000 else 10 if lead.budget and lead.budget > 10000000 else 0,
                "source_factor": 15 if lead.source in high_quality_sources else 0,
                "engagement_factor": 15 if interaction_count > 5 else 10 if interaction_count > 2 else 0,
                "urgency_factor": 10 if lead.timeline and ("immediately" in lead.timeline.lower() or "asap" in lead.timeline.lower()) else 0,
            }
        }
    
    # ══════════════════════════════════════════════════════════════════════════
    # PROCUREMENT AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def procurement_supplier_risk_analysis(self, user_id: int) -> dict:
        """Analyze supplier risk based on delivery performance."""
        from app.models.procurement import Vendor, PurchaseOrder
        
        vendors = (await self.db.execute(
            select(Vendor).where(Vendor.is_active.is_(True))
        )).scalars().all()
        
        risk_analysis = []
        for vendor in vendors:
            # Get delivery performance
            total_orders = (await self.db.execute(
                select(func.count(PurchaseOrder.id))
                .where(PurchaseOrder.vendor_id == vendor.id)
            )).scalar() or 0
            
            on_time_orders = (await self.db.execute(
                select(func.count(PurchaseOrder.id))
                .where(
                    PurchaseOrder.vendor_id == vendor.id,
                    PurchaseOrder.actual_delivery <= PurchaseOrder.expected_delivery,
                )
            )).scalar() or 0
            
            on_time_rate = (on_time_orders / total_orders * 100) if total_orders > 0 else 100
            
            # Calculate risk score (lower is better)
            risk_score = 100 - on_time_rate
            
            risk_analysis.append({
                "vendor_id": vendor.id,
                "vendor_name": vendor.name,
                "total_orders": total_orders,
                "on_time_rate": round(on_time_rate, 1),
                "risk_score": round(risk_score, 1),
                "risk_level": "high" if risk_score > 30 else "medium" if risk_score > 15 else "low",
            })
        
        return {
            "type": "supplier_risk",
            "total_vendors": len(vendors),
            "high_risk": [v for v in risk_analysis if v["risk_level"] == "high"],
            "medium_risk": [v for v in risk_analysis if v["risk_level"] == "medium"],
        }
    
    # ══════════════════════════════════════════════════════════════════════════
    # QUALITY AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def quality_defect_prediction(self, user_id: int) -> dict:
        """Predict potential defects based on historical patterns."""
        from app.models.quality import QualityInspection, QualityDefect, DefectSeverity
        
        # Get recent inspections
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_inspections = (await self.db.execute(
            select(QualityInspection)
            .where(QualityInspection.created_at >= thirty_days_ago)
        )).scalars().all()
        
        # Calculate defect rates by type
        defect_rates = {}
        for inspection in recent_inspections:
            if inspection.quantity_inspected > 0:
                defect_rate = inspection.quantity_failed / inspection.quantity_inspected * 100
                inspection_type = inspection.inspection_type or "general"
                
                if inspection_type not in defect_rates:
                    defect_rates[inspection_type] = []
                defect_rates[inspection_type].append(defect_rate)
        
        predictions = []
        for inspection_type, rates in defect_rates.items():
            avg_rate = sum(rates) / len(rates) if rates else 0
            trend = self._calculate_trend(rates) if len(rates) > 1 else 0
            
            if avg_rate > 5 or trend > 0.1:  # High defect rate or increasing trend
                predictions.append({
                    "inspection_type": inspection_type,
                    "avg_defect_rate": round(avg_rate, 2),
                    "trend": round(trend, 4),
                    "sample_size": len(rates),
                    "risk_level": "high" if avg_rate > 10 or trend > 0.2 else "medium",
                })
        
        return {
            "type": "defect_prediction",
            "total_types_analyzed": len(defect_rates),
            "at_risk_types": predictions,
        }
    
    # ══════════════════════════════════════════════════════════════════════════
    # HSE AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def hse_incident_prediction(self, user_id: int) -> dict:
        """Predict potential safety incidents."""
        from app.models.hse import HSEIncident, IncidentSeverity, IncidentStatus
        
        # Get recent incidents
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        
        recent_incidents = (await self.db.execute(
            select(HSEIncident)
            .where(HSEIncident.created_at >= ninety_days_ago)
        )).scalars().all()
        
        # Analyze by location and department
        location_stats = {}
        for incident in recent_incidents:
            location = incident.location or "Unknown"
            if location not in location_stats:
                location_stats[location] = {"count": 0, "severities": []}
            location_stats[location]["count"] += 1
            location_stats[location]["severities"].append(incident.severity.value)
        
        predictions = []
        for location, stats in location_stats.items():
            if stats["count"] >= 3:  # 3+ incidents in 90 days
                high_severity_count = stats["severities"].count("critical") + stats["severities"].count("high")
                predictions.append({
                    "location": location,
                    "incident_count_90d": stats["count"],
                    "high_severity_count": high_severity_count,
                    "risk_level": "high" if high_severity_count > 0 else "medium",
                })
        
        return {
            "type": "incident_prediction",
            "total_locations_analyzed": len(location_stats),
            "at_risk_locations": sorted(predictions, key=lambda x: x["incident_count_90d"], reverse=True),
        }
    
    async def hse_safety_score(self, user_id: int) -> dict:
        """Calculate overall safety score."""
        from app.models.hse import HSEIncident, IncidentStatus, HSEChecklist, ChecklistStatus
        
        # Get incident stats
        total_incidents = (await self.db.execute(
            select(func.count(HSEIncident.id))
        )).scalar() or 0
        
        resolved_incidents = (await self.db.execute(
            select(func.count(HSEIncident.id))
            .where(HSEIncident.status == IncidentStatus.RESOLVED)
        )).scalar() or 0
        
        # Get checklist stats
        total_checklists = (await self.db.execute(
            select(func.count(HSEChecklist.id))
        )).scalar() or 0
        
        passed_checklists = (await self.db.execute(
            select(func.count(HSEChecklist.id))
            .where(HSEChecklist.status == ChecklistStatus.PASSED)
        )).scalar() or 0
        
        # Calculate score (0-100)
        incident_score = (resolved_incidents / total_incidents * 50) if total_incidents > 0 else 50
        checklist_score = (passed_checklists / total_checklists * 50) if total_checklists > 0 else 50
        
        total_score = incident_score + checklist_score
        
        return {
            "type": "safety_score",
            "overall_score": round(total_score, 1),
            "incident_score": round(incident_score, 1),
            "checklist_score": round(checklist_score, 1),
            "total_incidents": total_incidents,
            "resolved_incidents": resolved_incidents,
            "total_checklists": total_checklists,
            "passed_checklists": passed_checklists,
        }
    
    # ══════════════════════════════════════════════════════════════════════════
    # PROJECTS AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def projects_risk_assessment(self, project_id: int) -> dict:
        """Assess project risks."""
        from app.models.projects import Project, ProjectRisk, RiskStatus
        
        project = await self.db.get(Project, project_id)
        if not project:
            return {"error": "Project not found"}
        
        # Get project risks
        risks = (await self.db.execute(
            select(ProjectRisk).where(ProjectRisk.project_id == project_id)
        )).scalars().all()
        
        # Calculate risk scores
        open_risks = [r for r in risks if r.status == RiskStatus.OPEN]
        total_risk_score = sum(float(r.probability) * float(r.impact) / 100 for r in open_risks)
        
        # Assess schedule risk
        if project.end_date:
            days_remaining = (project.end_date - date.today()).days
            schedule_risk = "high" if days_remaining < 30 and float(project.progress) < 70 else "low"
        else:
            schedule_risk = "unknown"
        
        # Assess budget risk
        if project.budget > 0:
            budget_utilization = float(project.actual_cost) / float(project.budget) * 100
            budget_risk = "high" if budget_utilization > 90 else "medium" if budget_utilization > 70 else "low"
        else:
            budget_risk = "unknown"
        
        return {
            "type": "project_risk_assessment",
            "project_id": project.id,
            "project_name": project.name,
            "overall_risk_score": round(total_risk_score, 2),
            "open_risks_count": len(open_risks),
            "schedule_risk": schedule_risk,
            "budget_risk": budget_risk,
            "risks": [
                {
                    "id": r.id,
                    "name": r.name,
                    "probability": float(r.probability),
                    "impact": float(r.impact),
                    "score": round(float(r.probability) * float(r.impact) / 100, 2),
                }
                for r in open_risks
            ],
        }
    
    # ══════════════════════════════════════════════════════════════════════════
    # SUPPORT AI
    # ══════════════════════════════════════════════════════════════════════════
    
    async def support_ticket_sentiment(self, ticket_id: int) -> dict:
        """Analyze ticket sentiment."""
        from app.models.support import Ticket, TicketComment
        
        ticket = await self.db.get(Ticket, ticket_id)
        if not ticket:
            return {"error": "Ticket not found"}
        
        # Get latest comment
        latest_comment = (await self.db.execute(
            select(TicketComment)
            .where(TicketComment.ticket_id == ticket_id)
            .order_by(TicketComment.created_at.desc())
            .limit(1)
        )).scalar_one_or_none()
        
        if not latest_comment:
            return {"type": "sentiment_analysis", "sentiment": "neutral", "confidence": 0}
        
        # Simple keyword-based sentiment (in production, use LLM)
        positive_words = ["thank", "great", "excellent", "resolved", "fixed", "helpful"]
        negative_words = ["angry", "terrible", "worst", "frustrated", "unacceptable", "delayed"]
        
        content = latest_comment.content.lower()
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(90, 50 + positive_count * 10)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(90, 50 + negative_count * 10)
        else:
            sentiment = "neutral"
            confidence = 50
        
        return {
            "type": "sentiment_analysis",
            "ticket_id": ticket.id,
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_signals": positive_count,
            "negative_signals": negative_count,
        }


# Singleton factory
def get_ai_module_integration(db: AsyncSession) -> AIModuleIntegration:
    return AIModuleIntegration(db)
