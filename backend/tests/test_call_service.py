import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.crm.communication.call_service import CallService
from app.crm.models.call import Call, CallRecording, CallStatus
from app.crm.models.customer import Customer

class TestCallService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی تست"""
        self.engine = create_engine('sqlite:///test.db')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.service = CallService(self.session)
        
        # ایجاد جداول
        Base.metadata.create_all(self.engine)
        
        # ایجاد مشتری تست
        self.customer = Customer(
            name="Test Customer",
            mobile="09123456789",
            email="test@example.com"
        )
        self.session.add(self.customer)
        self.session.commit()
    
    def tearDown(self):
        """پاکسازی بعد از تست"""
        self.session.close()
    
    def test_initiate_call(self):
        """تست شروع تماس"""
        call = self.service.initiate_call(
            customer_id=self.customer.id,
            phone_number="09123456789"
        )
        
        self.assertIsInstance(call, Call)
        self.assertEqual(call.customer_id, self.customer.id)
        self.assertEqual(call.status, CallStatus.INITIATED)
    
    def test_answer_call(self):
        """تست پاسخ به تماس"""
        # ایجاد تماس تست
        call = self.service.initiate_call(
            customer_id=self.customer.id,
            phone_number="09123456789"
        )
        
        # پاسخ به تماس
        result = self.service.answer_call(call.id)
        
        self.assertTrue(result)
        self.assertEqual(call.status, CallStatus.IN_PROGRESS)
    
    def test_end_call(self):
        """تست پایان تماس"""
        # ایجاد تماس تست
        call = self.service.initiate_call(
            customer_id=self.customer.id,
            phone_number="09123456789"
        )
        
        # پاسخ به تماس
        self.service.answer_call(call.id)
        
        # پایان تماس
        result = self.service.end_call(
            call_id=call.id,
            duration=120,
            notes="Test notes"
        )
        
        self.assertTrue(result)
        self.assertEqual(call.status, CallStatus.COMPLETED)
        self.assertEqual(call.duration, 120)
        self.assertEqual(call.notes, "Test notes")
    
    def test_call_recording(self):
        """تست ضبط تماس"""
        # ایجاد تماس تست
        call = self.service.initiate_call(
            customer_id=self.customer.id,
            phone_number="09123456789"
        )
        
        # شروع ضبط
        recording = self.service.start_recording(call.id)
        
        self.assertIsInstance(recording, CallRecording)
        self.assertEqual(recording.call_id, call.id)
        
        # پایان ضبط
        result = self.service.stop_recording(recording.recording_id)
        
        self.assertTrue(result)
        self.assertIsNotNone(recording.audio_file)
        self.assertIsNotNone(recording.transcript)
    
    def test_get_customer_calls(self):
        """تست دریافت تماس‌های مشتری"""
        # ایجاد چند تماس تست
        for i in range(3):
            self.service.initiate_call(
                customer_id=self.customer.id,
                phone_number="09123456789"
            )
        
        calls = self.service.get_customer_calls(self.customer.id)
        
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(c.customer_id == self.customer.id for c in calls))
    
    def test_get_call_statistics(self):
        """تست دریافت آمار تماس‌ها"""
        # ایجاد چند تماس تست
        for i in range(3):
            call = self.service.initiate_call(
                customer_id=self.customer.id,
                phone_number="09123456789"
            )
            self.service.answer_call(call.id)
            self.service.end_call(call.id, duration=120)
        
        # دریافت آمار
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        stats = self.service.get_call_statistics(start_date, end_date)
        
        self.assertEqual(stats["total_calls"], 3)
        self.assertEqual(stats["answered_calls"], 3)
        self.assertEqual(stats["average_duration"], 120)
        self.assertEqual(stats["total_duration"], 360)

if __name__ == '__main__':
    unittest.main() 