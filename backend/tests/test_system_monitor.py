import unittest
from datetime import datetime
from app.core.system_monitor import SystemMonitor

class TestSystemMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = SystemMonitor('sqlite:///test.db')
    
    def test_check_accounting_integrity(self):
        issues = self.monitor.check_accounting_integrity()
        self.assertIsInstance(issues, list)
        for issue in issues:
            self.assertIn('type', issue)
            self.assertIn('message', issue)
            self.assertIn('severity', issue)
    
    def test_check_inventory_integrity(self):
        issues = self.monitor.check_inventory_integrity()
        self.assertIsInstance(issues, list)
        for issue in issues:
            self.assertIn('type', issue)
            self.assertIn('message', issue)
            self.assertIn('severity', issue)
    
    def test_check_treasury_integrity(self):
        issues = self.monitor.check_treasury_integrity()
        self.assertIsInstance(issues, list)
        for issue in issues:
            self.assertIn('type', issue)
            self.assertIn('message', issue)
            self.assertIn('severity', issue)
    
    def test_check_sales_integrity(self):
        issues = self.monitor.check_sales_integrity()
        self.assertIsInstance(issues, list)
        for issue in issues:
            self.assertIn('type', issue)
            self.assertIn('message', issue)
            self.assertIn('severity', issue)
    
    def test_check_all_integrity(self):
        issues = self.monitor.check_all_integrity()
        self.assertIsInstance(issues, list)
        for issue in issues:
            self.assertIn('type', issue)
            self.assertIn('message', issue)
            self.assertIn('severity', issue)
    
    def test_send_notifications(self):
        test_issues = [
            {
                'type': 'accounting_warehouse_mismatch',
                'message': 'Test message',
                'severity': 'high'
            },
            {
                'type': 'inventory_negative',
                'message': 'Test message',
                'severity': 'high'
            }
        ]
        result = self.monitor.send_notifications(test_issues)
        self.assertIsInstance(result, bool)

if __name__ == '__main__':
    unittest.main() 