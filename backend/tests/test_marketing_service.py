import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.sales.models.marketing import (
    MarketingCampaign, CampaignStatus, CampaignType,
    Discount, DiscountType, MarketerReward, MarketerRewardType,
    MarketerPerformance
)
from app.sales.services.marketing_service import MarketingService
from app.utils.logger import setup_logger

class TestMarketingService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی محیط تست"""
        # ایجاد موتور دیتابیس تست
        self.engine = create_engine('sqlite:///:memory:')
        self.Session = sessionmaker(bind=self.engine)
        
        # ایجاد جداول
        MarketingCampaign.metadata.create_all(self.engine)
        Discount.metadata.create_all(self.engine)
        MarketerReward.metadata.create_all(self.engine)
        MarketerPerformance.metadata.create_all(self.engine)
        
        # ایجاد سشن دیتابیس
        self.db = self.Session()
        
        # ایجاد سرویس
        self.service = MarketingService(self.db)
        
        # ایجاد داده‌های تست
        self._create_test_data()

    def tearDown(self):
        """پاکسازی محیط تست"""
        self.db.close()

    def _create_test_data(self):
        """ایجاد داده‌های تست"""
        # ایجاد کمپین بازاریابی
        self.campaign = MarketingCampaign(
            name="کمپین تابستانه",
            description="تخفیف ویژه محصولات تابستانه",
            campaign_type=CampaignType.EMAIL,
            status=CampaignStatus.ACTIVE,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            budget=1000000,
            target_audience={"age_range": [18, 45], "gender": "all"},
            content={"subject": "تخفیف ویژه", "body": "محتوا"},
            metrics={"sent": 1000, "opened": 800, "clicked": 400}
        )
        self.db.add(self.campaign)
        self.db.commit()

        # ایجاد تخفیف
        self.discount = Discount(
            name="تخفیف 20 درصدی",
            description="تخفیف 20 درصدی برای خرید بالای 1 میلیون",
            discount_type=DiscountType.PERCENTAGE,
            value=20,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=15),
            min_purchase_amount=1000000,
            max_discount_amount=500000,
            is_active=True,
            usage_limit=100
        )
        self.db.add(self.discount)
        self.db.commit()

    def test_create_campaign(self):
        """تست ایجاد کمپین بازاریابی"""
        data = {
            "name": "کمپین جدید",
            "description": "تخفیف ویژه محصولات جدید",
            "campaign_type": CampaignType.SMS,
            "status": CampaignStatus.DRAFT,
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=15),
            "budget": 500000,
            "target_audience": {"age_range": [25, 35]},
            "content": {"message": "پیام تست"},
            "metrics": {}
        }
        
        campaign = self.service.create_campaign(data)
        self.assertIsNotNone(campaign)
        self.assertEqual(campaign.name, "کمپین جدید")
        self.assertEqual(campaign.campaign_type, CampaignType.SMS)

    def test_update_campaign_status(self):
        """تست به‌روزرسانی وضعیت کمپین"""
        campaign = self.service.update_campaign_status(self.campaign.id, CampaignStatus.PAUSED)
        self.assertIsNotNone(campaign)
        self.assertEqual(campaign.status, CampaignStatus.PAUSED)

    def test_get_campaign_metrics(self):
        """تست دریافت شاخص‌های عملکرد کمپین"""
        metrics = self.service.get_campaign_metrics(self.campaign.id)
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics["sent"], 1000)
        self.assertEqual(metrics["opened"], 800)
        self.assertEqual(metrics["clicked"], 400)

    def test_create_discount(self):
        """تست ایجاد تخفیف"""
        data = {
            "name": "تخفیف 10 درصدی",
            "description": "تخفیف 10 درصدی برای همه محصولات",
            "discount_type": DiscountType.PERCENTAGE,
            "value": 10,
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=10),
            "is_active": True
        }
        
        discount = self.service.create_discount(data)
        self.assertIsNotNone(discount)
        self.assertEqual(discount.name, "تخفیف 10 درصدی")
        self.assertEqual(discount.value, 10)

    def test_apply_discount(self):
        """تست اعمال تخفیف"""
        # تست تخفیف درصدی
        discount_amount = self.service.apply_discount(self.discount.id, 2000000)
        self.assertIsNotNone(discount_amount)
        self.assertEqual(discount_amount, 400000)  # 20% of 2000000

        # تست حداقل مبلغ خرید
        discount_amount = self.service.apply_discount(self.discount.id, 500000)
        self.assertIsNone(discount_amount)  # کمتر از حداقل مبلغ خرید

        # تست محدودیت تعداد استفاده
        for _ in range(100):
            self.service.apply_discount(self.discount.id, 2000000)
        discount_amount = self.service.apply_discount(self.discount.id, 2000000)
        self.assertIsNone(discount_amount)  # محدودیت تعداد استفاده

    def test_create_marketer_reward(self):
        """تست ایجاد پاداش بازاریاب"""
        data = {
            "marketer_id": 1,
            "reward_type": MarketerRewardType.COMMISSION,
            "amount": 100000,
            "description": "کمیسیون فروش",
            "status": "pending"
        }
        
        reward = self.service.create_marketer_reward(data)
        self.assertIsNotNone(reward)
        self.assertEqual(reward.amount, 100000)
        self.assertEqual(reward.status, "pending")

    def test_calculate_commission(self):
        """تست محاسبه کمیسیون"""
        commission = self.service.calculate_commission(1, 1000000, 5)  # 5% commission
        self.assertEqual(commission, 50000)  # 5% of 1000000

    def test_record_new_customer_reward(self):
        """تست ثبت پاداش جذب مشتری جدید"""
        reward = self.service.record_new_customer_reward(1, 2, 50000)
        self.assertIsNotNone(reward)
        self.assertEqual(reward.reward_type, MarketerRewardType.NEW_CUSTOMER)
        self.assertEqual(reward.amount, 50000)
        self.assertEqual(reward.reference_id, 2)

    def test_update_marketer_performance(self):
        """تست به‌روزرسانی عملکرد بازاریاب"""
        period_start = datetime.utcnow().date()
        period_end = (datetime.utcnow() + timedelta(days=30)).date()
        
        performance = self.service.update_marketer_performance(1, period_start, period_end)
        self.assertIsNotNone(performance)
        self.assertEqual(performance.marketer_id, 1)
        self.assertEqual(performance.period_start, period_start)
        self.assertEqual(performance.period_end, period_end)

if __name__ == '__main__':
    unittest.main() 