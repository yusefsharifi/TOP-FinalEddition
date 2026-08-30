import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.crm.communication.survey_service import SurveyService
from app.crm.models.survey import Survey, SurveyQuestion, SurveyResponse, QuestionResponse, SurveyType, QuestionType
from app.crm.models.customer import Customer
from app.db.base_class import Base

class TestSurveyService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی تست"""
        self.engine = create_engine('sqlite:///test.db')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.service = SurveyService(self.session)
        
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

    def test_create_survey(self):
        """تست ایجاد نظرسنجی"""
        questions = [
            {
                "text": "نظر شما درباره خدمات ما چیست؟",
                "type": QuestionType.RATING,
                "required": True
            },
            {
                "text": "کدام ویژگی‌ها را بیشتر می‌پسندید؟",
                "type": QuestionType.MULTIPLE_CHOICE,
                "options": ["کیفیت", "قیمت", "سرعت", "پشتیبانی"],
                "required": True
            }
        ]

        survey = self.service.create_survey(
            title="نظرسنجی رضایت مشتری",
            description="لطفاً به سوالات زیر پاسخ دهید",
            survey_type=SurveyType.CUSTOMER_SATISFACTION,
            questions=questions
        )

        self.assertIsInstance(survey, Survey)
        self.assertEqual(survey.title, "نظرسنجی رضایت مشتری")
        self.assertEqual(len(survey.questions), 2)

    def test_submit_response(self):
        """تست ثبت پاسخ نظرسنجی"""
        # ایجاد نظرسنجی تست
        questions = [
            {
                "text": "نظر شما درباره خدمات ما چیست؟",
                "type": QuestionType.RATING,
                "required": True
            }
        ]

        survey = self.service.create_survey(
            title="نظرسنجی تست",
            description="تست",
            survey_type=SurveyType.CUSTOMER_SATISFACTION,
            questions=questions
        )

        # ثبت پاسخ
        answers = [
            {
                "question_id": survey.questions[0].id,
                "answer": "5"
            }
        ]

        response = self.service.submit_response(
            survey_id=survey.id,
            customer_id=self.customer.id,
            answers=answers
        )

        self.assertIsInstance(response, SurveyResponse)
        self.assertEqual(response.survey_id, survey.id)
        self.assertEqual(response.customer_id, self.customer.id)
        self.assertEqual(len(response.answers), 1)

    def test_get_survey_responses(self):
        """تست دریافت پاسخ‌های نظرسنجی"""
        # ایجاد نظرسنجی و پاسخ‌های تست
        questions = [
            {
                "text": "نظر شما چیست؟",
                "type": QuestionType.RATING,
                "required": True
            }
        ]

        survey = self.service.create_survey(
            title="نظرسنجی تست",
            description="تست",
            survey_type=SurveyType.CUSTOMER_SATISFACTION,
            questions=questions
        )

        # ثبت چند پاسخ
        for i in range(3):
            answers = [
                {
                    "question_id": survey.questions[0].id,
                    "answer": str(i + 1)
                }
            ]
            self.service.submit_response(
                survey_id=survey.id,
                customer_id=self.customer.id,
                answers=answers
            )

        responses = self.service.get_survey_responses(survey.id)
        self.assertEqual(len(responses), 3)

    def test_get_customer_surveys(self):
        """تست دریافت نظرسنجی‌های مشتری"""
        # ایجاد چند نظرسنجی
        for i in range(3):
            questions = [
                {
                    "text": f"سوال تست {i}",
                    "type": QuestionType.RATING,
                    "required": True
                }
            ]
            survey = self.service.create_survey(
                title=f"نظرسنجی تست {i}",
                description="تست",
                survey_type=SurveyType.CUSTOMER_SATISFACTION,
                questions=questions
            )

            # ثبت پاسخ برای یکی از نظرسنجی‌ها
            if i == 1:
                answers = [
                    {
                        "question_id": survey.questions[0].id,
                        "answer": "5"
                    }
                ]
                self.service.submit_response(
                    survey_id=survey.id,
                    customer_id=self.customer.id,
                    answers=answers
                )

        # دریافت همه نظرسنجی‌ها
        all_surveys = self.service.get_customer_surveys(self.customer.id)
        self.assertEqual(len(all_surveys), 3)

        # دریافت فقط نظرسنجی‌های تکمیل شده
        completed_surveys = self.service.get_customer_surveys(
            self.customer.id,
            completed_only=True
        )
        self.assertEqual(len(completed_surveys), 1)

    def test_get_survey_statistics(self):
        """تست دریافت آمار نظرسنجی"""
        # ایجاد نظرسنجی تست
        questions = [
            {
                "text": "نظر شما چیست؟",
                "type": QuestionType.RATING,
                "required": True
            },
            {
                "text": "کدام گزینه را انتخاب می‌کنید؟",
                "type": QuestionType.SINGLE_CHOICE,
                "options": ["گزینه 1", "گزینه 2", "گزینه 3"],
                "required": True
            }
        ]

        survey = self.service.create_survey(
            title="نظرسنجی تست",
            description="تست",
            survey_type=SurveyType.CUSTOMER_SATISFACTION,
            questions=questions
        )

        # ثبت چند پاسخ
        for i in range(3):
            answers = [
                {
                    "question_id": survey.questions[0].id,
                    "answer": "5"
                },
                {
                    "question_id": survey.questions[1].id,
                    "answer": "گزینه 1"
                }
            ]
            self.service.submit_response(
                survey_id=survey.id,
                customer_id=self.customer.id,
                answers=answers
            )

        stats = self.service.get_survey_statistics(survey.id)
        
        self.assertEqual(stats["total_responses"], 3)
        self.assertEqual(stats["completion_rate"], 1.0)
        self.assertIn("question_stats", stats)
        self.assertEqual(len(stats["question_stats"]), 2)

if __name__ == '__main__':
    unittest.main() 