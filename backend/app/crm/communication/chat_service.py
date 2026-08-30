import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.crm.models import Customer, ChatMessage, ChatSession
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_chat_session(self, customer_id: int) -> ChatSession:
        """ایجاد یک جلسه چت جدید"""
        try:
            session = ChatSession(
                customer_id=customer_id,
                status="active",
                created_at=datetime.utcnow()
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session
        except Exception as e:
            logger.error(f"خطا در ایجاد جلسه چت: {str(e)}")
            self.db.rollback()
            raise

    def send_message(self, session_id: int, content: str, sender_type: str) -> ChatMessage:
        """ارسال پیام در چت"""
        try:
            message = ChatMessage(
                session_id=session_id,
                content=content,
                sender_type=sender_type,
                created_at=datetime.utcnow()
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        except Exception as e:
            logger.error(f"خطا در ارسال پیام: {str(e)}")
            self.db.rollback()
            raise

    def get_session_messages(self, session_id: int) -> List[ChatMessage]:
        """دریافت پیام‌های یک جلسه چت"""
        try:
            return self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).all()
        except Exception as e:
            logger.error(f"خطا در دریافت پیام‌ها: {str(e)}")
            raise

    def end_session(self, session_id: int) -> bool:
        """پایان دادن به جلسه چت"""
        try:
            session = self.db.query(ChatSession).filter(
                ChatSession.id == session_id
            ).first()
            if session:
                session.status = "ended"
                session.ended_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"خطا در پایان دادن به جلسه: {str(e)}")
            self.db.rollback()
            raise

    def transfer_to_human(self, session_id: int) -> bool:
        """انتقال به اپراتور انسانی"""
        try:
            session = self.db.query(ChatSession).filter(
                ChatSession.id == session_id
            ).first()
            if session:
                session.assigned_to = "human"
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"خطا در انتقال به اپراتور: {str(e)}")
            self.db.rollback()
            raise

    def get_active_sessions(self) -> List[ChatSession]:
        """دریافت جلسات فعال"""
        try:
            return self.db.query(ChatSession).filter(
                ChatSession.status == "active"
            ).all()
        except Exception as e:
            logger.error(f"خطا در دریافت جلسات فعال: {str(e)}")
            raise

    def analyze_sentiment(self, message_id: int) -> Dict:
        """تحلیل احساسات پیام"""
        try:
            message = self.db.query(ChatMessage).filter(
                ChatMessage.id == message_id
            ).first()
            if not message:
                return {"error": "پیام یافت نشد"}

            # TODO: پیاده‌سازی تحلیل احساسات با استفاده از مدل‌های NLP
            return {
                "sentiment": "positive",
                "confidence": 0.85,
                "keywords": ["خوب", "عالی", "ممنون"]
            }
        except Exception as e:
            logger.error(f"خطا در تحلیل احساسات: {str(e)}")
            raise 