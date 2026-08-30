from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.crm.models.advanced_loyalty import (
    PointMultiplier, SpecialDay, PointRule, CustomerBehavior,
    PointMultiplierType
)
from app.crm.models.loyalty import CustomerMembership, PointTransaction, PointTransactionType
from app.utils.logger import log_error

class AdvancedLoyaltyService:
    def __init__(self, db: Session):
        self.db = db

    def create_point_multiplier(self, data: Dict) -> Optional[PointMultiplier]:
        """ایجاد ضریب امتیازدهی جدید"""
        try:
            multiplier = PointMultiplier(**data)
            self.db.add(multiplier)
            self.db.commit()
            self.db.refresh(multiplier)
            return multiplier
        except Exception as e:
            log_error(f"خطا در ایجاد ضریب امتیازدهی: {str(e)}")
            self.db.rollback()
            return None

    def get_active_multipliers(self, customer_id: int) -> List[PointMultiplier]:
        """دریافت ضریب‌های فعال برای مشتری"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.customer_id == customer_id
            ).first()
            
            if not membership:
                return []

            multipliers = self.db.query(PointMultiplier).filter(
                PointMultiplier.is_active == True,
                PointMultiplier.start_date <= datetime.utcnow(),
                (PointMultiplier.end_date.is_(None) | (PointMultiplier.end_date >= datetime.utcnow())),
                (PointMultiplier.tier == membership.tier) | (PointMultiplier.tier.is_(None))
            ).all()

            return multipliers
        except Exception as e:
            log_error(f"خطا در دریافت ضریب‌های فعال: {str(e)}")
            return []

    def create_special_day(self, data: Dict) -> Optional[SpecialDay]:
        """ایجاد روز خاص برای امتیازدهی مضاعف"""
        try:
            special_day = SpecialDay(**data)
            self.db.add(special_day)
            self.db.commit()
            self.db.refresh(special_day)
            return special_day
        except Exception as e:
            log_error(f"خطا در ایجاد روز خاص: {str(e)}")
            self.db.rollback()
            return None

    def get_special_day_multiplier(self, date: date) -> Optional[float]:
        """دریافت ضریب امتیازدهی برای یک روز خاص"""
        try:
            special_day = self.db.query(SpecialDay).filter(
                SpecialDay.date == date,
                SpecialDay.is_active == True
            ).first()
            
            return special_day.point_multiplier if special_day else None
        except Exception as e:
            log_error(f"خطا در دریافت ضریب روز خاص: {str(e)}")
            return None

    def create_point_rule(self, data: Dict) -> Optional[PointRule]:
        """ایجاد قانون امتیازدهی هوشمند"""
        try:
            rule = PointRule(**data)
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            return rule
        except Exception as e:
            log_error(f"خطا در ایجاد قانون امتیازدهی: {str(e)}")
            self.db.rollback()
            return None

    def apply_point_rules(self, customer_id: int, behavior_type: str, behavior_value: Dict) -> List[PointTransaction]:
        """اعمال قوانین امتیازدهی هوشمند"""
        try:
            transactions = []
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.customer_id == customer_id
            ).first()
            
            if not membership:
                return transactions

            # به‌روزرسانی رفتار مشتری
            behavior = self.db.query(CustomerBehavior).filter(
                CustomerBehavior.customer_id == customer_id,
                CustomerBehavior.behavior_type == behavior_type
            ).first()

            if behavior:
                behavior.behavior_value = behavior_value
                behavior.last_updated = datetime.utcnow()
            else:
                behavior = CustomerBehavior(
                    customer_id=customer_id,
                    behavior_type=behavior_type,
                    behavior_value=behavior_value
                )
                self.db.add(behavior)

            # بررسی قوانین فعال
            rules = self.db.query(PointRule).filter(
                PointRule.is_active == True,
                PointRule.start_date <= datetime.utcnow(),
                (PointRule.end_date.is_(None) | (PointRule.end_date >= datetime.utcnow())),
                PointRule.condition_type == behavior_type
            ).all()

            for rule in rules:
                if self._check_rule_condition(rule, behavior_value):
                    transaction = PointTransaction(
                        membership_id=membership.id,
                        transaction_type=PointTransactionType.EARN,
                        points=rule.points,
                        description=f"امتیاز هوشمند برای {rule.name}",
                        metadata={"rule_id": rule.id}
                    )
                    transactions.append(transaction)
                    membership.points_balance += rule.points
                    membership.total_points_earned += rule.points

            self.db.commit()
            return transactions
        except Exception as e:
            log_error(f"خطا در اعمال قوانین امتیازدهی: {str(e)}")
            self.db.rollback()
            return []

    def _check_rule_condition(self, rule: PointRule, behavior_value: Dict) -> bool:
        """بررسی شرط قانون امتیازدهی"""
        try:
            condition_value = rule.condition_value
            if rule.condition_type == "purchase_amount":
                return behavior_value.get("amount", 0) >= condition_value.get("min_amount", 0)
            elif rule.condition_type == "visit_count":
                return behavior_value.get("count", 0) >= condition_value.get("min_visits", 0)
            # اضافه کردن شرط‌های دیگر در اینجا
            return False
        except Exception as e:
            log_error(f"خطا در بررسی شرط قانون: {str(e)}")
            return False

    def calculate_points_with_multipliers(self, base_points: int, customer_id: int) -> int:
        """محاسبه امتیاز با اعمال ضریب‌ها"""
        try:
            multipliers = self.get_active_multipliers(customer_id)
            total_multiplier = 1.0

            for multiplier in multipliers:
                if multiplier.multiplier_type == PointMultiplierType.TIER:
                    total_multiplier *= multiplier.multiplier_value
                elif multiplier.multiplier_type == PointMultiplierType.SPECIAL_DAY:
                    if self.get_special_day_multiplier(date.today()):
                        total_multiplier *= multiplier.multiplier_value

            return int(base_points * total_multiplier)
        except Exception as e:
            log_error(f"خطا در محاسبه امتیاز با ضریب: {str(e)}")
            return base_points 