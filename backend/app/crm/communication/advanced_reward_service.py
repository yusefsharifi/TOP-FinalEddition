from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.crm.models.advanced_loyalty import (
    ExperientialReward, PersonalizedReward, PartnerReward,
    CustomerRewardPreference, RewardRedemptionHistory, RewardType
)
from app.crm.models.loyalty import CustomerMembership, PointTransaction, PointTransactionType
from app.utils.logger import log_error

class AdvancedRewardService:
    def __init__(self, db: Session):
        self.db = db

    def create_experiential_reward(self, data: Dict) -> Optional[ExperientialReward]:
        """ایجاد پاداش تجربه‌ای جدید"""
        try:
            reward = ExperientialReward(**data)
            self.db.add(reward)
            self.db.commit()
            self.db.refresh(reward)
            return reward
        except Exception as e:
            log_error(f"خطا در ایجاد پاداش تجربه‌ای: {str(e)}")
            self.db.rollback()
            return None

    def create_personalized_reward(self, data: Dict) -> Optional[PersonalizedReward]:
        """ایجاد پاداش شخصی‌سازی شده جدید"""
        try:
            reward = PersonalizedReward(**data)
            self.db.add(reward)
            self.db.commit()
            self.db.refresh(reward)
            return reward
        except Exception as e:
            log_error(f"خطا در ایجاد پاداش شخصی‌سازی شده: {str(e)}")
            self.db.rollback()
            return None

    def create_partner_reward(self, data: Dict) -> Optional[PartnerReward]:
        """ایجاد پاداش مشارکتی جدید"""
        try:
            reward = PartnerReward(**data)
            self.db.add(reward)
            self.db.commit()
            self.db.refresh(reward)
            return reward
        except Exception as e:
            log_error(f"خطا در ایجاد پاداش مشارکتی: {str(e)}")
            self.db.rollback()
            return None

    def get_available_rewards(self, customer_id: int) -> Dict[str, List]:
        """دریافت لیست پاداش‌های قابل استفاده برای مشتری"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.customer_id == customer_id
            ).first()
            
            if not membership:
                return {}

            # دریافت ترجیحات مشتری
            preferences = self.db.query(CustomerRewardPreference).filter(
                CustomerRewardPreference.customer_id == customer_id
            ).first()

            # دریافت پاداش‌های تجربه‌ای
            experiential_rewards = self.db.query(ExperientialReward).filter(
                ExperientialReward.is_active == True,
                ExperientialReward.start_date <= datetime.utcnow(),
                (ExperientialReward.end_date.is_(None) | (ExperientialReward.end_date >= datetime.utcnow())),
                ExperientialReward.quantity_available > 0,
                ExperientialReward.points_cost <= membership.points_balance
            ).all()

            # دریافت پاداش‌های شخصی‌سازی شده
            personalized_rewards = self.db.query(PersonalizedReward).filter(
                PersonalizedReward.is_active == True,
                PersonalizedReward.points_cost <= membership.points_balance
            ).all()

            # دریافت پاداش‌های مشارکتی
            partner_rewards = self.db.query(PartnerReward).filter(
                PartnerReward.is_active == True,
                PartnerReward.start_date <= datetime.utcnow(),
                (PartnerReward.end_date.is_(None) | (PartnerReward.end_date >= datetime.utcnow())),
                PartnerReward.quantity_available > 0,
                PartnerReward.points_cost <= membership.points_balance
            ).all()

            return {
                "experiential": experiential_rewards,
                "personalized": personalized_rewards,
                "partner": partner_rewards
            }
        except Exception as e:
            log_error(f"خطا در دریافت پاداش‌های قابل استفاده: {str(e)}")
            return {}

    def redeem_experiential_reward(self, customer_id: int, reward_id: int) -> Optional[RewardRedemptionHistory]:
        """استفاده از پاداش تجربه‌ای"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.customer_id == customer_id
            ).first()
            
            if not membership:
                return None

            reward = self.db.query(ExperientialReward).filter(
                ExperientialReward.id == reward_id,
                ExperientialReward.is_active == True,
                ExperientialReward.quantity_available > 0
            ).first()

            if not reward or reward.points_cost > membership.points_balance:
                return None

            # ایجاد تراکنش امتیاز
            transaction = PointTransaction(
                membership_id=membership.id,
                transaction_type=PointTransactionType.REDEEM,
                points=-reward.points_cost,
                description=f"استفاده از پاداش تجربه‌ای: {reward.name}",
                metadata={"reward_id": reward.id, "reward_type": RewardType.EXPERIENTIAL}
            )
            self.db.add(transaction)

            # به‌روزرسانی موجودی امتیاز
            membership.points_balance -= reward.points_cost
            reward.quantity_available -= 1

            # ثبت تاریخچه استفاده
            history = RewardRedemptionHistory(
                customer_id=customer_id,
                reward_type=RewardType.EXPERIENTIAL,
                reward_id=reward.id,
                points_cost=reward.points_cost,
                status="completed"
            )
            self.db.add(history)

            self.db.commit()
            return history
        except Exception as e:
            log_error(f"خطا در استفاده از پاداش تجربه‌ای: {str(e)}")
            self.db.rollback()
            return None

    def redeem_personalized_reward(self, customer_id: int, reward_id: int, personalization_data: Dict) -> Optional[RewardRedemptionHistory]:
        """استفاده از پاداش شخصی‌سازی شده"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.customer_id == customer_id
            ).first()
            
            if not membership:
                return None

            reward = self.db.query(PersonalizedReward).filter(
                PersonalizedReward.id == reward_id,
                PersonalizedReward.is_active == True
            ).first()

            if not reward or reward.points_cost > membership.points_balance:
                return None

            # ایجاد تراکنش امتیاز
            transaction = PointTransaction(
                membership_id=membership.id,
                transaction_type=PointTransactionType.REDEEM,
                points=-reward.points_cost,
                description=f"استفاده از پاداش شخصی‌سازی شده: {reward.name}",
                metadata={
                    "reward_id": reward.id,
                    "reward_type": RewardType.PERSONALIZED,
                    "personalization_data": personalization_data
                }
            )
            self.db.add(transaction)

            # به‌روزرسانی موجودی امتیاز
            membership.points_balance -= reward.points_cost

            # ثبت تاریخچه استفاده
            history = RewardRedemptionHistory(
                customer_id=customer_id,
                reward_type=RewardType.PERSONALIZED,
                reward_id=reward.id,
                points_cost=reward.points_cost,
                status="completed",
                metadata={"personalization_data": personalization_data}
            )
            self.db.add(history)

            self.db.commit()
            return history
        except Exception as e:
            log_error(f"خطا در استفاده از پاداش شخصی‌سازی شده: {str(e)}")
            self.db.rollback()
            return None

    def redeem_partner_reward(self, customer_id: int, reward_id: int) -> Optional[RewardRedemptionHistory]:
        """استفاده از پاداش مشارکتی"""
        try:
            membership = self.db.query(CustomerMembership).filter(
                CustomerMembership.customer_id == customer_id
            ).first()
            
            if not membership:
                return None

            reward = self.db.query(PartnerReward).filter(
                PartnerReward.id == reward_id,
                PartnerReward.is_active == True,
                PartnerReward.quantity_available > 0
            ).first()

            if not reward or reward.points_cost > membership.points_balance:
                return None

            # ایجاد تراکنش امتیاز
            transaction = PointTransaction(
                membership_id=membership.id,
                transaction_type=PointTransactionType.REDEEM,
                points=-reward.points_cost,
                description=f"استفاده از پاداش مشارکتی: {reward.name}",
                metadata={"reward_id": reward.id, "reward_type": RewardType.PARTNER}
            )
            self.db.add(transaction)

            # به‌روزرسانی موجودی امتیاز
            membership.points_balance -= reward.points_cost
            reward.quantity_available -= 1

            # ثبت تاریخچه استفاده
            history = RewardRedemptionHistory(
                customer_id=customer_id,
                reward_type=RewardType.PARTNER,
                reward_id=reward.id,
                points_cost=reward.points_cost,
                status="completed"
            )
            self.db.add(history)

            self.db.commit()
            return history
        except Exception as e:
            log_error(f"خطا در استفاده از پاداش مشارکتی: {str(e)}")
            self.db.rollback()
            return None

    def update_reward_preferences(self, customer_id: int, preferences: Dict) -> Optional[CustomerRewardPreference]:
        """به‌روزرسانی ترجیحات پاداش مشتری"""
        try:
            preference = self.db.query(CustomerRewardPreference).filter(
                CustomerRewardPreference.customer_id == customer_id
            ).first()

            if preference:
                for key, value in preferences.items():
                    setattr(preference, key, value)
                preference.last_updated = datetime.utcnow()
            else:
                preference = CustomerRewardPreference(
                    customer_id=customer_id,
                    **preferences
                )
                self.db.add(preference)

            self.db.commit()
            self.db.refresh(preference)
            return preference
        except Exception as e:
            log_error(f"خطا در به‌روزرسانی ترجیحات پاداش: {str(e)}")
            self.db.rollback()
            return None

    def get_redemption_history(self, customer_id: int) -> List[RewardRedemptionHistory]:
        """دریافت تاریخچه استفاده از پاداش‌ها"""
        try:
            history = self.db.query(RewardRedemptionHistory).filter(
                RewardRedemptionHistory.customer_id == customer_id
            ).order_by(RewardRedemptionHistory.redemption_date.desc()).all()
            return history
        except Exception as e:
            log_error(f"خطا در دریافت تاریخچه استفاده از پاداش‌ها: {str(e)}")
            return [] 