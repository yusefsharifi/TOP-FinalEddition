import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.sales.models.subscription import (
    Subscription, SubscriptionItem, SubscriptionDelivery,
    SubscriptionDeliveryItem, SubscriptionPayment
)
from app.sales.services.subscription_service import SubscriptionService
from app.utils.logging import log_error

class TestSubscriptionService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی تست"""
        # ایجاد دیتابیس تست
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # ایجاد سرویس
        self.service = SubscriptionService(self.session)
        
        # ایجاد داده‌های تست
        self._create_test_data()
    
    def tearDown(self):
        """پاکسازی تست"""
        self.session.close()
    
    def _create_test_data(self):
        """ایجاد داده‌های تست"""
        # ایجاد اشتراک تست
        self.test_subscription = Subscription(
            subscription_number="SUB-001",
            customer_id=1,
            sales_rep_id=1,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            next_delivery_date=datetime.now() + timedelta(days=7),
            status="active",
            type="monthly",
            total_amount=1000.0,
            discount_amount=100.0,
            tax_amount=90.0,
            final_amount=990.0
        )
        self.session.add(self.test_subscription)
        self.session.commit()
        
        # ایجاد آیتم اشتراک تست
        self.test_subscription_item = SubscriptionItem(
            subscription_id=self.test_subscription.id,
            product_id=1,
            quantity=2,
            unit_price=500.0,
            total_amount=1000.0
        )
        self.session.add(self.test_subscription_item)
        self.session.commit()
    
    def test_create_subscription(self):
        """تست ایجاد اشتراک"""
        data = {
            "subscription_number": "SUB-002",
            "customer_id": 2,
            "sales_rep_id": 2,
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=30),
            "next_delivery_date": datetime.now() + timedelta(days=7),
            "status": "active",
            "type": "monthly",
            "total_amount": 2000.0,
            "discount_amount": 200.0,
            "tax_amount": 180.0,
            "final_amount": 1980.0
        }
        subscription = self.service.create_subscription(data)
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.subscription_number, "SUB-002")
    
    def test_get_subscription(self):
        """تست دریافت اشتراک"""
        subscription = self.service.get_subscription(self.test_subscription.id)
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.id, self.test_subscription.id)
    
    def test_update_subscription_status(self):
        """تست به‌روزرسانی وضعیت اشتراک"""
        subscription = self.service.update_subscription_status(
            self.test_subscription.id, "cancelled"
        )
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.status, "cancelled")
    
    def test_add_subscription_item(self):
        """تست افزودن آیتم به اشتراک"""
        data = {
            "subscription_id": self.test_subscription.id,
            "product_id": 2,
            "quantity": 3,
            "unit_price": 300.0,
            "total_amount": 900.0
        }
        item = self.service.add_subscription_item(data)
        self.assertIsNotNone(item)
        self.assertEqual(item.product_id, 2)
    
    def test_create_subscription_delivery(self):
        """تست ایجاد تحویل اشتراک"""
        data = {
            "subscription_id": self.test_subscription.id,
            "delivery_number": "DEL-001",
            "scheduled_date": datetime.now() + timedelta(days=7),
            "status": "scheduled",
            "total_amount": 1000.0
        }
        delivery = self.service.create_subscription_delivery(data)
        self.assertIsNotNone(delivery)
        self.assertEqual(delivery.delivery_number, "DEL-001")
    
    def test_add_delivery_item(self):
        """تست افزودن آیتم به تحویل اشتراک"""
        # ابتدا یک تحویل ایجاد می‌کنیم
        delivery_data = {
            "subscription_id": self.test_subscription.id,
            "delivery_number": "DEL-001",
            "scheduled_date": datetime.now() + timedelta(days=7),
            "status": "scheduled",
            "total_amount": 1000.0
        }
        delivery = self.service.create_subscription_delivery(delivery_data)
        
        # سپس آیتم تحویل را اضافه می‌کنیم
        data = {
            "delivery_id": delivery.id,
            "subscription_item_id": self.test_subscription_item.id,
            "quantity": 2,
            "unit_price": 500.0,
            "total_amount": 1000.0
        }
        delivery_item = self.service.add_delivery_item(data)
        self.assertIsNotNone(delivery_item)
        self.assertEqual(delivery_item.quantity, 2)
    
    def test_create_subscription_payment(self):
        """تست ثبت پرداخت اشتراک"""
        data = {
            "subscription_id": self.test_subscription.id,
            "payment_number": "PAY-001",
            "amount": 990.0,
            "payment_date": datetime.now(),
            "payment_method": "credit_card",
            "status": "completed"
        }
        payment = self.service.create_subscription_payment(data)
        self.assertIsNotNone(payment)
        self.assertEqual(payment.payment_number, "PAY-001")
    
    def test_calculate_subscription_totals(self):
        """تست محاسبه مجموع اشتراک"""
        totals = self.service.calculate_subscription_totals(self.test_subscription.id)
        self.assertIsNotNone(totals)
        self.assertEqual(totals["total_amount"], 1000.0)
    
    def test_get_subscription_history(self):
        """تست دریافت تاریخچه اشتراک"""
        history = self.service.get_subscription_history(self.test_subscription.id)
        self.assertIsNotNone(history)
        self.assertIsInstance(history, list)
    
    def test_get_customer_subscriptions(self):
        """تست دریافت اشتراک‌های مشتری"""
        subscriptions = self.service.get_customer_subscriptions(1)
        self.assertIsNotNone(subscriptions)
        self.assertIsInstance(subscriptions, list)
    
    def test_get_sales_rep_subscriptions(self):
        """تست دریافت اشتراک‌های نماینده فروش"""
        subscriptions = self.service.get_sales_rep_subscriptions(1)
        self.assertIsNotNone(subscriptions)
        self.assertIsInstance(subscriptions, list)
    
    def test_get_upcoming_deliveries(self):
        """تست دریافت تحویل‌های پیش‌رو"""
        deliveries = self.service.get_upcoming_deliveries(7)
        self.assertIsNotNone(deliveries)
        self.assertIsInstance(deliveries, list)
    
    def test_process_subscription_delivery(self):
        """تست پردازش تحویل اشتراک"""
        # ابتدا یک تحویل ایجاد می‌کنیم
        delivery_data = {
            "subscription_id": self.test_subscription.id,
            "delivery_number": "DEL-001",
            "scheduled_date": datetime.now() + timedelta(days=7),
            "status": "scheduled",
            "total_amount": 1000.0
        }
        delivery = self.service.create_subscription_delivery(delivery_data)
        
        # سپس تحویل را پردازش می‌کنیم
        processed_delivery = self.service.process_subscription_delivery(delivery.id)
        self.assertIsNotNone(processed_delivery)
        self.assertEqual(processed_delivery.status, "completed") 