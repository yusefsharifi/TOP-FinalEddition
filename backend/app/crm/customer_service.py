import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import requests
from twilio.rest import Client
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import json

from .customer import Customer, CustomerType
from .customer_contact import CustomerContact, ContactType
from .customer_communication import CustomerCommunication, CommunicationType, CommunicationDirection, CommunicationStatus
from .customer_document import CustomerDocument, DocumentType
from .customer_activity import CustomerActivity, ActivityType, ActivityStatus
from .customer_preference import CustomerPreference

class CustomerService:
    """سرویس مدیریت مشتریان"""
    
    def __init__(self, db: Session):
        self.logger = logging.getLogger(__name__)
        self.db = db
        
        # تنظیمات سرویس‌های ارتباطی
        self.sms_config = {
            'account_sid': 'YOUR_TWILIO_ACCOUNT_SID',
            'auth_token': 'YOUR_TWILIO_AUTH_TOKEN',
            'from_number': 'YOUR_TWILIO_PHONE_NUMBER'
        }
        
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'YOUR_EMAIL_USERNAME',
            'password': 'YOUR_EMAIL_PASSWORD'
        }
        
        self.whatsapp_config = {
            'api_key': 'YOUR_WHATSAPP_API_KEY',
            'phone_number_id': 'YOUR_WHATSAPP_PHONE_NUMBER_ID'
        }
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Customer:
        """ایجاد مشتری جدید"""
        try:
            customer = Customer(**customer_data)
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)
            return customer
        except Exception as e:
            self.logger.error(f"خطا در ایجاد مشتری: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_customer(self, customer_id: int) -> Customer:
        """دریافت اطلاعات مشتری"""
        try:
            customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="مشتری یافت نشد")
            return customer
        except Exception as e:
            self.logger.error(f"خطا در دریافت اطلاعات مشتری: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> Customer:
        """بروزرسانی اطلاعات مشتری"""
        try:
            customer = self.get_customer(customer_id)
            for key, value in customer_data.items():
                setattr(customer, key, value)
            self.db.commit()
            self.db.refresh(customer)
            return customer
        except Exception as e:
            self.logger.error(f"خطا در بروزرسانی اطلاعات مشتری: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def delete_customer(self, customer_id: int) -> bool:
        """حذف مشتری"""
        try:
            customer = self.get_customer(customer_id)
            self.db.delete(customer)
            self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"خطا در حذف مشتری: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def add_contact(self, customer_id: int, contact_data: Dict[str, Any]) -> CustomerContact:
        """افزودن تماس جدید به مشتری"""
        try:
            customer = self.get_customer(customer_id)
            contact = CustomerContact(**contact_data, customer_id=customer_id)
            self.db.add(contact)
            self.db.commit()
            self.db.refresh(contact)
            return contact
        except Exception as e:
            self.logger.error(f"خطا در افزودن تماس: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def send_communication(self, customer_id: int, communication_data: Dict[str, Any]) -> CustomerCommunication:
        """ارسال پیام به مشتری"""
        try:
            customer = self.get_customer(customer_id)
            communication = CustomerCommunication(
                **communication_data,
                customer_id=customer_id,
                direction=CommunicationDirection.OUTBOUND
            )
            
            # ارسال پیام بر اساس نوع ارتباط
            if communication.type == CommunicationType.SMS:
                self._send_sms(communication)
            elif communication.type == CommunicationType.EMAIL:
                self._send_email(communication)
            elif communication.type == CommunicationType.WHATSAPP:
                self._send_whatsapp(communication)
            
            self.db.add(communication)
            self.db.commit()
            self.db.refresh(communication)
            return communication
        except Exception as e:
            self.logger.error(f"خطا در ارسال پیام: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def _send_sms(self, communication: CustomerCommunication) -> bool:
        """ارسال پیامک"""
        try:
            client = Client(self.sms_config['account_sid'], self.sms_config['auth_token'])
            message = client.messages.create(
                body=communication.content,
                from_=self.sms_config['from_number'],
                to=communication.customer.mobile
            )
            communication.status = CommunicationStatus.SENT
            communication.sent_at = datetime.utcnow()
            communication.metadata = {'message_sid': message.sid}
            return True
        except Exception as e:
            self.logger.error(f"خطا در ارسال پیامک: {str(e)}")
            communication.status = CommunicationStatus.FAILED
            communication.metadata = {'error': str(e)}
            return False
    
    def _send_email(self, communication: CustomerCommunication) -> bool:
        """ارسال ایمیل"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['username']
            msg['To'] = communication.customer.email
            msg['Subject'] = communication.subject
            
            msg.attach(MIMEText(communication.content, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            
            communication.status = CommunicationStatus.SENT
            communication.sent_at = datetime.utcnow()
            return True
        except Exception as e:
            self.logger.error(f"خطا در ارسال ایمیل: {str(e)}")
            communication.status = CommunicationStatus.FAILED
            communication.metadata = {'error': str(e)}
            return False
    
    def _send_whatsapp(self, communication: CustomerCommunication) -> bool:
        """ارسال پیام واتساپ"""
        try:
            url = f"https://graph.facebook.com/v17.0/{self.whatsapp_config['phone_number_id']}/messages"
            headers = {
                "Authorization": f"Bearer {self.whatsapp_config['api_key']}",
                "Content-Type": "application/json"
            }
            data = {
                "messaging_product": "whatsapp",
                "to": communication.customer.mobile,
                "type": "text",
                "text": {"body": communication.content}
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            communication.status = CommunicationStatus.SENT
            communication.sent_at = datetime.utcnow()
            communication.metadata = {'message_id': response.json().get('messages', [{}])[0].get('id')}
            return True
        except Exception as e:
            self.logger.error(f"خطا در ارسال پیام واتساپ: {str(e)}")
            communication.status = CommunicationStatus.FAILED
            communication.metadata = {'error': str(e)}
            return False
    
    def create_activity(self, customer_id: int, activity_data: Dict[str, Any]) -> CustomerActivity:
        """ایجاد فعالیت جدید برای مشتری"""
        try:
            customer = self.get_customer(customer_id)
            activity = CustomerActivity(**activity_data, customer_id=customer_id)
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            return activity
        except Exception as e:
            self.logger.error(f"خطا در ایجاد فعالیت: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def update_activity_status(self, activity_id: int, status: ActivityStatus) -> CustomerActivity:
        """بروزرسانی وضعیت فعالیت"""
        try:
            activity = self.db.query(CustomerActivity).filter(CustomerActivity.id == activity_id).first()
            if not activity:
                raise HTTPException(status_code=404, detail="فعالیت یافت نشد")
            
            activity.status = status
            if status == ActivityStatus.COMPLETED:
                activity.end_date = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(activity)
            return activity
        except Exception as e:
            self.logger.error(f"خطا در بروزرسانی وضعیت فعالیت: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def add_document(self, customer_id: int, document_data: Dict[str, Any]) -> CustomerDocument:
        """افزودن سند جدید به مشتری"""
        try:
            customer = self.get_customer(customer_id)
            document = CustomerDocument(**document_data, customer_id=customer_id)
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            return document
        except Exception as e:
            self.logger.error(f"خطا در افزودن سند: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def update_preferences(self, customer_id: int, preferences_data: Dict[str, Any]) -> CustomerPreference:
        """بروزرسانی ترجیحات مشتری"""
        try:
            customer = self.get_customer(customer_id)
            preferences = self.db.query(CustomerPreference).filter(
                CustomerPreference.customer_id == customer_id
            ).first()
            
            if not preferences:
                preferences = CustomerPreference(customer_id=customer_id)
                self.db.add(preferences)
            
            for key, value in preferences_data.items():
                setattr(preferences, key, value)
            
            self.db.commit()
            self.db.refresh(preferences)
            return preferences
        except Exception as e:
            self.logger.error(f"خطا در بروزرسانی ترجیحات: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_customer_communications(self, customer_id: int) -> List[CustomerCommunication]:
        """دریافت تاریخچه ارتباطات مشتری"""
        try:
            return self.db.query(CustomerCommunication).filter(
                CustomerCommunication.customer_id == customer_id
            ).order_by(CustomerCommunication.created_at.desc()).all()
        except Exception as e:
            self.logger.error(f"خطا در دریافت تاریخچه ارتباطات: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_customer_activities(self, customer_id: int) -> List[CustomerActivity]:
        """دریافت فعالیت‌های مشتری"""
        try:
            return self.db.query(CustomerActivity).filter(
                CustomerActivity.customer_id == customer_id
            ).order_by(CustomerActivity.start_date.desc()).all()
        except Exception as e:
            self.logger.error(f"خطا در دریافت فعالیت‌ها: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_customer_documents(self, customer_id: int) -> List[CustomerDocument]:
        """دریافت اسناد مشتری"""
        try:
            return self.db.query(CustomerDocument).filter(
                CustomerDocument.customer_id == customer_id
            ).order_by(CustomerDocument.created_at.desc()).all()
        except Exception as e:
            self.logger.error(f"خطا در دریافت اسناد: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def search_customers(self, query: str) -> List[Customer]:
        """جستجوی مشتریان"""
        try:
            return self.db.query(Customer).filter(
                (Customer.name.ilike(f"%{query}%")) |
                (Customer.code.ilike(f"%{query}%")) |
                (Customer.mobile.ilike(f"%{query}%")) |
                (Customer.email.ilike(f"%{query}%"))
            ).all()
        except Exception as e:
            self.logger.error(f"خطا در جستجوی مشتریان: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e)) 