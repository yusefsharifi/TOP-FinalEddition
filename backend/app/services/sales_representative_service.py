from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.sales.models.sales_representative import (
    SalesRepresentative, SalesRegion, SalesVisit,
    SalesPerformance, SalesRepStatus, SalesRepLevel
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class SalesRepresentativeService:
    def __init__(self, db: Session):
        self.db = db

    def create_sales_rep(self, data: Dict[str, Any]) -> Optional[SalesRepresentative]:
        """ایجاد فروشنده جدید"""
        try:
            sales_rep = SalesRepresentative(**data)
            self.db.add(sales_rep)
            self.db.commit()
            self.db.refresh(sales_rep)
            return sales_rep
        except Exception as e:
            logger.error(f"Error creating sales representative: {str(e)}")
            self.db.rollback()
            return None

    def get_sales_rep(self, sales_rep_id: int) -> Optional[SalesRepresentative]:
        """دریافت اطلاعات فروشنده"""
        try:
            return self.db.query(SalesRepresentative).filter(
                SalesRepresentative.id == sales_rep_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting sales representative: {str(e)}")
            return None

    def update_sales_rep(self, sales_rep_id: int, data: Dict[str, Any]) -> Optional[SalesRepresentative]:
        """به‌روزرسانی اطلاعات فروشنده"""
        try:
            sales_rep = self.get_sales_rep(sales_rep_id)
            if sales_rep:
                for key, value in data.items():
                    setattr(sales_rep, key, value)
                self.db.commit()
                self.db.refresh(sales_rep)
            return sales_rep
        except Exception as e:
            logger.error(f"Error updating sales representative: {str(e)}")
            self.db.rollback()
            return None

    def create_region(self, data: Dict[str, Any]) -> Optional[SalesRegion]:
        """ایجاد منطقه فروش جدید"""
        try:
            region = SalesRegion(**data)
            self.db.add(region)
            self.db.commit()
            self.db.refresh(region)
            return region
        except Exception as e:
            logger.error(f"Error creating sales region: {str(e)}")
            self.db.rollback()
            return None

    def get_region(self, region_id: int) -> Optional[SalesRegion]:
        """دریافت اطلاعات منطقه فروش"""
        try:
            return self.db.query(SalesRegion).filter(
                SalesRegion.id == region_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting sales region: {str(e)}")
            return None

    def record_visit(self, data: Dict[str, Any]) -> Optional[SalesVisit]:
        """ثبت بازدید فروش"""
        try:
            visit = SalesVisit(**data)
            self.db.add(visit)
            self.db.commit()
            self.db.refresh(visit)
            return visit
        except Exception as e:
            logger.error(f"Error recording sales visit: {str(e)}")
            self.db.rollback()
            return None

    def get_visits(self, sales_rep_id: int, start_date: datetime, end_date: datetime) -> List[SalesVisit]:
        """دریافت لیست بازدیدهای فروشنده در بازه زمانی مشخص"""
        try:
            return self.db.query(SalesVisit).filter(
                SalesVisit.sales_rep_id == sales_rep_id,
                SalesVisit.visit_date.between(start_date, end_date)
            ).order_by(SalesVisit.visit_date.desc()).all()
        except Exception as e:
            logger.error(f"Error getting sales visits: {str(e)}")
            return []

    def record_performance(self, data: Dict[str, Any]) -> Optional[SalesPerformance]:
        """ثبت عملکرد فروش"""
        try:
            performance = SalesPerformance(**data)
            self.db.add(performance)
            self.db.commit()
            self.db.refresh(performance)
            return performance
        except Exception as e:
            logger.error(f"Error recording sales performance: {str(e)}")
            self.db.rollback()
            return None

    def get_performance(self, sales_rep_id: int, period_start: datetime, period_end: datetime) -> Optional[SalesPerformance]:
        """دریافت عملکرد فروشنده در بازه زمانی مشخص"""
        try:
            return self.db.query(SalesPerformance).filter(
                SalesPerformance.sales_rep_id == sales_rep_id,
                SalesPerformance.period_start == period_start,
                SalesPerformance.period_end == period_end
            ).first()
        except Exception as e:
            logger.error(f"Error getting sales performance: {str(e)}")
            return None

    def calculate_performance_metrics(self, sales_rep_id: int, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """محاسبه شاخص‌های عملکرد فروشنده"""
        try:
            # دریافت فروش‌های دوره
            sales = self.db.query(SalesPerformance).filter(
                SalesPerformance.sales_rep_id == sales_rep_id,
                SalesPerformance.period_start == period_start,
                SalesPerformance.period_end == period_end
            ).first()

            if not sales:
                return {}

            # محاسبه شاخص‌ها
            metrics = {
                "total_sales": sales.total_sales,
                "target_achievement": sales.target_achievement,
                "new_customers": sales.new_customers,
                "customer_retention": sales.customer_retention,
                "average_order_value": sales.average_order_value,
                "additional_metrics": sales.metrics
            }

            return metrics
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            return {}

    def get_team_performance(self, manager_id: int, period_start: datetime, period_end: datetime) -> List[Dict[str, Any]]:
        """دریافت عملکرد تیم فروش"""
        try:
            team_members = self.db.query(SalesRepresentative).filter(
                SalesRepresentative.manager_id == manager_id
            ).all()

            team_performance = []
            for member in team_members:
                performance = self.get_performance(member.id, period_start, period_end)
                if performance:
                    team_performance.append({
                        "sales_rep_id": member.id,
                        "name": member.user.name,
                        "performance": self.calculate_performance_metrics(member.id, period_start, period_end)
                    })

            return team_performance
        except Exception as e:
            logger.error(f"Error getting team performance: {str(e)}")
            return [] 