from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.sales.models.order import (
    Order, OrderItem, OrderPayment, OrderShipment,
    OrderReturn, OrderItemReturn, OrderStatus, OrderType
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, data: Dict[str, Any]) -> Optional[Order]:
        """ایجاد سفارش جدید"""
        try:
            order = Order(**data)
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            return order
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            self.db.rollback()
            return None

    def get_order(self, order_id: int) -> Optional[Order]:
        """دریافت اطلاعات سفارش"""
        try:
            return self.db.query(Order).filter(
                Order.id == order_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting order: {str(e)}")
            return None

    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """به‌روزرسانی وضعیت سفارش"""
        try:
            order = self.get_order(order_id)
            if not order:
                return None

            order.status = status
            self.db.commit()
            self.db.refresh(order)
            return order
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            self.db.rollback()
            return None

    def add_order_item(self, data: Dict[str, Any]) -> Optional[OrderItem]:
        """افزودن آیتم به سفارش"""
        try:
            item = OrderItem(**data)
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            logger.error(f"Error adding order item: {str(e)}")
            self.db.rollback()
            return None

    def create_order_payment(self, data: Dict[str, Any]) -> Optional[OrderPayment]:
        """ثبت پرداخت سفارش"""
        try:
            payment = OrderPayment(**data)
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            return payment
        except Exception as e:
            logger.error(f"Error creating order payment: {str(e)}")
            self.db.rollback()
            return None

    def create_order_shipment(self, data: Dict[str, Any]) -> Optional[OrderShipment]:
        """ثبت ارسال سفارش"""
        try:
            shipment = OrderShipment(**data)
            self.db.add(shipment)
            self.db.commit()
            self.db.refresh(shipment)
            return shipment
        except Exception as e:
            logger.error(f"Error creating order shipment: {str(e)}")
            self.db.rollback()
            return None

    def create_order_return(self, data: Dict[str, Any]) -> Optional[OrderReturn]:
        """ثبت مرجوعی سفارش"""
        try:
            order_return = OrderReturn(**data)
            self.db.add(order_return)
            self.db.commit()
            self.db.refresh(order_return)
            return order_return
        except Exception as e:
            logger.error(f"Error creating order return: {str(e)}")
            self.db.rollback()
            return None

    def add_return_item(self, data: Dict[str, Any]) -> Optional[OrderItemReturn]:
        """افزودن آیتم به مرجوعی"""
        try:
            return_item = OrderItemReturn(**data)
            self.db.add(return_item)
            self.db.commit()
            self.db.refresh(return_item)
            return return_item
        except Exception as e:
            logger.error(f"Error adding return item: {str(e)}")
            self.db.rollback()
            return None

    def calculate_order_totals(self, order_id: int) -> Optional[Dict[str, float]]:
        """محاسبه مجموع سفارش"""
        try:
            order = self.get_order(order_id)
            if not order:
                return None

            total_amount = sum(item.total_amount for item in order.items)
            discount_amount = sum(item.discount_amount for item in order.items)
            tax_amount = sum(item.tax_amount for item in order.items)
            final_amount = total_amount - discount_amount + tax_amount + order.shipping_amount

            return {
                "total_amount": total_amount,
                "discount_amount": discount_amount,
                "tax_amount": tax_amount,
                "shipping_amount": order.shipping_amount,
                "final_amount": final_amount
            }
        except Exception as e:
            logger.error(f"Error calculating order totals: {str(e)}")
            return None

    def get_order_history(self, order_id: int) -> List[Dict[str, Any]]:
        """دریافت تاریخچه سفارش"""
        try:
            order = self.get_order(order_id)
            if not order:
                return []

            history = []
            
            # اضافه کردن تغییرات وضعیت
            history.append({
                "date": order.created_at,
                "action": "create",
                "details": "ایجاد سفارش"
            })

            # اضافه کردن پرداخت‌ها
            for payment in order.payments:
                history.append({
                    "date": payment.payment_date,
                    "action": "payment",
                    "details": f"پرداخت {payment.amount} تومان"
                })

            # اضافه کردن ارسال‌ها
            for shipment in order.shipments:
                history.append({
                    "date": shipment.created_at,
                    "action": "shipment",
                    "details": f"ارسال سفارش - شماره پیگیری: {shipment.tracking_number}"
                })

            # اضافه کردن مرجوعی‌ها
            for order_return in order.returns:
                history.append({
                    "date": order_return.created_at,
                    "action": "return",
                    "details": f"مرجوعی سفارش - مبلغ: {order_return.refund_amount} تومان"
                })

            return sorted(history, key=lambda x: x["date"])
        except Exception as e:
            logger.error(f"Error getting order history: {str(e)}")
            return []

    def get_customer_orders(self, customer_id: int, status: Optional[str] = None) -> List[Order]:
        """دریافت سفارشات مشتری"""
        try:
            query = self.db.query(Order).filter(Order.customer_id == customer_id)
            if status:
                query = query.filter(Order.status == status)
            return query.order_by(Order.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting customer orders: {str(e)}")
            return []

    def get_sales_rep_orders(self, sales_rep_id: int, status: Optional[str] = None) -> List[Order]:
        """دریافت سفارشات نماینده فروش"""
        try:
            query = self.db.query(Order).filter(Order.sales_rep_id == sales_rep_id)
            if status:
                query = query.filter(Order.status == status)
            return query.order_by(Order.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting sales rep orders: {str(e)}")
            return [] 