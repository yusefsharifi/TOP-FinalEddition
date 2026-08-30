from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.sales.models.subscription import (
    Subscription, SubscriptionItem, SubscriptionDelivery,
    SubscriptionDeliveryItem, SubscriptionPayment,
    SubscriptionStatus, SubscriptionType
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def create_subscription(self, data: Dict[str, Any]) -> Optional[Subscription]:
        """ایجاد اشتراک جدید"""
        try:
            subscription = Subscription(**data)
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            return subscription
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            self.db.rollback()
            return None

    def get_subscription(self, subscription_id: int) -> Optional[Subscription]:
        """دریافت اطلاعات اشتراک"""
        try:
            return self.db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting subscription: {str(e)}")
            return None

    def update_subscription_status(self, subscription_id: int, status: str) -> Optional[Subscription]:
        """به‌روزرسانی وضعیت اشتراک"""
        try:
            subscription = self.get_subscription(subscription_id)
            if not subscription:
                return None

            subscription.status = status
            self.db.commit()
            self.db.refresh(subscription)
            return subscription
        except Exception as e:
            logger.error(f"Error updating subscription status: {str(e)}")
            self.db.rollback()
            return None

    def add_subscription_item(self, data: Dict[str, Any]) -> Optional[SubscriptionItem]:
        """افزودن آیتم به اشتراک"""
        try:
            item = SubscriptionItem(**data)
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            logger.error(f"Error adding subscription item: {str(e)}")
            self.db.rollback()
            return None

    def create_subscription_delivery(self, data: Dict[str, Any]) -> Optional[SubscriptionDelivery]:
        """ایجاد تحویل اشتراک"""
        try:
            delivery = SubscriptionDelivery(**data)
            self.db.add(delivery)
            self.db.commit()
            self.db.refresh(delivery)
            return delivery
        except Exception as e:
            logger.error(f"Error creating subscription delivery: {str(e)}")
            self.db.rollback()
            return None

    def add_delivery_item(self, data: Dict[str, Any]) -> Optional[SubscriptionDeliveryItem]:
        """افزودن آیتم به تحویل اشتراک"""
        try:
            delivery_item = SubscriptionDeliveryItem(**data)
            self.db.add(delivery_item)
            self.db.commit()
            self.db.refresh(delivery_item)
            return delivery_item
        except Exception as e:
            logger.error(f"Error adding delivery item: {str(e)}")
            self.db.rollback()
            return None

    def create_subscription_payment(self, data: Dict[str, Any]) -> Optional[SubscriptionPayment]:
        """ثبت پرداخت اشتراک"""
        try:
            payment = SubscriptionPayment(**data)
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            return payment
        except Exception as e:
            logger.error(f"Error creating subscription payment: {str(e)}")
            self.db.rollback()
            return None

    def calculate_subscription_totals(self, subscription_id: int) -> Optional[Dict[str, float]]:
        """محاسبه مجموع اشتراک"""
        try:
            subscription = self.get_subscription(subscription_id)
            if not subscription:
                return None

            total_amount = sum(item.total_amount for item in subscription.items)
            discount_amount = sum(item.discount_amount for item in subscription.items)
            tax_amount = sum(item.tax_amount for item in subscription.items)
            final_amount = total_amount - discount_amount + tax_amount + subscription.shipping_amount

            return {
                "total_amount": total_amount,
                "discount_amount": discount_amount,
                "tax_amount": tax_amount,
                "shipping_amount": subscription.shipping_amount,
                "final_amount": final_amount
            }
        except Exception as e:
            logger.error(f"Error calculating subscription totals: {str(e)}")
            return None

    def get_subscription_history(self, subscription_id: int) -> List[Dict[str, Any]]:
        """دریافت تاریخچه اشتراک"""
        try:
            subscription = self.get_subscription(subscription_id)
            if not subscription:
                return []

            history = []
            
            # اضافه کردن تغییرات وضعیت
            history.append({
                "date": subscription.created_at,
                "action": "create",
                "details": "ایجاد اشتراک"
            })

            # اضافه کردن تحویل‌ها
            for delivery in subscription.deliveries:
                history.append({
                    "date": delivery.scheduled_date,
                    "action": "delivery",
                    "details": f"تحویل اشتراک - شماره: {delivery.delivery_number}"
                })

            # اضافه کردن پرداخت‌ها
            for payment in subscription.payments:
                history.append({
                    "date": payment.payment_date,
                    "action": "payment",
                    "details": f"پرداخت {payment.amount} تومان"
                })

            return sorted(history, key=lambda x: x["date"])
        except Exception as e:
            logger.error(f"Error getting subscription history: {str(e)}")
            return []

    def get_customer_subscriptions(self, customer_id: int, status: Optional[str] = None) -> List[Subscription]:
        """دریافت اشتراک‌های مشتری"""
        try:
            query = self.db.query(Subscription).filter(Subscription.customer_id == customer_id)
            if status:
                query = query.filter(Subscription.status == status)
            return query.order_by(Subscription.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting customer subscriptions: {str(e)}")
            return []

    def get_sales_rep_subscriptions(self, sales_rep_id: int, status: Optional[str] = None) -> List[Subscription]:
        """دریافت اشتراک‌های نماینده فروش"""
        try:
            query = self.db.query(Subscription).filter(Subscription.sales_rep_id == sales_rep_id)
            if status:
                query = query.filter(Subscription.status == status)
            return query.order_by(Subscription.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting sales rep subscriptions: {str(e)}")
            return []

    def get_upcoming_deliveries(self, days: int = 7) -> List[SubscriptionDelivery]:
        """دریافت تحویل‌های پیش‌رو"""
        try:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=days)
            return self.db.query(SubscriptionDelivery).filter(
                SubscriptionDelivery.scheduled_date.between(start_date, end_date),
                SubscriptionDelivery.status == "pending"
            ).order_by(SubscriptionDelivery.scheduled_date).all()
        except Exception as e:
            logger.error(f"Error getting upcoming deliveries: {str(e)}")
            return []

    def process_subscription_delivery(self, delivery_id: int) -> Optional[SubscriptionDelivery]:
        """پردازش تحویل اشتراک"""
        try:
            delivery = self.db.query(SubscriptionDelivery).filter(
                SubscriptionDelivery.id == delivery_id
            ).first()
            if not delivery:
                return None

            # به‌روزرسانی تاریخ تحویل واقعی
            delivery.actual_delivery_date = datetime.utcnow()
            delivery.status = "completed"

            # محاسبه تاریخ تحویل بعدی
            subscription = delivery.subscription
            if subscription.delivery_interval:
                interval_parts = subscription.delivery_interval.split()
                if len(interval_parts) == 2:
                    amount = int(interval_parts[0])
                    unit = interval_parts[1].lower()
                    if unit == "month":
                        next_date = delivery.scheduled_date + timedelta(days=30 * amount)
                    elif unit == "week":
                        next_date = delivery.scheduled_date + timedelta(weeks=amount)
                    elif unit == "year":
                        next_date = delivery.scheduled_date + timedelta(days=365 * amount)
                    else:
                        next_date = delivery.scheduled_date + timedelta(days=amount)
                    subscription.next_delivery_date = next_date

            self.db.commit()
            self.db.refresh(delivery)
            return delivery
        except Exception as e:
            logger.error(f"Error processing subscription delivery: {str(e)}")
            self.db.rollback()
            return None 