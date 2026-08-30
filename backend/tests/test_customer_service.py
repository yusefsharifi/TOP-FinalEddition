import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.crm.customer_service import CustomerService
from app.crm.customer import Customer, CustomerType
from app.crm.customer_contact import CustomerContact, ContactType
from app.crm.customer_communication import CustomerCommunication, CommunicationType, CommunicationDirection, CommunicationStatus
from app.crm.customer_activity import CustomerActivity, ActivityType, ActivityStatus
from app.crm.customer_document import CustomerDocument, DocumentType
from app.crm.customer_preference import CustomerPreference

class TestCustomerService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی تست"""
        self.engine = create_engine('sqlite:///test.db')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.service = CustomerService(self.session)
        
        # ایجاد جداول
        Base.metadata.create_all(self.engine)
    
    def tearDown(self):
        """پاکسازی بعد از تست"""
        self.session.close()
    
    def test_create_customer(self):
        """تست ایجاد مشتری"""
        customer_data = {
            'code': 'CUST001',
            'name': 'Test Customer',
            'type': CustomerType.REGULAR,
            'mobile': '09123456789',
            'email': 'test@example.com'
        }
        
        customer = self.service.create_customer(customer_data)
        
        self.assertIsInstance(customer, Customer)
        self.assertEqual(customer.code, 'CUST001')
        self.assertEqual(customer.name, 'Test Customer')
    
    def test_get_customer(self):
        """تست دریافت مشتری"""
        # ایجاد مشتری تست
        customer_data = {
            'code': 'CUST002',
            'name': 'Test Customer 2',
            'type': CustomerType.REGULAR,
            'mobile': '09123456789',
            'email': 'test2@example.com'
        }
        customer = self.service.create_customer(customer_data)
        
        # دریافت مشتری
        retrieved_customer = self.service.get_customer(customer.id)
        
        self.assertEqual(retrieved_customer.id, customer.id)
        self.assertEqual(retrieved_customer.code, 'CUST002')
    
    def test_update_customer(self):
        """تست بروزرسانی مشتری"""
        # ایجاد مشتری تست
        customer_data = {
            'code': 'CUST003',
            'name': 'Test Customer 3',
            'type': CustomerType.REGULAR,
            'mobile': '09123456789',
            'email': 'test3@example.com'
        }
        customer = self.service.create_customer(customer_data)
        
        # بروزرسانی مشتری
        update_data = {
            'name': 'Updated Customer 3',
            'type': CustomerType.VIP
        }
        updated_customer = self.service.update_customer(customer.id, update_data)
        
        self.assertEqual(updated_customer.name, 'Updated Customer 3')
        self.assertEqual(updated_customer.type, CustomerType.VIP)
    
    def test_delete_customer(self):
        """تست حذف مشتری"""
        # ایجاد مشتری تست
        customer_data = {
            'code': 'CUST004',
            'name': 'Test Customer 4',
            'type': CustomerType.REGULAR,
            'mobile': '09123456789',
            'email': 'test4@example.com'
        }
        customer = self.service.create_customer(customer_data)
        
        # حذف مشتری
        result = self.service.delete_customer(customer.id)
        
        self.assertTrue(result)
        self.assertIsNone(self.service.get_customer(customer.id))
    
    def test_add_contact(self):
        """تست افزودن تماس"""
        # ایجاد مشتری تست
        customer_data = {
            'code': 'CUST005',
            'name': 'Test Customer 5',
            'type': CustomerType.REGULAR,
            'mobile': '09123456789',
            'email': 'test5@example.com'
        }
        customer = self.service.create_customer(customer_data)
        
        # افزودن تماس
        contact_data = {
            'type': ContactType.PRIMARY,
            'name': 'Test Contact',
            'position': 'Manager',
            'mobile': '09123456789',
            'email': 'contact@example.com'
        }
        contact = self.service.add_contact(customer.id, contact_data)
        
        self.assertIsInstance(contact, CustomerContact)
        self.assertEqual(contact.name, 'Test Contact')
        self.assertEqual(contact.customer_id, customer.id)
    
    def test_send_communication(self):
        """تست ارسال پیام"""
        # ایجاد مشتری تست
        customer_data = {
            'code': 'CUST006',
            'name': 'Test Customer 6',
            'type': CustomerType.REGULAR,
            'mobile': '09123456789',
            'email': 'test6@example.com'
        }
        customer = self.service.create_customer(customer_data)
        
        # ارسال پیام
        communication_data = {
            'type': CommunicationType.EMAIL,
            'subject': 'Test Subject',
            'content': 'Test Content'
        }
        communication = self.service.send_communication(customer.id, communication_data)
        
        self.assertIsInstance(communication, CustomerCommunication)
        self.assertEqual(communication.type, CommunicationType.EMAIL)
        self.assertEqual(communication.customer_id, customer.id)
    
    def test_create_activity(self):
        """تست ایجاد فعالیت"""
        # ایجاد مشتری تست
        customer_data = {
            'code': 'CUST007',
            'name': 'Test Customer 7',
            'type': CustomerType.REGULAR,
            'mobile': '09123456789',
            'email': 'test7@example.com'
        }
        customer = self.service.create_customer(customer_data)
        
        # ایجاد فعالیت
        activity_data = {
            'type': ActivityType.MEETING,
            'title': 'Test Meeting',
            'description': 'Test Description',
            'start_date': datetime.utcnow(),
            'duration': 60
        }
        activity = self.service.create_activity(customer.id, activity_data)
        
        self.assertIsInstance(activity, CustomerActivity)
        self.assertEqual(activity.title, 'Test Meeting')
        self.assertEqual(activity.customer_id, customer.id)
    
    def test_add_document(self):
        """تست افزودن سند"""
        # ایجاد مشتری تست
        customer_data = {
            'code': 'CUST008',
            'name': 'Test Customer 8',
            'type': CustomerType.REGULAR,
            'mobile': '09123456789',
            'email': 'test8@example.com'
        }
        customer = self.service.create_customer(customer_data)
        
        # افزودن سند
        document_data = {
            'type': DocumentType.CONTRACT,
            'title': 'Test Contract',
            'description': 'Test Description',
            'file_path': '/path/to/file.pdf',
            'file_name': 'contract.pdf',
            'file_size': 1024,
            'file_type': 'pdf'
        }
        document = self.service.add_document(customer.id, document_data)
        
        self.assertIsInstance(document, CustomerDocument)
        self.assertEqual(document.title, 'Test Contract')
        self.assertEqual(document.customer_id, customer.id)
    
    def test_update_preferences(self):
        """تست بروزرسانی ترجیحات"""
        # ایجاد مشتری تست
        customer_data = {
            'code': 'CUST009',
            'name': 'Test Customer 9',
            'type': CustomerType.REGULAR,
            'mobile': '09123456789',
            'email': 'test9@example.com'
        }
        customer = self.service.create_customer(customer_data)
        
        # بروزرسانی ترجیحات
        preferences_data = {
            'preferred_contact_method': 'email',
            'preferred_contact_time': '9:00-17:00',
            'language': 'fa',
            'timezone': 'Asia/Tehran'
        }
        preferences = self.service.update_preferences(customer.id, preferences_data)
        
        self.assertIsInstance(preferences, CustomerPreference)
        self.assertEqual(preferences.preferred_contact_method, 'email')
        self.assertEqual(preferences.customer_id, customer.id)
    
    def test_search_customers(self):
        """تست جستجوی مشتریان"""
        # ایجاد مشتریان تست
        customers_data = [
            {
                'code': 'CUST010',
                'name': 'Test Customer 10',
                'type': CustomerType.REGULAR,
                'mobile': '09123456789',
                'email': 'test10@example.com'
            },
            {
                'code': 'CUST011',
                'name': 'Test Customer 11',
                'type': CustomerType.REGULAR,
                'mobile': '09123456789',
                'email': 'test11@example.com'
            }
        ]
        for data in customers_data:
            self.service.create_customer(data)
        
        # جستجوی مشتریان
        results = self.service.search_customers('Test Customer')
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all('Test Customer' in c.name for c in results))

if __name__ == '__main__':
    unittest.main() 