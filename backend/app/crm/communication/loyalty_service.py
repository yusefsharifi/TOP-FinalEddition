import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.crm.models.loyalty import (
    CustomerMembership, PointTransaction, Reward, CustomerReward,
    MembershipTier, PointTransactionType, RewardStatus
)

logger = logging.getLogger(__name__)

class LoyaltyService:
    def __init__(self, db: Session):
        self.db = db

    def enroll_customer(self, customer_id: int, tier: MembershipTier = MembershipTier.BRONZE) -> CustomerMembership:
        """ثبت نام مشتری در باشگاه"""
        try:
            membership = CustomerMembership(
                customer_id=customer_id,
                tier=tier
            )
            self.db.add(membership)
            self.db.commit()
            self.db.refresh(membership)
            
            # ثبت تراکنش امتیاز خوش‌آمدگویی
            self.add_points(
                membership_id=membership.id,
                points=100,  # امتیاز خوش‌آمدگویی
                transaction_type=PointTransactionType.EARN,
                description="امتیاز خوش‌آمدگویی به باشگاه مشتریان"
            )
            
            return membership
        except Exception as e:
            logger.error(f"خطا در ثبت نام مشتری در باشگاه: {str(e)}")
            self.db.rollback()
            raise

    def add_points(self, membership_id: int, points: int, 
                  transaction_type: PointTransactionType,
                  description: str, reference_id: str = None,
                  metadata: Dict = None) -> PointTransaction:
        """افزودن امتیاز به حساب مشتری"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.id == membership_id
            ).first()
            
            if not membership:
                raise ValueError("عضویت یافت نشد")
            
            transaction = PointTransaction(
                membership_id=membership_id,
                transaction_type=transaction_type,
                points=points,
                description=description,
                reference_id=reference_id,
                metadata=metadata
            )
            
            # به‌روزرسانی موجودی امتیاز
            if transaction_type == PointTransactionType.EARN:
                membership.points_balance += points
                membership.total_points_earned += points
            elif transaction_type == PointTransactionType.REDEEM:
                if membership.points_balance < points:
                    raise ValueError("موجودی امتیاز کافی نیست")
                membership.points_balance -= points
                membership.total_points_redeemed += points
            
            membership.last_activity_at = datetime.utcnow()
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            # بررسی ارتقای سطح عضویت
            self._check_tier_upgrade(membership)
            
            return transaction
        except Exception as e:
            logger.error(f"خطا در افزودن امتیاز: {str(e)}")
            self.db.rollback()
            raise

    def _check_tier_upgrade(self, membership: CustomerMembership) -> None:
        """بررسی شرایط ارتقای سطح عضویت"""
        current_tier = membership.tier
        points = membership.total_points_earned
        
        # شرایط ارتقای سطح
        if points >= 10000 and current_tier == MembershipTier.BRONZE:
            membership.tier = MembershipTier.SILVER
        elif points >= 25000 and current_tier == MembershipTier.SILVER:
            membership.tier = MembershipTier.GOLD
        elif points >= 50000 and current_tier == MembershipTier.GOLD:
            membership.tier = MembershipTier.PLATINUM

    def create_reward(self, name: str, description: str, points_cost: int,
                     start_date: datetime, end_date: datetime = None,
                     quantity_available: int = None, metadata: Dict = None) -> Reward:
        """ایجاد پاداش جدید"""
        try:
            reward = Reward(
                name=name,
                description=description,
                points_cost=points_cost,
                start_date=start_date,
                end_date=end_date,
                quantity_available=quantity_available,
                metadata=metadata
            )
            self.db.add(reward)
            self.db.commit()
            self.db.refresh(reward)
            return reward
        except Exception as e:
            logger.error(f"خطا در ایجاد پاداش: {str(e)}")
            self.db.rollback()
            raise

    def redeem_reward(self, membership_id: int, reward_id: int) -> CustomerReward:
        """استفاده از پاداش"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.id == membership_id
            ).first()
            
            reward = self.db.query(Reward).filter(
                Reward.id == reward_id,
                Reward.is_active == True
            ).first()
            
            if not membership or not reward:
                raise ValueError("عضویت یا پاداش یافت نشد")
            
            # بررسی موجودی پاداش
            if reward.quantity_available is not None and reward.quantity_available <= 0:
                raise ValueError("موجودی پاداش به پایان رسیده است")
            
            # بررسی تاریخ اعتبار
            if reward.end_date and reward.end_date < datetime.utcnow():
                raise ValueError("تاریخ اعتبار پاداش به پایان رسیده است")
            
            # بررسی موجودی امتیاز
            if membership.points_balance < reward.points_cost:
                raise ValueError("موجودی امتیاز کافی نیست")
            
            # ثبت پاداش مشتری
            customer_reward = CustomerReward(
                membership_id=membership_id,
                reward_id=reward_id,
                points_spent=reward.points_cost,
                expires_at=datetime.utcnow() + timedelta(days=30)  # اعتبار 30 روزه
            )
            
            # به‌روزرسانی موجودی پاداش
            if reward.quantity_available is not None:
                reward.quantity_available -= 1
            
            # کسر امتیاز
            self.add_points(
                membership_id=membership_id,
                points=reward.points_cost,
                transaction_type=PointTransactionType.REDEEM,
                description=f"استفاده از پاداش: {reward.name}",
                metadata={"reward_id": reward_id}
            )
            
            self.db.add(customer_reward)
            self.db.commit()
            self.db.refresh(customer_reward)
            
            return customer_reward
        except Exception as e:
            logger.error(f"خطا در استفاده از پاداش: {str(e)}")
            self.db.rollback()
            raise

    def get_membership_status(self, customer_id: int) -> Dict:
        """دریافت وضعیت عضویت مشتری"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.customer_id == customer_id
            ).first()
            
            if not membership:
                return {"status": "not_enrolled"}
            
            return {
                "status": "active",
                "tier": membership.tier,
                "points_balance": membership.points_balance,
                "total_points_earned": membership.total_points_earned,
                "total_points_redeemed": membership.total_points_redeemed,
                "joined_at": membership.joined_at,
                "last_activity_at": membership.last_activity_at
            }
        except Exception as e:
            logger.error(f"خطا در دریافت وضعیت عضویت: {str(e)}")
            raise

    def get_available_rewards(self, membership_id: int) -> List[Dict]:
        """دریافت لیست پاداش‌های قابل استفاده"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.id == membership_id
            ).first()
            
            if not membership:
                raise ValueError("عضویت یافت نشد")
            
            available_rewards = self.db.query(Reward).filter(
                Reward.is_active == True,
                Reward.start_date <= datetime.utcnow(),
                (Reward.end_date.is_(None) | (Reward.end_date > datetime.utcnow())),
                (Reward.quantity_available.is_(None) | (Reward.quantity_available > 0))
            ).all()
            
            return [{
                "id": reward.id,
                "name": reward.name,
                "description": reward.description,
                "points_cost": reward.points_cost,
                "available_quantity": reward.quantity_available,
                "expires_at": reward.end_date
            } for reward in available_rewards]
        except Exception as e:
            logger.error(f"خطا در دریافت لیست پاداش‌ها: {str(e)}")
            raise

    def get_membership_history(self, customer_id: int, 
                             start_date: datetime = None,
                             end_date: datetime = None) -> Dict:
        """دریافت تاریخچه عضویت مشتری"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.customer_id == customer_id
            ).first()
            
            if not membership:
                raise ValueError("عضویت یافت نشد")
            
            # دریافت تراکنش‌های امتیاز
            query = self.db.query(PointTransaction).filter(
                PointTransaction.membership_id == membership.id
            )
            
            if start_date:
                query = query.filter(PointTransaction.created_at >= start_date)
            if end_date:
                query = query.filter(PointTransaction.created_at <= end_date)
            
            transactions = query.order_by(PointTransaction.created_at.desc()).all()
            
            # دریافت پاداش‌های دریافتی
            rewards = self.db.query(CustomerReward).filter(
                CustomerReward.membership_id == membership.id
            ).order_by(CustomerReward.created_at.desc()).all()
            
            return {
                "points_history": [{
                    "date": t.created_at,
                    "type": t.transaction_type,
                    "points": t.points,
                    "description": t.description
                } for t in transactions],
                "rewards_history": [{
                    "date": r.created_at,
                    "reward_name": r.reward.name,
                    "points_spent": r.points_spent,
                    "status": r.status,
                    "expires_at": r.expires_at
                } for r in rewards]
            }
        except Exception as e:
            logger.error(f"خطا در دریافت تاریخچه عضویت: {str(e)}")
            raise 