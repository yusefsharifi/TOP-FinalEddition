import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.sales.models.order import (
    Order, OrderItem, OrderPayment, OrderShipment,
    OrderStatus, PaymentStatus
)
from app.sales.services.order_service import OrderService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class TestOrderService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی تست"""
        # ایجاد دیتابیس تست
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # ایجاد سرویس
        self.service = OrderService(self.session)
        
        # ایجاد داده‌های تست
        self._create_test_data()
    
    def tearDown(self):
        """پاکسازی تست"""
        self.session.close()
    
    def _create_test_data(self):
        """ایجاد داده‌های تست"""
        # ایجاد سفارش تست
        self.test_order = Order(
            order_number="ORD-001",
            customer_id=1,
            sales_rep_id=1,
            status=OrderStatus.DRAFT.value,
            payment_status=PaymentStatus.PENDING.value,
            subtotal=1000.0,
            tax_amount=90.0,
            shipping_amount=50.0,
            discount_amount=0.0,
            total_amount=1140.0,
            created_by=1
        )
        self.session.add(self.test_order)
        self.session.commit()
        
        # ایجاد آیتم سفارش تست
        self.test_order_item = OrderItem(
            order_id=self.test_order.id,
            product_id=1,
            product_name="محصول تست",
            product_code="PROD-001",
            unit_price=1000.0,
            quantity=1,
            total_amount=1000.0
        )
        self.session.add(self.test_order_item)
        self.session.commit()
    
    def test_create_order(self):
        """تست ایجاد سفارش"""
        data = {
            "order_number": "ORD-002",
            "customer_id": 2,
            "sales_rep_id": 2,
            "items": [
                {
                    "product_id": 2,
                    "product_name": "محصول تست 2",
                    "product_code": "PROD-002",
                    "unit_price": 2000.0,
                    "quantity": 2
                }
            ],
            "tax_rate": 9,
            "shipping_amount": 100.0,
            "discount_amount": 0.0,
            "created_by": 1
        }
        order = self.service.create_order(data)
        self.assertIsNotNone(order)
        self.assertEqual(order.order_number, "ORD-002")
        self.assertEqual(len(order.items), 1)
    
    def test_get_order(self):
        """تست دریافت سفارش"""
        order = self.service.get_order(self.test_order.id)
        self.assertIsNotNone(order)
        self.assertEqual(order.id, self.test_order.id)
    
    def test_update_order(self):
        """تست به‌روزرسانی سفارش"""
        data = {
            "notes": "یادداشت تست",
            "internal_notes": "یادداشت داخلی تست"
        }
        order = self.service.update_order(self.test_order.id, data)
        self.assertIsNotNone(order)
        self.assertEqual(order.notes, "یادداشت تست")
        self.assertEqual(order.internal_notes, "یادداشت داخلی تست")
    
    def test_update_order_status(self):
        """تست به‌روزرسانی وضعیت سفارش"""
        order = self.service.update_order_status(
            self.test_order.id, OrderStatus.CONFIRMED.value
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.status, OrderStatus.CONFIRMED.value)
    
    def test_create_order_payment(self):
        """تست ایجاد پرداخت سفارش"""
        data = {
            "order_id": self.test_order.id,
            "amount": 500.0,
            "payment_method": "cash",
            "payment_reference": "REF-001"
        }
        payment = self.service.create_order_payment(data)
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, 500.0)
        self.assertEqual(payment.payment_method, "cash")
    
    def test_get_order_payments(self):
        """تست دریافت پرداخت‌های سفارش"""
        # ابتدا یک پرداخت ایجاد می‌کنیم
        payment_data = {
            "order_id": self.test_order.id,
            "amount": 500.0,
            "payment_method": "cash",
            "payment_reference": "REF-001"
        }
        self.service.create_order_payment(payment_data)
        
        # سپس پرداخت‌ها را دریافت می‌کنیم
        payments = self.service.get_order_payments(self.test_order.id)
        self.assertIsNotNone(payments)
        self.assertIsInstance(payments, list)
        self.assertEqual(len(payments), 1)
    
    def test_create_order_shipment(self):
        """تست ایجاد ارسال سفارش"""
        data = {
            "order_id": self.test_order.id,
            "shipment_number": "SHIP-001",
            "shipping_method": "post",
            "tracking_number": "TRACK-001",
            "estimated_delivery": datetime.utcnow(),
            "shipping_address": {
                "address": "آدرس تست",
                "city": "شهر تست",
                "postal_code": "12345"
            }
        }
        shipment = self.service.create_order_shipment(data)
        self.assertIsNotNone(shipment)
        self.assertEqual(shipment.shipment_number, "SHIP-001")
        self.assertEqual(shipment.shipping_method, "post")
    
    def test_get_order_shipments(self):
        """تست دریافت ارسال‌های سفارش"""
        # ابتدا یک ارسال ایجاد می‌کنیم
        shipment_data = {
            "order_id": self.test_order.id,
            "shipment_number": "SHIP-001",
            "shipping_method": "post",
            "tracking_number": "TRACK-001",
            "estimated_delivery": datetime.utcnow(),
            "shipping_address": {
                "address": "آدرس تست",
                "city": "شهر تست",
                "postal_code": "12345"
            }
        }
        self.service.create_order_shipment(shipment_data)
        
        # سپس ارسال‌ها را دریافت می‌کنیم
        shipments = self.service.get_order_shipments(self.test_order.id)
        self.assertIsNotNone(shipments)
        self.assertIsInstance(shipments, list)
        self.assertEqual(len(shipments), 1)
    
    def test_search_orders(self):
        """تست جستجوی سفارشات"""
        orders = self.service.search_orders("ORD-001")
        self.assertIsNotNone(orders)
        self.assertIsInstance(orders, list)
        self.assertEqual(len(orders), 1)
    
    def test_get_customer_orders(self):
        """تست دریافت سفارشات مشتری"""
        orders = self.service.get_customer_orders(1)
        self.assertIsNotNone(orders)
        self.assertIsInstance(orders, list)
        self.assertEqual(len(orders), 1)
    
    def test_get_sales_rep_orders(self):
        """تست دریافت سفارشات نماینده فروش"""
        orders = self.service.get_sales_rep_orders(1)
        self.assertIsNotNone(orders)
        self.assertIsInstance(orders, list)
        self.assertEqual(len(orders), 1)
    
    def test_get_order_statistics(self):
        """تست دریافت آمار سفارش"""
        statistics = self.service.get_order_statistics(self.test_order.id)
        self.assertIsNotNone(statistics)
        self.assertIsInstance(statistics, dict)
        self.assertEqual(statistics["total_amount"], 1140.0)
        self.assertEqual(statistics["payment_status"], PaymentStatus.PENDING.value)
        self.assertEqual(statistics["order_status"], OrderStatus.DRAFT.value)

if __name__ == '__main__':
    unittest.main() 