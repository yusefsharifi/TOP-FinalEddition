import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.crm.models.advanced_loyalty import (
    ExperientialReward, PersonalizedReward, PartnerReward,
    CustomerRewardPreference, RewardRedemptionHistory, RewardType
)
from app.crm.models.loyalty import CustomerMembership, PointTransaction, PointTransactionType
from app.crm.communication.advanced_reward_service import AdvancedRewardService
from app.utils.logger import setup_logger

class TestAdvancedRewardService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی محیط تست"""
        # ایجاد موتور دیتابیس تست
        self.engine = create_engine('sqlite:///:memory:')
        self.Session = sessionmaker(bind=self.engine)
        
        # ایجاد جداول
        CustomerMembership.metadata.create_all(self.engine)
        ExperientialReward.metadata.create_all(self.engine)
        PersonalizedReward.metadata.create_all(self.engine)
        PartnerReward.metadata.create_all(self.engine)
        CustomerRewardPreference.metadata.create_all(self.engine)
        RewardRedemptionHistory.metadata.create_all(self.engine)
        PointTransaction.metadata.create_all(self.engine)
        
        # ایجاد سشن دیتابیس
        self.db = self.Session()
        
        # ایجاد سرویس
        self.service = AdvancedRewardService(self.db)
        
        # ایجاد داده‌های تست
        self._create_test_data()

    def tearDown(self):
        """پاکسازی محیط تست"""
        self.db.close()

    def _create_test_data(self):
        """ایجاد داده‌های تست"""
        # ایجاد عضویت مشتری
        self.membership = CustomerMembership(
            customer_id=1,
            points_balance=1000,
            tier="GOLD"
        )
        self.db.add(self.membership)
        self.db.commit()

        # ایجاد پاداش تجربه‌ای
        self.experiential_reward = ExperientialReward(
            name="تور تفریحی",
            description="تور یک روزه به منطقه تفریحی",
            points_cost=500,
            quantity_available=10,
            experience_type="TOUR",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        self.db.add(self.experiential_reward)
        self.db.commit()

        # ایجاد پاداش شخصی‌سازی شده
        self.personalized_reward = PersonalizedReward(
            name="کارت هدیه",
            description="کارت هدیه با مبلغ دلخواه",
            points_cost=300,
            min_value=100000,
            max_value=1000000,
            validity_days=90,
            is_active=True
        )
        self.db.add(self.personalized_reward)
        self.db.commit()

        # ایجاد پاداش مشارکتی
        self.partner_reward = PartnerReward(
            name="تخفیف رستوران",
            description="تخفیف 20 درصدی در رستوران شریک",
            points_cost=200,
            quantity_available=20,
            partner_name="رستوران شریک",
            discount_percentage=20,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=60),
            is_active=True
        )
        self.db.add(self.partner_reward)
        self.db.commit()

    def test_create_experiential_reward(self):
        """تست ایجاد پاداش تجربه‌ای"""
        data = {
            "name": "تور جدید",
            "description": "تور دو روزه",
            "points_cost": 800,
            "quantity_available": 5,
            "experience_type": "TOUR",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=15),
            "is_active": True
        }
        
        reward = self.service.create_experiential_reward(data)
        self.assertIsNotNone(reward)
        self.assertEqual(reward.name, "تور جدید")
        self.assertEqual(reward.points_cost, 800)

    def test_create_personalized_reward(self):
        """تست ایجاد پاداش شخصی‌سازی شده"""
        data = {
            "name": "کارت هدیه جدید",
            "description": "کارت هدیه با مبلغ دلخواه",
            "points_cost": 400,
            "min_value": 200000,
            "max_value": 2000000,
            "validity_days": 60,
            "is_active": True
        }
        
        reward = self.service.create_personalized_reward(data)
        self.assertIsNotNone(reward)
        self.assertEqual(reward.name, "کارت هدیه جدید")
        self.assertEqual(reward.points_cost, 400)

    def test_create_partner_reward(self):
        """تست ایجاد پاداش مشارکتی"""
        data = {
            "name": "تخفیف جدید",
            "description": "تخفیف 30 درصدی",
            "points_cost": 300,
            "quantity_available": 15,
            "partner_name": "شریک جدید",
            "discount_percentage": 30,
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=45),
            "is_active": True
        }
        
        reward = self.service.create_partner_reward(data)
        self.assertIsNotNone(reward)
        self.assertEqual(reward.name, "تخفیف جدید")
        self.assertEqual(reward.points_cost, 300)

    def test_get_available_rewards(self):
        """تست دریافت پاداش‌های قابل استفاده"""
        rewards = self.service.get_available_rewards(1)
        
        self.assertIn("experiential", rewards)
        self.assertIn("personalized", rewards)
        self.assertIn("partner", rewards)
        
        self.assertEqual(len(rewards["experiential"]), 1)
        self.assertEqual(len(rewards["personalized"]), 1)
        self.assertEqual(len(rewards["partner"]), 1)

    def test_redeem_experiential_reward(self):
        """تست استفاده از پاداش تجربه‌ای"""
        history = self.service.redeem_experiential_reward(1, self.experiential_reward.id)
        
        self.assertIsNotNone(history)
        self.assertEqual(history.reward_type, RewardType.EXPERIENTIAL)
        self.assertEqual(history.points_cost, 500)
        
        # بررسی به‌روزرسانی موجودی امتیاز
        membership = self.db.query(CustomerMembership).filter_by(customer_id=1).first()
        self.assertEqual(membership.points_balance, 500)
        
        # بررسی کاهش موجودی پاداش
        reward = self.db.query(ExperientialReward).filter_by(id=self.experiential_reward.id).first()
        self.assertEqual(reward.quantity_available, 9)

    def test_redeem_personalized_reward(self):
        """تست استفاده از پاداش شخصی‌سازی شده"""
        personalization_data = {
            "amount": 500000,
            "message": "تبریک تولد"
        }
        
        history = self.service.redeem_personalized_reward(1, self.personalized_reward.id, personalization_data)
        
        self.assertIsNotNone(history)
        self.assertEqual(history.reward_type, RewardType.PERSONALIZED)
        self.assertEqual(history.points_cost, 300)
        self.assertEqual(history.metadata["personalization_data"], personalization_data)
        
        # بررسی به‌روزرسانی موجودی امتیاز
        membership = self.db.query(CustomerMembership).filter_by(customer_id=1).first()
        self.assertEqual(membership.points_balance, 700)

    def test_redeem_partner_reward(self):
        """تست استفاده از پاداش مشارکتی"""
        history = self.service.redeem_partner_reward(1, self.partner_reward.id)
        
        self.assertIsNotNone(history)
        self.assertEqual(history.reward_type, RewardType.PARTNER)
        self.assertEqual(history.points_cost, 200)
        
        # بررسی به‌روزرسانی موجودی امتیاز
        membership = self.db.query(CustomerMembership).filter_by(customer_id=1).first()
        self.assertEqual(membership.points_balance, 800)
        
        # بررسی کاهش موجودی پاداش
        reward = self.db.query(PartnerReward).filter_by(id=self.partner_reward.id).first()
        self.assertEqual(reward.quantity_available, 19)

    def test_update_reward_preferences(self):
        """تست به‌روزرسانی ترجیحات پاداش"""
        preferences = {
            "preferred_reward_types": ["EXPERIENTIAL", "PERSONALIZED"],
            "min_points_threshold": 200,
            "max_points_threshold": 1000,
            "notification_enabled": True
        }
        
        updated_preferences = self.service.update_reward_preferences(1, preferences)
        
        self.assertIsNotNone(updated_preferences)
        self.assertEqual(updated_preferences.preferred_reward_types, ["EXPERIENTIAL", "PERSONALIZED"])
        self.assertEqual(updated_preferences.min_points_threshold, 200)
        self.assertEqual(updated_preferences.max_points_threshold, 1000)
        self.assertTrue(updated_preferences.notification_enabled)

    def test_get_redemption_history(self):
        """تست دریافت تاریخچه استفاده از پاداش‌ها"""
        # استفاده از چند پاداش
        self.service.redeem_experiential_reward(1, self.experiential_reward.id)
        self.service.redeem_personalized_reward(1, self.personalized_reward.id, {"amount": 300000})
        self.service.redeem_partner_reward(1, self.partner_reward.id)
        
        history = self.service.get_redemption_history(1)
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].reward_type, RewardType.PARTNER)
        self.assertEqual(history[1].reward_type, RewardType.PERSONALIZED)
        self.assertEqual(history[2].reward_type, RewardType.EXPERIENTIAL)

if __name__ == '__main__':
    unittest.main() 