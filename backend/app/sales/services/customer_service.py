from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.sales.models.customer import (
    Customer, CustomerContact, CustomerNote,
    CustomerActivity, CustomerSegment,
    CustomerType, CustomerStatus
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, data: Dict[str, Any]) -> Optional[Customer]:
        """ایجاد مشتری جدید"""
        try:
            customer = Customer(**data)
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)
            return customer
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            self.db.rollback()
            return None

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """دریافت اطلاعات مشتری"""
        try:
            return self.db.query(Customer).filter(
                Customer.id == customer_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting customer: {str(e)}")
            return None

    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Optional[Customer]:
        """به‌روزرسانی اطلاعات مشتری"""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return None

            for key, value in data.items():
                setattr(customer, key, value)

            self.db.commit()
            self.db.refresh(customer)
            return customer
        except Exception as e:
            logger.error(f"Error updating customer: {str(e)}")
            self.db.rollback()
            return None

    def update_customer_status(self, customer_id: int, status: str) -> Optional[Customer]:
        """به‌روزرسانی وضعیت مشتری"""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return None

            customer.status = status
            self.db.commit()
            self.db.refresh(customer)
            return customer
        except Exception as e:
            logger.error(f"Error updating customer status: {str(e)}")
            self.db.rollback()
            return None

    def add_customer_contact(self, data: Dict[str, Any]) -> Optional[CustomerContact]:
        """افزودن مخاطب به مشتری"""
        try:
            contact = CustomerContact(**data)
            self.db.add(contact)
            self.db.commit()
            self.db.refresh(contact)
            return contact
        except Exception as e:
            logger.error(f"Error adding customer contact: {str(e)}")
            self.db.rollback()
            return None

    def get_customer_contacts(self, customer_id: int) -> List[CustomerContact]:
        """دریافت مخاطبین مشتری"""
        try:
            return self.db.query(CustomerContact).filter(
                CustomerContact.customer_id == customer_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting customer contacts: {str(e)}")
            return []

    def add_customer_note(self, data: Dict[str, Any]) -> Optional[CustomerNote]:
        """افزودن یادداشت به مشتری"""
        try:
            note = CustomerNote(**data)
            self.db.add(note)
            self.db.commit()
            self.db.refresh(note)
            return note
        except Exception as e:
            logger.error(f"Error adding customer note: {str(e)}")
            self.db.rollback()
            return None

    def get_customer_notes(self, customer_id: int, note_type: Optional[str] = None) -> List[CustomerNote]:
        """دریافت یادداشت‌های مشتری"""
        try:
            query = self.db.query(CustomerNote).filter(
                CustomerNote.customer_id == customer_id
            )
            if note_type:
                query = query.filter(CustomerNote.note_type == note_type)
            return query.order_by(CustomerNote.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting customer notes: {str(e)}")
            return []

    def add_customer_activity(self, data: Dict[str, Any]) -> Optional[CustomerActivity]:
        """افزودن فعالیت به مشتری"""
        try:
            activity = CustomerActivity(**data)
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            return activity
        except Exception as e:
            logger.error(f"Error adding customer activity: {str(e)}")
            self.db.rollback()
            return None

    def get_customer_activities(self, customer_id: int, activity_type: Optional[str] = None) -> List[CustomerActivity]:
        """دریافت فعالیت‌های مشتری"""
        try:
            query = self.db.query(CustomerActivity).filter(
                CustomerActivity.customer_id == customer_id
            )
            if activity_type:
                query = query.filter(CustomerActivity.activity_type == activity_type)
            return query.order_by(CustomerActivity.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting customer activities: {str(e)}")
            return []

    def create_customer_segment(self, data: Dict[str, Any]) -> Optional[CustomerSegment]:
        """ایجاد بخش مشتریان"""
        try:
            segment = CustomerSegment(**data)
            self.db.add(segment)
            self.db.commit()
            self.db.refresh(segment)
            return segment
        except Exception as e:
            logger.error(f"Error creating customer segment: {str(e)}")
            self.db.rollback()
            return None

    def get_customer_segment(self, segment_id: int) -> Optional[CustomerSegment]:
        """دریافت بخش مشتریان"""
        try:
            return self.db.query(CustomerSegment).filter(
                CustomerSegment.id == segment_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting customer segment: {str(e)}")
            return None

    def get_customers_by_segment(self, segment_id: int) -> List[Customer]:
        """دریافت مشتریان یک بخش"""
        try:
            segment = self.get_customer_segment(segment_id)
            if not segment:
                return []

            # اینجا باید منطق فیلتر کردن مشتریان بر اساس معیارهای بخش پیاده‌سازی شود
            return []
        except Exception as e:
            logger.error(f"Error getting customers by segment: {str(e)}")
            return []

    def search_customers(self, query: str, customer_type: Optional[str] = None) -> List[Customer]:
        """جستجوی مشتریان"""
        try:
            search_query = self.db.query(Customer).filter(
                or_(
                    Customer.first_name.ilike(f"%{query}%"),
                    Customer.last_name.ilike(f"%{query}%"),
                    Customer.company_name.ilike(f"%{query}%"),
                    Customer.email.ilike(f"%{query}%"),
                    Customer.phone.ilike(f"%{query}%"),
                    Customer.mobile.ilike(f"%{query}%")
                )
            )
            if customer_type:
                search_query = search_query.filter(Customer.customer_type == customer_type)
            return search_query.all()
        except Exception as e:
            logger.error(f"Error searching customers: {str(e)}")
            return []

    def get_customers_by_sales_rep(self, sales_rep_id: int, status: Optional[str] = None) -> List[Customer]:
        """دریافت مشتریان نماینده فروش"""
        try:
            query = self.db.query(Customer).filter(
                Customer.sales_rep_id == sales_rep_id
            )
            if status:
                query = query.filter(Customer.status == status)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting customers by sales rep: {str(e)}")
            return []

    def get_customers_by_territory(self, territory: str, status: Optional[str] = None) -> List[Customer]:
        """دریافت مشتریان یک منطقه"""
        try:
            query = self.db.query(Customer).filter(
                Customer.assigned_territory == territory
            )
            if status:
                query = query.filter(Customer.status == status)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting customers by territory: {str(e)}")
            return []

    def get_customer_statistics(self, customer_id: int) -> Dict[str, Any]:
        """دریافت آمار مشتری"""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return {}

            # اینجا باید منطق محاسبه آمار مشتری پیاده‌سازی شود
            return {
                "total_orders": 0,
                "total_spent": 0.0,
                "average_order_value": 0.0,
                "last_order_date": None,
                "days_since_last_order": 0,
                "total_returns": 0,
                "return_rate": 0.0,
                "customer_lifetime_value": 0.0
            }
        except Exception as e:
            logger.error(f"Error getting customer statistics: {str(e)}")
            return {} 