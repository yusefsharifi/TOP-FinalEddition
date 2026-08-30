import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.crm.communication.loyalty_service import LoyaltyService
from app.crm.models.loyalty import (
    CustomerMembership, PointTransaction, Reward, CustomerReward,
    MembershipTier, PointTransactionType, RewardStatus
)
from app.crm.models.customer import Customer
from app.db.base_class import Base

class TestLoyaltyService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی تست"""
        self.engine = create_engine('sqlite:///test.db')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.service = LoyaltyService(self.session)
        
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

    def test_enroll_customer(self):
        """تست ثبت نام مشتری در باشگاه"""
        membership = self.service.enroll_customer(self.customer.id)
        
        self.assertIsInstance(membership, CustomerMembership)
        self.assertEqual(membership.customer_id, self.customer.id)
        self.assertEqual(membership.tier, MembershipTier.BRONZE)
        self.assertEqual(membership.points_balance, 100)  # امتیاز خوش‌آمدگویی

    def test_add_points(self):
        """تست افزودن امتیاز"""
        # ثبت نام مشتری
        membership = self.service.enroll_customer(self.customer.id)
        
        # افزودن امتیاز
        transaction = self.service.add_points(
            membership_id=membership.id,
            points=500,
            transaction_type=PointTransactionType.EARN,
            description="امتیاز خرید"
        )
        
        self.assertIsInstance(transaction, PointTransaction)
        self.assertEqual(transaction.points, 500)
        self.assertEqual(membership.points_balance, 600)  # 100 + 500

    def test_tier_upgrade(self):
        """تست ارتقای سطح عضویت"""
        # ثبت نام مشتری
        membership = self.service.enroll_customer(self.customer.id)
        
        # افزودن امتیاز برای ارتقا به سطح نقره‌ای
        self.service.add_points(
            membership_id=membership.id,
            points=10000,
            transaction_type=PointTransactionType.EARN,
            description="امتیاز ارتقا"
        )
        
        self.assertEqual(membership.tier, MembershipTier.SILVER)
        
        # افزودن امتیاز برای ارتقا به سطح طلایی
        self.service.add_points(
            membership_id=membership.id,
            points=15000,
            transaction_type=PointTransactionType.EARN,
            description="امتیاز ارتقا"
        )
        
        self.assertEqual(membership.tier, MembershipTier.GOLD)

    def test_create_and_redeem_reward(self):
        """تست ایجاد و استفاده از پاداش"""
        # ثبت نام مشتری
        membership = self.service.enroll_customer(self.customer.id)
        
        # افزودن امتیاز
        self.service.add_points(
            membership_id=membership.id,
            points=1000,
            transaction_type=PointTransactionType.EARN,
            description="امتیاز تست"
        )
        
        # ایجاد پاداش
        reward = self.service.create_reward(
            name="تخفیف 10 درصدی",
            description="تخفیف 10 درصدی برای خرید بعدی",
            points_cost=500,
            start_date=datetime.utcnow(),
            quantity_available=10
        )
        
        self.assertIsInstance(reward, Reward)
        self.assertEqual(reward.points_cost, 500)
        
        # استفاده از پاداش
        customer_reward = self.service.redeem_reward(
            membership_id=membership.id,
            reward_id=reward.id
        )
        
        self.assertIsInstance(customer_reward, CustomerReward)
        self.assertEqual(customer_reward.status, RewardStatus.AVAILABLE)
        self.assertEqual(membership.points_balance, 600)  # 100 + 1000 - 500

    def test_get_membership_status(self):
        """تست دریافت وضعیت عضویت"""
        # ثبت نام مشتری
        membership = self.service.enroll_customer(self.customer.id)
        
        # افزودن امتیاز
        self.service.add_points(
            membership_id=membership.id,
            points=1000,
            transaction_type=PointTransactionType.EARN,
            description="امتیاز تست"
        )
        
        # دریافت وضعیت
        status = self.service.get_membership_status(self.customer.id)
        
        self.assertEqual(status["status"], "active")
        self.assertEqual(status["tier"], MembershipTier.BRONZE)
        self.assertEqual(status["points_balance"], 1100)  # 100 + 1000

    def test_get_available_rewards(self):
        """تست دریافت لیست پاداش‌های قابل استفاده"""
        # ثبت نام مشتری
        membership = self.service.enroll_customer(self.customer.id)
        
        # افزودن امتیاز
        self.service.add_points(
            membership_id=membership.id,
            points=1000,
            transaction_type=PointTransactionType.EARN,
            description="امتیاز تست"
        )
        
        # ایجاد چند پاداش
        self.service.create_reward(
            name="تخفیف 10 درصدی",
            description="تخفیف 10 درصدی برای خرید بعدی",
            points_cost=500,
            start_date=datetime.utcnow(),
            quantity_available=10
        )
        
        self.service.create_reward(
            name="ارسال رایگان",
            description="ارسال رایگان برای خرید بعدی",
            points_cost=1000,
            start_date=datetime.utcnow(),
            quantity_available=5
        )
        
        # دریافت لیست پاداش‌ها
        rewards = self.service.get_available_rewards(membership.id)
        
        self.assertEqual(len(rewards), 1)  # فقط پاداش 500 امتیازی قابل استفاده است
        self.assertEqual(rewards[0]["points_cost"], 500)

    def test_get_membership_history(self):
        """تست دریافت تاریخچه عضویت"""
        # ثبت نام مشتری
        membership = self.service.enroll_customer(self.customer.id)
        
        # افزودن امتیاز
        self.service.add_points(
            membership_id=membership.id,
            points=1000,
            transaction_type=PointTransactionType.EARN,
            description="امتیاز تست"
        )
        
        # ایجاد و استفاده از پاداش
        reward = self.service.create_reward(
            name="تخفیف 10 درصدی",
            description="تخفیف 10 درصدی برای خرید بعدی",
            points_cost=500,
            start_date=datetime.utcnow(),
            quantity_available=10
        )
        
        self.service.redeem_reward(
            membership_id=membership.id,
            reward_id=reward.id
        )
        
        # دریافت تاریخچه
        history = self.service.get_membership_history(self.customer.id)
        
        self.assertEqual(len(history["points_history"]), 3)  # خوش‌آمدگویی + کسب + استفاده
        self.assertEqual(len(history["rewards_history"]), 1)

if __name__ == '__main__':
    unittest.main() 