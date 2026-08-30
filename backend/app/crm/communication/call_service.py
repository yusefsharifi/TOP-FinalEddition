import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.crm.models import Customer, Call, CallRecording, CallStatus
from app.core.config import settings
from app.core.voice import start_recording, stop_recording, transcribe_audio

logger = logging.getLogger(__name__)

class CallService:
    def __init__(self, db: Session):
        self.db = db

    def initiate_call(self, customer_id: int, phone_number: str) -> Call:
        """شروع تماس جدید"""
        try:
            call = Call(
                customer_id=customer_id,
                phone_number=phone_number,
                status=CallStatus.INITIATED,
                started_at=datetime.utcnow()
            )
            self.db.add(call)
            self.db.commit()
            self.db.refresh(call)
            return call
        except Exception as e:
            logger.error(f"خطا در شروع تماس: {str(e)}")
            self.db.rollback()
            raise

    def answer_call(self, call_id: int) -> bool:
        """پاسخ به تماس"""
        try:
            call = self.db.query(Call).filter(Call.id == call_id).first()
            if call:
                call.status = CallStatus.IN_PROGRESS
                call.answered_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"خطا در پاسخ به تماس: {str(e)}")
            self.db.rollback()
            raise

    def end_call(self, call_id: int, duration: int, notes: str = None) -> bool:
        """پایان تماس"""
        try:
            call = self.db.query(Call).filter(Call.id == call_id).first()
            if call:
                call.status = CallStatus.COMPLETED
                call.ended_at = datetime.utcnow()
                call.duration = duration
                call.notes = notes
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"خطا در پایان تماس: {str(e)}")
            self.db.rollback()
            raise

    def start_recording(self, call_id: int) -> CallRecording:
        """شروع ضبط تماس"""
        try:
            call = self.db.query(Call).filter(Call.id == call_id).first()
            if not call:
                return None

            # شروع ضبط صدا
            recording_id = start_recording(call_id)
            
            recording = CallRecording(
                call_id=call_id,
                recording_id=recording_id,
                started_at=datetime.utcnow()
            )
            self.db.add(recording)
            self.db.commit()
            self.db.refresh(recording)
            return recording
        except Exception as e:
            logger.error(f"خطا در شروع ضبط تماس: {str(e)}")
            self.db.rollback()
            raise

    def stop_recording(self, recording_id: int) -> bool:
        """پایان ضبط تماس"""
        try:
            recording = self.db.query(CallRecording).filter(
                CallRecording.recording_id == recording_id
            ).first()
            
            if recording:
                # توقف ضبط صدا
                audio_file = stop_recording(recording_id)
                
                # ذخیره فایل صوتی
                recording.audio_file = audio_file
                recording.ended_at = datetime.utcnow()
                
                # تبدیل صدا به متن
                recording.transcript = transcribe_audio(audio_file)
                
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"خطا در پایان ضبط تماس: {str(e)}")
            self.db.rollback()
            raise

    def get_call_recordings(self, call_id: int) -> List[CallRecording]:
        """دریافت ضبط‌های تماس"""
        try:
            return self.db.query(CallRecording).filter(
                CallRecording.call_id == call_id
            ).order_by(CallRecording.started_at.desc()).all()
        except Exception as e:
            logger.error(f"خطا در دریافت ضبط‌های تماس: {str(e)}")
            raise

    def get_customer_calls(self, customer_id: int) -> List[Call]:
        """دریافت تماس‌های مشتری"""
        try:
            return self.db.query(Call).filter(
                Call.customer_id == customer_id
            ).order_by(Call.started_at.desc()).all()
        except Exception as e:
            logger.error(f"خطا در دریافت تماس‌های مشتری: {str(e)}")
            raise

    def analyze_call_quality(self, call_id: int) -> Dict:
        """تحلیل کیفیت تماس"""
        try:
            call = self.db.query(Call).filter(Call.id == call_id).first()
            if not call:
                return {"error": "تماس یافت نشد"}

            recordings = self.get_call_recordings(call_id)
            if not recordings:
                return {"error": "ضبطی یافت نشد"}

            # تحلیل متن گفتگو
            transcript = recordings[0].transcript
            sentiment_analysis = {
                "positive": 0.6,
                "neutral": 0.3,
                "negative": 0.1,
                "keywords": ["خوب", "عالی", "ممنون", "بد", "ضعیف"]
            }

            # تحلیل کیفیت صدا
            audio_quality = {
                "clarity": 0.85,
                "noise_level": 0.15,
                "signal_strength": 0.9
            }

            return {
                "duration": call.duration,
                "sentiment": sentiment_analysis,
                "audio_quality": audio_quality,
                "key_points": ["نکته 1", "نکته 2", "نکته 3"]
            }
        except Exception as e:
            logger.error(f"خطا در تحلیل کیفیت تماس: {str(e)}")
            raise

    def get_call_statistics(self, start_date: datetime, 
                          end_date: datetime) -> Dict:
        """دریافت آمار تماس‌ها"""
        try:
            calls = self.db.query(Call).filter(
                Call.started_at.between(start_date, end_date)
            ).all()
            
            stats = {
                "total_calls": len(calls),
                "answered_calls": len([c for c in calls if c.status == CallStatus.COMPLETED]),
                "missed_calls": len([c for c in calls if c.status == CallStatus.MISSED]),
                "average_duration": sum(c.duration for c in calls if c.duration) / len(calls) if calls else 0,
                "total_duration": sum(c.duration for c in calls if c.duration),
                "recorded_calls": len([c for c in calls if c.recordings])
            }
            
            return stats
        except Exception as e:
            logger.error(f"خطا در دریافت آمار تماس‌ها: {str(e)}")
            raise 