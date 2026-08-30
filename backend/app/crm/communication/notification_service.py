import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.crm.models import Customer, Notification, NotificationType, NotificationChannel
from app.core.config import settings
from app.core.email import send_email
from app.core.sms import send_sms
from app.core.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, customer_id: int, title: str, content: str, 
                          notification_type: NotificationType,
                          channels: List[NotificationChannel]) -> Notification:
        """ایجاد نوتیفیکیشن جدید"""
        try:
            notification = Notification(
                customer_id=customer_id,
                title=title,
                content=content,
                type=notification_type,
                channels=channels,
                status="pending",
                created_at=datetime.utcnow()
            )
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            
            # ارسال نوتیفیکیشن از طریق کانال‌های مشخص شده
            self._send_notification(notification)
            
            return notification
        except Exception as e:
            logger.error(f"خطا در ایجاد نوتیفیکیشن: {str(e)}")
            self.db.rollback()
            raise

    def _send_notification(self, notification: Notification) -> bool:
        """ارسال نوتیفیکیشن از طریق کانال‌های مشخص شده"""
        try:
            customer = self.db.query(Customer).filter(
                Customer.id == notification.customer_id
            ).first()
            
            if not customer:
                return False

            success = True
            for channel in notification.channels:
                try:
                    if channel == NotificationChannel.EMAIL:
                        success &= send_email(
                            to_email=customer.email,
                            subject=notification.title,
                            content=notification.content
                        )
                    elif channel == NotificationChannel.SMS:
                        success &= send_sms(
                            to_number=customer.mobile,
                            message=notification.content
                        )
                    elif channel == NotificationChannel.WHATSAPP:
                        success &= send_whatsapp_message(
                            to_number=customer.mobile,
                            message=notification.content
                        )
                    elif channel == NotificationChannel.IN_APP:
                        # نوتیفیکیشن درون برنامه‌ای نیازی به ارسال ندارد
                        pass
                except Exception as e:
                    logger.error(f"خطا در ارسال نوتیفیکیشن از طریق {channel}: {str(e)}")
                    success = False

            # بروزرسانی وضعیت نوتیفیکیشن
            notification.status = "sent" if success else "failed"
            notification.sent_at = datetime.utcnow() if success else None
            self.db.commit()

            return success
        except Exception as e:
            logger.error(f"خطا در ارسال نوتیفیکیشن: {str(e)}")
            return False

    def get_customer_notifications(self, customer_id: int, 
                                unread_only: bool = False) -> List[Notification]:
        """دریافت نوتیفیکیشن‌های مشتری"""
        try:
            query = self.db.query(Notification).filter(
                Notification.customer_id == customer_id
            )
            
            if unread_only:
                query = query.filter(Notification.is_read == False)
                
            return query.order_by(Notification.created_at.desc()).all()
        except Exception as e:
            logger.error(f"خطا در دریافت نوتیفیکیشن‌های مشتری: {str(e)}")
            raise

    def mark_as_read(self, notification_id: int) -> bool:
        """علامت‌گذاری نوتیفیکیشن به عنوان خوانده شده"""
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"خطا در علامت‌گذاری نوتیفیکیشن: {str(e)}")
            self.db.rollback()
            raise

    def get_notification_statistics(self, start_date: datetime, 
                                  end_date: datetime) -> Dict:
        """دریافت آمار نوتیفیکیشن‌ها"""
        try:
            notifications = self.db.query(Notification).filter(
                Notification.created_at.between(start_date, end_date)
            ).all()
            
            stats = {
                "total": len(notifications),
                "sent": len([n for n in notifications if n.status == "sent"]),
                "failed": len([n for n in notifications if n.status == "failed"]),
                "read": len([n for n in notifications if n.is_read]),
                "unread": len([n for n in notifications if not n.is_read]),
                "by_type": {},
                "by_channel": {}
            }
            
            # آمار بر اساس نوع نوتیفیکیشن
            for notification in notifications:
                stats["by_type"][notification.type] = stats["by_type"].get(
                    notification.type, 0) + 1
                
                # آمار بر اساس کانال
                for channel in notification.channels:
                    stats["by_channel"][channel] = stats["by_channel"].get(
                        channel, 0) + 1
            
            return stats
        except Exception as e:
            logger.error(f"خطا در دریافت آمار نوتیفیکیشن‌ها: {str(e)}")
            raise 