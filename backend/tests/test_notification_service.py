import unittest
from datetime import datetime
from app.core.notification_service import NotificationService

class TestNotificationService(unittest.TestCase):
    def setUp(self):
        self.service = NotificationService('sqlite:///test.db')
    
    def test_send_notification(self):
        result = self.service.send_notification(
            user_id=1,
            title='Test Notification',
            message='This is a test notification',
            severity='high'
        )
        self.assertIsInstance(result, bool)
    
    def test_send_batch_notifications(self):
        notifications = [
            {
                'user_id': 1,
                'title': 'Test Notification 1',
                'message': 'This is test notification 1',
                'severity': 'high'
            },
            {
                'user_id': 2,
                'title': 'Test Notification 2',
                'message': 'This is test notification 2',
                'severity': 'medium'
            }
        ]
        result = self.service.send_batch_notifications(notifications)
        self.assertIsInstance(result, bool)
    
    def test_get_user_notifications(self):
        notifications = self.service.get_user_notifications(user_id=1)
        self.assertIsInstance(notifications, list)
        for notification in notifications:
            self.assertIn('id', notification)
            self.assertIn('title', notification)
            self.assertIn('message', notification)
            self.assertIn('severity', notification)
            self.assertIn('created_at', notification)
            self.assertIn('read_at', notification)
    
    def test_mark_notification_as_read(self):
        result = self.service.mark_notification_as_read(notification_id=1)
        self.assertIsInstance(result, bool)

if __name__ == '__main__':
    unittest.main() 