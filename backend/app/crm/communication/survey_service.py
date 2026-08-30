import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.crm.models.survey import Survey, SurveyQuestion, SurveyResponse, QuestionResponse, SurveyType, QuestionType
from app.core.config import settings

logger = logging.getLogger(__name__)

class SurveyService:
    def __init__(self, db: Session):
        self.db = db

    def create_survey(self, title: str, description: str, survey_type: SurveyType,
                     questions: List[Dict], start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> Survey:
        """ایجاد نظرسنجی جدید"""
        try:
            survey = Survey(
                title=title,
                description=description,
                type=survey_type,
                start_date=start_date or datetime.utcnow(),
                end_date=end_date
            )
            self.db.add(survey)
            self.db.commit()
            self.db.refresh(survey)

            # افزودن سوالات نظرسنجی
            for i, question_data in enumerate(questions):
                question = SurveyQuestion(
                    survey_id=survey.id,
                    question_text=question_data["text"],
                    question_type=question_data["type"],
                    options=question_data.get("options", []),
                    is_required=question_data.get("required", True),
                    order=i
                )
                self.db.add(question)

            self.db.commit()
            return survey
        except Exception as e:
            logger.error(f"خطا در ایجاد نظرسنجی: {str(e)}")
            self.db.rollback()
            raise

    def submit_response(self, survey_id: int, customer_id: int, 
                       answers: List[Dict]) -> SurveyResponse:
        """ثبت پاسخ نظرسنجی"""
        try:
            response = SurveyResponse(
                survey_id=survey_id,
                customer_id=customer_id,
                submitted_at=datetime.utcnow()
            )
            self.db.add(response)
            self.db.commit()
            self.db.refresh(response)

            # ثبت پاسخ‌ها
            for answer in answers:
                question = self.db.query(SurveyQuestion).filter(
                    SurveyQuestion.id == answer["question_id"]
                ).first()
                
                if question:
                    question_response = QuestionResponse(
                        response_id=response.id,
                        question_id=question.id,
                        answer=answer["answer"]
                    )
                    self.db.add(question_response)

            self.db.commit()
            return response
        except Exception as e:
            logger.error(f"خطا در ثبت پاسخ نظرسنجی: {str(e)}")
            self.db.rollback()
            raise

    def get_survey_responses(self, survey_id: int) -> List[SurveyResponse]:
        """دریافت پاسخ‌های نظرسنجی"""
        try:
            return self.db.query(SurveyResponse).filter(
                SurveyResponse.survey_id == survey_id
            ).order_by(SurveyResponse.submitted_at.desc()).all()
        except Exception as e:
            logger.error(f"خطا در دریافت پاسخ‌های نظرسنجی: {str(e)}")
            raise

    def get_customer_surveys(self, customer_id: int, 
                           completed_only: bool = False) -> List[Survey]:
        """دریافت نظرسنجی‌های مشتری"""
        try:
            query = self.db.query(Survey).join(
                SurveyResponse,
                Survey.id == SurveyResponse.survey_id
            ).filter(SurveyResponse.customer_id == customer_id)

            if completed_only:
                query = query.filter(SurveyResponse.submitted_at.isnot(None))

            return query.order_by(Survey.created_at.desc()).all()
        except Exception as e:
            logger.error(f"خطا در دریافت نظرسنجی‌های مشتری: {str(e)}")
            raise

    def get_survey_statistics(self, survey_id: int) -> Dict:
        """دریافت آمار نظرسنجی"""
        try:
            survey = self.db.query(Survey).filter(Survey.id == survey_id).first()
            if not survey:
                return {"error": "نظرسنجی یافت نشد"}

            responses = self.get_survey_responses(survey_id)
            
            stats = {
                "total_responses": len(responses),
                "completion_rate": len(responses) / survey.total_questions if survey.total_questions > 0 else 0,
                "average_score": sum(r.score for r in responses) / len(responses) if responses else 0,
                "question_stats": {}
            }

            # آمار برای هر سوال
            for question in survey.questions:
                question_responses = [r for r in responses if r.question_id == question.id]
                stats["question_stats"][question.id] = {
                    "total_answers": len(question_responses),
                    "average_score": sum(r.score for r in question_responses) / len(question_responses) if question_responses else 0,
                    "answer_distribution": {}
                }

                # توزیع پاسخ‌ها برای سوالات چند گزینه‌ای
                if question.question_type in ["multiple_choice", "single_choice"]:
                    for option in question.options:
                        count = len([r for r in question_responses if r.answer == option])
                        stats["question_stats"][question.id]["answer_distribution"][option] = count

            return stats
        except Exception as e:
            logger.error(f"خطا در دریافت آمار نظرسنجی: {str(e)}")
            raise

    def analyze_sentiment(self, survey_id: int) -> Dict:
        """تحلیل احساسات پاسخ‌های نظرسنجی"""
        try:
            responses = self.get_survey_responses(survey_id)
            
            # جمع‌آوری متن‌های پاسخ‌ها
            texts = []
            for response in responses:
                for answer in response.answers:
                    if isinstance(answer.answer, str):
                        texts.append(answer.answer)

            # TODO: پیاده‌سازی تحلیل احساسات با استفاده از مدل‌های NLP
            sentiment_analysis = {
                "positive": 0.6,
                "neutral": 0.3,
                "negative": 0.1,
                "keywords": ["خوب", "عالی", "ممنون", "بد", "ضعیف"]
            }

            return sentiment_analysis
        except Exception as e:
            logger.error(f"خطا در تحلیل احساسات نظرسنجی: {str(e)}")
            raise

    def get_survey(self, survey_id: int) -> Optional[Survey]:
        """دریافت اطلاعات نظرسنجی"""
        try:
            return self.db.query(Survey).filter(Survey.id == survey_id).first()
        except Exception as e:
            logger.error(f"خطا در دریافت نظرسنجی: {str(e)}")
            raise 