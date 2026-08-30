import unittest
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.crm.communication.advanced_loyalty_service import AdvancedLoyaltyService
from app.crm.models.advanced_loyalty import (
    PointMultiplier, SpecialDay, PointRule, CustomerBehavior,
    PointMultiplierType
)
from app.crm.models.loyalty import (
    CustomerMembership, PointTransaction, PointTransactionType,
    MembershipTier
)
from app.crm.models.customer import Customer
from app.db.base_class import Base

class TestAdvancedLoyaltyService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی تست"""
        self.engine = create_engine('sqlite:///test.db')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.service = AdvancedLoyaltyService(self.session)
        
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
        
        # ایجاد عضویت مشتری
        self.membership = CustomerMembership(
            customer_id=self.customer.id,
            tier=MembershipTier.BRONZE
        )
        self.session.add(self.membership)
        self.session.commit()

    def tearDown(self):
        """پاکسازی بعد از تست"""
        self.session.close()

    def test_create_point_multiplier(self):
        """تست ایجاد ضریب امتیازدهی"""
        data = {
            "name": "ضریب نقره‌ای",
            "description": "ضریب امتیازدهی برای مشتریان نقره‌ای",
            "multiplier_type": PointMultiplierType.TIER,
            "multiplier_value": 1.5,
            "tier": MembershipTier.SILVER,
            "start_date": datetime.utcnow()
        }
        
        multiplier = self.service.create_point_multiplier(data)
        
        self.assertIsInstance(multiplier, PointMultiplier)
        self.assertEqual(multiplier.name, "ضریب نقره‌ای")
        self.assertEqual(multiplier.multiplier_value, 1.5)

    def test_create_special_day(self):
        """تست ایجاد روز خاص"""
        data = {
            "name": "جشنواره نوروز",
            "description": "امتیازدهی مضاعف در جشنواره نوروز",
            "date": date.today(),
            "point_multiplier": 2.0,
            "is_active": True
        }
        
        special_day = self.service.create_special_day(data)
        
        self.assertIsInstance(special_day, SpecialDay)
        self.assertEqual(special_day.name, "جشنواره نوروز")
        self.assertEqual(special_day.point_multiplier, 2.0)

    def test_create_point_rule(self):
        """تست ایجاد قانون امتیازدهی"""
        data = {
            "name": "امتیاز خرید بالای 1 میلیون",
            "description": "امتیاز برای خرید بالای 1 میلیون تومان",
            "condition_type": "purchase_amount",
            "condition_value": {"min_amount": 1000000},
            "points": 100,
            "start_date": datetime.utcnow(),
            "is_active": True
        }
        
        rule = self.service.create_point_rule(data)
        
        self.assertIsInstance(rule, PointRule)
        self.assertEqual(rule.name, "امتیاز خرید بالای 1 میلیون")
        self.assertEqual(rule.points, 100)

    def test_apply_point_rules(self):
        """تست اعمال قوانین امتیازدهی"""
        # ایجاد قانون
        rule_data = {
            "name": "امتیاز خرید بالای 1 میلیون",
            "description": "امتیاز برای خرید بالای 1 میلیون تومان",
            "condition_type": "purchase_amount",
            "condition_value": {"min_amount": 1000000},
            "points": 100,
            "start_date": datetime.utcnow(),
            "is_active": True
        }
        rule = self.service.create_point_rule(rule_data)
        
        # اعمال قانون
        behavior_value = {"amount": 1500000}
        transactions = self.service.apply_point_rules(
            self.customer.id,
            "purchase_amount",
            behavior_value
        )
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].points, 100)
        self.assertEqual(self.membership.points_balance, 100)

    def test_calculate_points_with_multipliers(self):
        """تست محاسبه امتیاز با ضریب"""
        # ایجاد ضریب برای سطح برنز
        multiplier_data = {
            "name": "ضریب برنز",
            "description": "ضریب امتیازدهی برای مشتریان برنز",
            "multiplier_type": PointMultiplierType.TIER,
            "multiplier_value": 1.2,
            "tier": MembershipTier.BRONZE,
            "start_date": datetime.utcnow()
        }
        self.service.create_point_multiplier(multiplier_data)
        
        # محاسبه امتیاز
        base_points = 100
        final_points = self.service.calculate_points_with_multipliers(
            base_points,
            self.customer.id
        )
        
        self.assertEqual(final_points, 120)  # 100 * 1.2

if __name__ == '__main__':
    unittest.main() 