from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum

class ChatSessionStatus(str, enum.Enum):
    ACTIVE = "active"
    ENDED = "ended"
    WAITING = "waiting"

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(Enum(ChatSessionStatus), default=ChatSessionStatus.ACTIVE)
    assigned_to = Column(String, default="bot")  # bot or human
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    last_message_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    content = Column(Text)
    sender_type = Column(String)  # customer or agent
    created_at = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float, nullable=True)
    is_read = Column(Boolean, default=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages") 