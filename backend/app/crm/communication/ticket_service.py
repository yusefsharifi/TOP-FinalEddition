import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.crm.models import Customer, Ticket, TicketMessage, TicketStatus, TicketPriority
from app.core.config import settings

logger = logging.getLogger(__name__)

class TicketService:
    def __init__(self, db: Session):
        self.db = db

    def create_ticket(self, customer_id: int, subject: str, description: str, priority: TicketPriority = TicketPriority.MEDIUM) -> Ticket:
        """ایجاد تیکت جدید"""
        try:
            ticket = Ticket(
                customer_id=customer_id,
                subject=subject,
                description=description,
                priority=priority,
                status=TicketStatus.OPEN,
                created_at=datetime.utcnow()
            )
            self.db.add(ticket)
            self.db.commit()
            self.db.refresh(ticket)
            return ticket
        except Exception as e:
            logger.error(f"خطا در ایجاد تیکت: {str(e)}")
            self.db.rollback()
            raise

    def add_message(self, ticket_id: int, content: str, sender_type: str) -> TicketMessage:
        """افزودن پیام به تیکت"""
        try:
            message = TicketMessage(
                ticket_id=ticket_id,
                content=content,
                sender_type=sender_type,
                created_at=datetime.utcnow()
            )
            self.db.add(message)
            
            # بروزرسانی وضعیت تیکت
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket:
                ticket.last_updated = datetime.utcnow()
                if sender_type == "agent":
                    ticket.status = TicketStatus.IN_PROGRESS
            
            self.db.commit()
            self.db.refresh(message)
            return message
        except Exception as e:
            logger.error(f"خطا در افزودن پیام: {str(e)}")
            self.db.rollback()
            raise

    def update_ticket_status(self, ticket_id: int, status: TicketStatus) -> bool:
        """بروزرسانی وضعیت تیکت"""
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket:
                ticket.status = status
                ticket.last_updated = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"خطا در بروزرسانی وضعیت تیکت: {str(e)}")
            self.db.rollback()
            raise

    def assign_ticket(self, ticket_id: int, agent_id: int) -> bool:
        """اختصاص تیکت به اپراتور"""
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket:
                ticket.assigned_to = agent_id
                ticket.last_updated = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"خطا در اختصاص تیکت: {str(e)}")
            self.db.rollback()
            raise

    def get_ticket_messages(self, ticket_id: int) -> List[TicketMessage]:
        """دریافت پیام‌های تیکت"""
        try:
            return self.db.query(TicketMessage).filter(
                TicketMessage.ticket_id == ticket_id
            ).order_by(TicketMessage.created_at).all()
        except Exception as e:
            logger.error(f"خطا در دریافت پیام‌های تیکت: {str(e)}")
            raise

    def get_customer_tickets(self, customer_id: int) -> List[Ticket]:
        """دریافت تیکت‌های مشتری"""
        try:
            return self.db.query(Ticket).filter(
                Ticket.customer_id == customer_id
            ).order_by(Ticket.created_at.desc()).all()
        except Exception as e:
            logger.error(f"خطا در دریافت تیکت‌های مشتری: {str(e)}")
            raise

    def get_agent_tickets(self, agent_id: int, status: Optional[TicketStatus] = None) -> List[Ticket]:
        """دریافت تیکت‌های اپراتور"""
        try:
            query = self.db.query(Ticket).filter(Ticket.assigned_to == agent_id)
            if status:
                query = query.filter(Ticket.status == status)
            return query.order_by(Ticket.priority.desc(), Ticket.created_at.desc()).all()
        except Exception as e:
            logger.error(f"خطا در دریافت تیکت‌های اپراتور: {str(e)}")
            raise

    def get_ticket_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """دریافت آمار تیکت‌ها"""
        try:
            tickets = self.db.query(Ticket).filter(
                Ticket.created_at.between(start_date, end_date)
            ).all()
            
            stats = {
                "total": len(tickets),
                "open": len([t for t in tickets if t.status == TicketStatus.OPEN]),
                "in_progress": len([t for t in tickets if t.status == TicketStatus.IN_PROGRESS]),
                "resolved": len([t for t in tickets if t.status == TicketStatus.RESOLVED]),
                "closed": len([t for t in tickets if t.status == TicketStatus.CLOSED]),
                "high_priority": len([t for t in tickets if t.priority == TicketPriority.HIGH]),
                "medium_priority": len([t for t in tickets if t.priority == TicketPriority.MEDIUM]),
                "low_priority": len([t for t in tickets if t.priority == TicketPriority.LOW])
            }
            
            return stats
        except Exception as e:
            logger.error(f"خطا در دریافت آمار تیکت‌ها: {str(e)}")
            raise 