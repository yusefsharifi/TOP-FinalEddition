from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum

class CallStatus(str, enum.Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"
    FAILED = "failed"

class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    phone_number = Column(String(20))
    status = Column(Enum(CallStatus), default=CallStatus.INITIATED)
    duration = Column(Integer, nullable=True)  # مدت زمان تماس به ثانیه
    notes = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    quality_score = Column(Float, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="calls")
    recordings = relationship("CallRecording", back_populates="call")

class CallRecording(Base):
    __tablename__ = "call_recordings"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"))
    recording_id = Column(String(100))  # شناسه ضبط در سیستم تلفنی
    audio_file = Column(String(255), nullable=True)  # مسیر فایل صوتی
    transcript = Column(Text, nullable=True)  # متن گفتگو
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # مدت زمان ضبط به ثانیه
    quality_score = Column(Float, nullable=True)

    # Relationships
    call = relationship("Call", back_populates="recordings") 