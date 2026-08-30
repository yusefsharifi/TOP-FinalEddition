from app.core.test_manager import DynamicTestManager
from app.crm.communication.survey_service import SurveyService
from app.crm.models.survey import SurveyType, QuestionType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base

def setup_test_environment():
    """راه‌اندازی محیط تست"""
    engine = create_engine('sqlite:///test.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    return session

def create_test_survey(service: SurveyService):
    """ایجاد یک نظرسنجی تست"""
    questions = [
        {
            "text": "نظر شما درباره خدمات ما چیست؟",
            "type": QuestionType.RATING,
            "required": True
        }
    ]
    
    return service.create_survey(
        title="نظرسنجی تست",
        description="تست",
        survey_type=SurveyType.CUSTOMER_SATISFACTION,
        questions=questions
    )

def test_create_survey(service: SurveyService):
    """تست ایجاد نظرسنجی"""
    survey = create_test_survey(service)
    assert isinstance(survey, Survey)
    assert survey.title == "نظرسنجی تست"
    assert len(survey.questions) == 1
    return {"survey_id": survey.id}

def test_submit_response(service: SurveyService):
    """تست ثبت پاسخ نظرسنجی"""
    survey = create_test_survey(service)
    answers = [
        {
            "question_id": survey.questions[0].id,
            "answer": "5"
        }
    ]
    
    response = service.submit_response(
        survey_id=survey.id,
        customer_id=1,  # ID مشتری تست
        answers=answers
    )
    
    assert response.survey_id == survey.id
    assert response.customer_id == 1
    assert len(response.answers) == 1
    return {"response_id": response.id}

def load_survey_tests(test_manager: DynamicTestManager, service: SurveyService):
    """بارگذاری تست‌های نظرسنجی"""
    test_manager.add_test_case(
        category="survey",
        test_name="test_create_survey",
        test_func=lambda: test_create_survey(service),
        description="تست ایجاد نظرسنجی جدید",
        tags=["survey", "create"]
    )
    
    test_manager.add_test_case(
        category="survey",
        test_name="test_submit_response",
        test_func=lambda: test_submit_response(service),
        description="تست ثبت پاسخ نظرسنجی",
        tags=["survey", "response"]
    )

def main():
    """تابع اصلی برای اجرای تست‌ها"""
    # راه‌اندازی محیط تست
    session = setup_test_environment()
    service = SurveyService(session)
    
    # ایجاد مدیر تست
    test_manager = DynamicTestManager()
    
    # بارگذاری تست‌ها
    load_survey_tests(test_manager, service)
    
    # اجرای تست‌ها
    print("اجرای تست‌های نظرسنجی...")
    results = test_manager.run_category_tests("survey")
    
    # نمایش نتایج
    print("\nنتایج تست‌ها:")
    for result in results:
        print(f"\nتست: {result['name']}")
        print(f"وضعیت: {result['status']}")
        if result['status'] == 'success':
            print(f"نتیجه: {result['result']}")
        else:
            print(f"خطا: {result['error']}")
    
    # نمایش آمار
    stats = test_manager.get_test_statistics()
    print("\nآمار تست‌ها:")
    print(f"تعداد کل تست‌ها: {stats['total_tests']}")
    print(f"تعداد نتایج: {stats['total_results']}")
    print(f"تست‌های موفق: {stats['success_count']}")
    print(f"تست‌های ناموفق: {stats['error_count']}")
    print(f"درصد موفقیت: {stats['success_rate']:.2f}%")

if __name__ == "__main__":
    main() 