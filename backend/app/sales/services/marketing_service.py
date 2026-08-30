from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.sales.models.marketing import (
    MarketingCampaign, CampaignStatus, CampaignType,
    Discount, DiscountType, MarketerReward, MarketerRewardType,
    MarketerPerformance
)
from app.utils.logger import log_error

class MarketingService:
    def __init__(self, db: Session):
        self.db = db

    # مدیریت کمپین‌های بازاریابی
    def create_campaign(self, data: Dict) -> Optional[MarketingCampaign]:
        """ایجاد کمپین بازاریابی جدید"""
        try:
            campaign = MarketingCampaign(**data)
            self.db.add(campaign)
            self.db.commit()
            self.db.refresh(campaign)
            return campaign
        except Exception as e:
            log_error(f"خطا در ایجاد کمپین بازاریابی: {str(e)}")
            self.db.rollback()
            return None

    def update_campaign_status(self, campaign_id: int, status: CampaignStatus) -> Optional[MarketingCampaign]:
        """به‌روزرسانی وضعیت کمپین"""
        try:
            campaign = self.db.query(MarketingCampaign).filter(
                MarketingCampaign.id == campaign_id
            ).first()
            
            if campaign:
                campaign.status = status
                self.db.commit()
                self.db.refresh(campaign)
            return campaign
        except Exception as e:
            log_error(f"خطا در به‌روزرسانی وضعیت کمپین: {str(e)}")
            self.db.rollback()
            return None

    def get_campaign_metrics(self, campaign_id: int) -> Dict:
        """دریافت شاخص‌های عملکرد کمپین"""
        try:
            campaign = self.db.query(MarketingCampaign).filter(
                MarketingCampaign.id == campaign_id
            ).first()
            
            if not campaign:
                return {}
            
            return campaign.metrics or {}
        except Exception as e:
            log_error(f"خطا در دریافت شاخص‌های عملکرد کمپین: {str(e)}")
            return {}

    # مدیریت تخفیفات
    def create_discount(self, data: Dict) -> Optional[Discount]:
        """ایجاد تخفیف جدید"""
        try:
            discount = Discount(**data)
            self.db.add(discount)
            self.db.commit()
            self.db.refresh(discount)
            return discount
        except Exception as e:
            log_error(f"خطا در ایجاد تخفیف: {str(e)}")
            self.db.rollback()
            return None

    def apply_discount(self, discount_id: int, order_amount: float) -> Optional[float]:
        """اعمال تخفیف بر روی مبلغ سفارش"""
        try:
            discount = self.db.query(Discount).filter(
                Discount.id == discount_id,
                Discount.is_active == True,
                Discount.start_date <= datetime.utcnow(),
                (Discount.end_date.is_(None) | (Discount.end_date >= datetime.utcnow())),
                (Discount.usage_limit.is_(None) | (Discount.used_count < Discount.usage_limit))
            ).first()
            
            if not discount:
                return None

            # بررسی حداقل مبلغ خرید
            if discount.min_purchase_amount and order_amount < discount.min_purchase_amount:
                return None

            # محاسبه مقدار تخفیف
            if discount.discount_type == DiscountType.PERCENTAGE:
                discount_amount = order_amount * (discount.value / 100)
                if discount.max_discount_amount:
                    discount_amount = min(discount_amount, discount.max_discount_amount)
            else:  # FIXED
                discount_amount = discount.value

            # به‌روزرسانی تعداد استفاده
            discount.used_count += 1
            self.db.commit()

            return discount_amount
        except Exception as e:
            log_error(f"خطا در اعمال تخفیف: {str(e)}")
            return None

    # مدیریت پاداش‌های بازاریاب
    def create_marketer_reward(self, data: Dict) -> Optional[MarketerReward]:
        """ایجاد پاداش برای بازاریاب"""
        try:
            reward = MarketerReward(**data)
            self.db.add(reward)
            self.db.commit()
            self.db.refresh(reward)
            return reward
        except Exception as e:
            log_error(f"خطا در ایجاد پاداش بازاریاب: {str(e)}")
            self.db.rollback()
            return None

    def calculate_commission(self, marketer_id: int, sale_amount: float, commission_rate: float) -> float:
        """محاسبه کمیسیون فروش"""
        try:
            commission = sale_amount * (commission_rate / 100)
            
            # ثبت پاداش
            reward_data = {
                "marketer_id": marketer_id,
                "reward_type": MarketerRewardType.COMMISSION,
                "amount": commission,
                "description": f"کمیسیون فروش به مبلغ {sale_amount}",
                "status": "pending"
            }
            self.create_marketer_reward(reward_data)
            
            return commission
        except Exception as e:
            log_error(f"خطا در محاسبه کمیسیون: {str(e)}")
            return 0.0

    def record_new_customer_reward(self, marketer_id: int, customer_id: int, reward_amount: float) -> Optional[MarketerReward]:
        """ثبت پاداش جذب مشتری جدید"""
        try:
            reward_data = {
                "marketer_id": marketer_id,
                "reward_type": MarketerRewardType.NEW_CUSTOMER,
                "amount": reward_amount,
                "description": f"پاداش جذب مشتری جدید",
                "reference_id": customer_id,
                "status": "pending"
            }
            return self.create_marketer_reward(reward_data)
        except Exception as e:
            log_error(f"خطا در ثبت پاداش جذب مشتری جدید: {str(e)}")
            return None

    def update_marketer_performance(self, marketer_id: int, period_start: datetime, period_end: datetime) -> Optional[MarketerPerformance]:
        """به‌روزرسانی عملکرد بازاریاب"""
        try:
            # محاسبه شاخص‌های عملکرد
            total_sales = self._calculate_total_sales(marketer_id, period_start, period_end)
            total_commission = self._calculate_total_commission(marketer_id, period_start, period_end)
            new_customers = self._count_new_customers(marketer_id, period_start, period_end)
            retained_customers = self._count_retained_customers(marketer_id, period_start, period_end)
            special_product_sales = self._calculate_special_product_sales(marketer_id, period_start, period_end)
            target_achievement_rate = self._calculate_target_achievement_rate(marketer_id, period_start, period_end)

            # ایجاد یا به‌روزرسانی رکورد عملکرد
            performance = self.db.query(MarketerPerformance).filter(
                MarketerPerformance.marketer_id == marketer_id,
                MarketerPerformance.period_start == period_start,
                MarketerPerformance.period_end == period_end
            ).first()

            if performance:
                performance.total_sales = total_sales
                performance.total_commission = total_commission
                performance.new_customers = new_customers
                performance.retained_customers = retained_customers
                performance.special_product_sales = special_product_sales
                performance.target_achievement_rate = target_achievement_rate
            else:
                performance = MarketerPerformance(
                    marketer_id=marketer_id,
                    period_start=period_start,
                    period_end=period_end,
                    total_sales=total_sales,
                    total_commission=total_commission,
                    new_customers=new_customers,
                    retained_customers=retained_customers,
                    special_product_sales=special_product_sales,
                    target_achievement_rate=target_achievement_rate
                )
                self.db.add(performance)

            self.db.commit()
            self.db.refresh(performance)
            return performance
        except Exception as e:
            log_error(f"خطا در به‌روزرسانی عملکرد بازاریاب: {str(e)}")
            self.db.rollback()
            return None

    def _calculate_total_sales(self, marketer_id: int, period_start: datetime, period_end: datetime) -> float:
        """محاسبه کل فروش بازاریاب در دوره مشخص"""
        # TODO: پیاده‌سازی محاسبه کل فروش
        return 0.0

    def _calculate_total_commission(self, marketer_id: int, period_start: datetime, period_end: datetime) -> float:
        """محاسبه کل کمیسیون بازاریاب در دوره مشخص"""
        # TODO: پیاده‌سازی محاسبه کل کمیسیون
        return 0.0

    def _count_new_customers(self, marketer_id: int, period_start: datetime, period_end: datetime) -> int:
        """شمارش مشتریان جدید جذب شده توسط بازاریاب"""
        # TODO: پیاده‌سازی شمارش مشتریان جدید
        return 0

    def _count_retained_customers(self, marketer_id: int, period_start: datetime, period_end: datetime) -> int:
        """شمارش مشتریان حفظ شده توسط بازاریاب"""
        # TODO: پیاده‌سازی شمارش مشتریان حفظ شده
        return 0

    def _calculate_special_product_sales(self, marketer_id: int, period_start: datetime, period_end: datetime) -> float:
        """محاسبه فروش محصولات خاص توسط بازاریاب"""
        # TODO: پیاده‌سازی محاسبه فروش محصولات خاص
        return 0.0

    def _calculate_target_achievement_rate(self, marketer_id: int, period_start: datetime, period_end: datetime) -> float:
        """محاسبه نرخ دستیابی به اهداف"""
        # TODO: پیاده‌سازی محاسبه نرخ دستیابی به اهداف
        return 0.0 