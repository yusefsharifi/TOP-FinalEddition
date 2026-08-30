from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.sales.models.pricing import (
    PricingRule, PriceAdjustment, DynamicPricing,
    PriceHistory, VolumeDiscount, PricingType, PricingRuleType
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class PricingService:
    def __init__(self, db: Session):
        self.db = db

    def create_pricing_rule(self, data: Dict[str, Any]) -> Optional[PricingRule]:
        """ایجاد قانون قیمت‌گذاری جدید"""
        try:
            rule = PricingRule(**data)
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            return rule
        except Exception as e:
            logger.error(f"Error creating pricing rule: {str(e)}")
            self.db.rollback()
            return None

    def get_pricing_rule(self, rule_id: int) -> Optional[PricingRule]:
        """دریافت اطلاعات قانون قیمت‌گذاری"""
        try:
            return self.db.query(PricingRule).filter(
                PricingRule.id == rule_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting pricing rule: {str(e)}")
            return None

    def create_price_adjustment(self, data: Dict[str, Any]) -> Optional[PriceAdjustment]:
        """ایجاد تنظیم قیمت جدید"""
        try:
            adjustment = PriceAdjustment(**data)
            self.db.add(adjustment)
            self.db.commit()
            self.db.refresh(adjustment)
            return adjustment
        except Exception as e:
            logger.error(f"Error creating price adjustment: {str(e)}")
            self.db.rollback()
            return None

    def get_price_adjustments(self, rule_id: int) -> List[PriceAdjustment]:
        """دریافت تنظیمات قیمت یک قانون"""
        try:
            return self.db.query(PriceAdjustment).filter(
                PriceAdjustment.pricing_rule_id == rule_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting price adjustments: {str(e)}")
            return []

    def create_dynamic_pricing(self, data: Dict[str, Any]) -> Optional[DynamicPricing]:
        """ایجاد قیمت‌گذاری پویا جدید"""
        try:
            dynamic_pricing = DynamicPricing(**data)
            self.db.add(dynamic_pricing)
            self.db.commit()
            self.db.refresh(dynamic_pricing)
            return dynamic_pricing
        except Exception as e:
            logger.error(f"Error creating dynamic pricing: {str(e)}")
            self.db.rollback()
            return None

    def update_dynamic_price(self, dynamic_pricing_id: int, new_price: float, reason: str) -> Optional[PriceHistory]:
        """به‌روزرسانی قیمت پویا و ثبت در تاریخچه"""
        try:
            dynamic_pricing = self.db.query(DynamicPricing).filter(
                DynamicPricing.id == dynamic_pricing_id
            ).first()

            if not dynamic_pricing:
                return None

            # بررسی محدودیت‌های قیمت
            if dynamic_pricing.min_price and new_price < dynamic_pricing.min_price:
                new_price = dynamic_pricing.min_price
            if dynamic_pricing.max_price and new_price > dynamic_pricing.max_price:
                new_price = dynamic_pricing.max_price

            # ثبت در تاریخچه
            price_history = PriceHistory(
                dynamic_pricing_id=dynamic_pricing_id,
                price=new_price,
                effective_date=datetime.utcnow(),
                reason=reason
            )
            self.db.add(price_history)
            self.db.commit()
            self.db.refresh(price_history)
            return price_history
        except Exception as e:
            logger.error(f"Error updating dynamic price: {str(e)}")
            self.db.rollback()
            return None

    def get_price_history(self, dynamic_pricing_id: int, start_date: datetime, end_date: datetime) -> List[PriceHistory]:
        """دریافت تاریخچه قیمت"""
        try:
            return self.db.query(PriceHistory).filter(
                PriceHistory.dynamic_pricing_id == dynamic_pricing_id,
                PriceHistory.effective_date.between(start_date, end_date)
            ).order_by(PriceHistory.effective_date.desc()).all()
        except Exception as e:
            logger.error(f"Error getting price history: {str(e)}")
            return []

    def create_volume_discount(self, data: Dict[str, Any]) -> Optional[VolumeDiscount]:
        """ایجاد تخفیف حجمی جدید"""
        try:
            discount = VolumeDiscount(**data)
            self.db.add(discount)
            self.db.commit()
            self.db.refresh(discount)
            return discount
        except Exception as e:
            logger.error(f"Error creating volume discount: {str(e)}")
            self.db.rollback()
            return None

    def calculate_final_price(self, product_id: int, quantity: int, customer_segment_id: Optional[int] = None) -> float:
        """محاسبه قیمت نهایی با اعمال تمام قوانین و تخفیف‌ها"""
        try:
            # دریافت قیمت پایه
            dynamic_pricing = self.db.query(DynamicPricing).filter(
                DynamicPricing.product_id == product_id,
                DynamicPricing.is_active == True
            ).first()

            if not dynamic_pricing:
                return 0.0

            base_price = dynamic_pricing.base_price

            # اعمال قوانین قیمت‌گذاری
            rules = self.db.query(PricingRule).filter(
                PricingRule.is_active == True,
                PricingRule.start_date <= datetime.utcnow(),
                PricingRule.end_date >= datetime.utcnow()
            ).order_by(PricingRule.priority.desc()).all()

            for rule in rules:
                adjustments = self.get_price_adjustments(rule.id)
                for adjustment in adjustments:
                    if (adjustment.product_id == product_id or 
                        (adjustment.customer_segment_id == customer_segment_id and customer_segment_id)):
                        if adjustment.adjustment_type == "percentage":
                            base_price *= (1 + adjustment.adjustment_value / 100)
                        else:
                            base_price += adjustment.adjustment_value

            # اعمال تخفیف حجمی
            volume_discounts = self.db.query(VolumeDiscount).filter(
                VolumeDiscount.product_id == product_id,
                VolumeDiscount.is_active == True,
                VolumeDiscount.min_quantity <= quantity
            ).order_by(VolumeDiscount.min_quantity.desc()).all()

            for discount in volume_discounts:
                if not discount.max_quantity or quantity <= discount.max_quantity:
                    if discount.discount_type == "percentage":
                        base_price *= (1 - discount.discount_value / 100)
                    else:
                        base_price -= discount.discount_value
                    break

            return base_price
        except Exception as e:
            logger.error(f"Error calculating final price: {str(e)}")
            return 0.0

    def get_active_discounts(self, product_id: int, quantity: int) -> List[VolumeDiscount]:
        """دریافت تخفیف‌های فعال برای یک محصول"""
        try:
            return self.db.query(VolumeDiscount).filter(
                VolumeDiscount.product_id == product_id,
                VolumeDiscount.is_active == True,
                VolumeDiscount.min_quantity <= quantity
            ).order_by(VolumeDiscount.min_quantity.desc()).all()
        except Exception as e:
            logger.error(f"Error getting active discounts: {str(e)}")
            return [] 