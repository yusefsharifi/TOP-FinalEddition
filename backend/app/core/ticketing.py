import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import pandas as pd
from .ai_analytics import BusinessAIAnalytics

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"

class TicketCategory(Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    SALES = "sales"
    GENERAL = "general"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    SUGGESTION = "suggestion"

class TicketSource(Enum):
    EMAIL = "email"
    WEB = "web"
    PHONE = "phone"
    CHAT = "chat"
    SOCIAL_MEDIA = "social_media"
    MOBILE_APP = "mobile_app"

class SLAStatus(Enum):
    WITHIN_SLA = "within_sla"
    NEAR_SLA = "near_sla"
    BREACHED_SLA = "breached_sla"

@dataclass
class Ticket:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    source: TicketSource
    customer_id: str
    assigned_to: Optional[str] = None
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    sla_status: SLAStatus = SLAStatus.WITHIN_SLA
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    sentiment_score: Optional[float] = None
    resolution_time: Optional[float] = None
    customer_satisfaction: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TicketComment:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ticket_id: str
    user_id: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_internal: bool = False
    sentiment_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SLA:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: TicketCategory
    priority: TicketPriority
    response_time: int  # در دقیقه
    resolution_time: int  # در دقیقه
    business_hours: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class SupportAgent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    email: str
    categories: List[TicketCategory]
    skills: List[str]
    availability: bool = True
    current_tickets: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class TicketingManager:
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.ai_analytics = BusinessAIAnalytics()
        
        # تنظیمات پردازش متن
        self.text_vectorizer = TfidfVectorizer()
        self.sentiment_analyzer = None
        self.setup_nlp()
        
        # ایجاد دایرکتوری‌های مورد نیاز
        self.create_directories()
        
        # بارگذاری داده‌ها
        self.load_data()

    def setup_nlp(self):
        """تنظیم پردازش زبان طبیعی"""
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            logger.info("NLP models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NLP models: {str(e)}")
            raise

    def create_directories(self):
        """ایجاد دایرکتوری‌های مورد نیاز"""
        directories = [
            "tickets",
            "comments",
            "slas",
            "agents",
            "attachments",
            "analytics"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    def load_data(self):
        """بارگذاری داده‌ها از فایل‌ها"""
        try:
            self.tickets = self._load_json("tickets/tickets.json", {})
            self.comments = self._load_json("comments/comments.json", {})
            self.slas = self._load_json("slas/slas.json", {})
            self.agents = self._load_json("agents/agents.json", {})
            logger.info("All data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _load_json(self, file_path: str, default_value: Any) -> Any:
        """بارگذاری داده از فایل JSON"""
        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_value
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return default_value

    def _save_json(self, file_path: str, data: Any):
        """ذخیره داده در فایل JSON"""
        try:
            full_path = self.base_path / file_path
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving {file_path}: {str(e)}")
            raise

    def create_ticket(self, ticket: Ticket) -> Ticket:
        """ایجاد تیکت جدید"""
        try:
            # تحلیل احساسات متن تیکت
            sentiment = self.sentiment_analyzer(ticket.description)[0]
            ticket.sentiment_score = float(sentiment["score"])
            
            # تعیین اولویت هوشمند
            ticket.priority = self._determine_priority(ticket)
            
            # ذخیره تیکت
            self.tickets[ticket.id] = ticket.__dict__
            self._save_json("tickets/tickets.json", self.tickets)
            
            logger.info(f"Created ticket: {ticket.id}")
            return ticket
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            raise

    def _determine_priority(self, ticket: Ticket) -> TicketPriority:
        """تعیین اولویت هوشمند تیکت"""
        try:
            # عوامل موثر در اولویت‌بندی
            factors = {
                "sentiment_score": ticket.sentiment_score or 0.5,
                "category_priority": self._get_category_priority(ticket.category),
                "customer_priority": self._get_customer_priority(ticket.customer_id),
                "keyword_priority": self._analyze_keywords(ticket.description)
            }
            
            # محاسبه امتیاز کلی
            total_score = sum(factors.values())
            
            # تعیین اولویت بر اساس امتیاز
            if total_score >= 3.5:
                return TicketPriority.CRITICAL
            elif total_score >= 2.5:
                return TicketPriority.URGENT
            elif total_score >= 1.5:
                return TicketPriority.HIGH
            elif total_score >= 0.5:
                return TicketPriority.MEDIUM
            else:
                return TicketPriority.LOW
        except Exception as e:
            logger.error(f"Error determining priority: {str(e)}")
            return TicketPriority.MEDIUM

    def _get_category_priority(self, category: TicketCategory) -> float:
        """دریافت اولویت دسته‌بندی"""
        priorities = {
            TicketCategory.TECHNICAL: 1.0,
            TicketCategory.BILLING: 0.8,
            TicketCategory.SALES: 0.6,
            TicketCategory.GENERAL: 0.4,
            TicketCategory.COMPLAINT: 1.2,
            TicketCategory.FEEDBACK: 0.3,
            TicketCategory.SUGGESTION: 0.2
        }
        return priorities.get(category, 0.5)

    def _get_customer_priority(self, customer_id: str) -> float:
        """دریافت اولویت مشتری"""
        try:
            # این بخش می‌تواند با سیستم CRM یکپارچه شود
            return 0.5
        except Exception as e:
            logger.error(f"Error getting customer priority: {str(e)}")
            return 0.5

    def _analyze_keywords(self, text: str) -> float:
        """تحلیل کلمات کلیدی متن"""
        try:
            urgent_keywords = ["urgent", "critical", "immediate", "asap", "emergency"]
            high_keywords = ["important", "high priority", "need help", "issue"]
            medium_keywords = ["question", "request", "help", "support"]
            
            text = text.lower()
            score = 0.0
            
            for word in urgent_keywords:
                if word in text:
                    score += 1.0
            for word in high_keywords:
                if word in text:
                    score += 0.7
            for word in medium_keywords:
                if word in text:
                    score += 0.3
                    
            return min(score, 1.0)
        except Exception as e:
            logger.error(f"Error analyzing keywords: {str(e)}")
            return 0.5

    def assign_ticket(self, ticket_id: str) -> Optional[str]:
        """تخصیص هوشمند تیکت به کارشناس"""
        try:
            if ticket_id not in self.tickets:
                raise ValueError("Ticket not found")
            
            ticket = self.tickets[ticket_id]
            
            # فیلتر کردن کارشناسان مناسب
            suitable_agents = [
                agent for agent in self.agents.values()
                if (agent["availability"] and
                    ticket["category"] in agent["categories"] and
                    agent["current_tickets"] < 10)  # محدودیت تعداد تیکت‌های همزمان
            ]
            
            if not suitable_agents:
                return None
            
            # محاسبه امتیاز هر کارشناس
            agent_scores = []
            for agent in suitable_agents:
                score = self._calculate_agent_score(agent, ticket)
                agent_scores.append((agent["id"], score))
            
            # انتخاب کارشناس با بالاترین امتیاز
            best_agent = max(agent_scores, key=lambda x: x[1])[0]
            
            # به‌روزرسانی وضعیت کارشناس
            self.agents[best_agent]["current_tickets"] += 1
            self._save_json("agents/agents.json", self.agents)
            
            # به‌روزرسانی تیکت
            ticket["assigned_to"] = best_agent
            ticket["status"] = TicketStatus.IN_PROGRESS
            self._save_json("tickets/tickets.json", self.tickets)
            
            return best_agent
        except Exception as e:
            logger.error(f"Error assigning ticket: {str(e)}")
            return None

    def _calculate_agent_score(self, agent: Dict[str, Any], ticket: Dict[str, Any]) -> float:
        """محاسبه امتیاز کارشناس"""
        try:
            scores = {
                "category_match": 0.4,
                "skill_match": 0.3,
                "performance": 0.2,
                "workload": 0.1
            }
            
            # تطابق دسته‌بندی
            if ticket["category"] in agent["categories"]:
                scores["category_match"] = 1.0
            
            # تطابق مهارت‌ها
            skill_match = self._calculate_skill_match(agent["skills"], ticket["description"])
            scores["skill_match"] = skill_match
            
            # عملکرد
            performance = agent.get("performance_metrics", {}).get("resolution_rate", 0.5)
            scores["performance"] = performance
            
            # بار کاری
            workload = 1.0 - (agent["current_tickets"] / 10)
            scores["workload"] = workload
            
            # محاسبه امتیاز نهایی
            final_score = sum(scores.values()) / len(scores)
            return final_score
        except Exception as e:
            logger.error(f"Error calculating agent score: {str(e)}")
            return 0.0

    def _calculate_skill_match(self, skills: List[str], text: str) -> float:
        """محاسبه تطابق مهارت‌ها"""
        try:
            text = text.lower()
            matches = sum(1 for skill in skills if skill.lower() in text)
            return min(matches / len(skills), 1.0) if skills else 0.0
        except Exception as e:
            logger.error(f"Error calculating skill match: {str(e)}")
            return 0.0

    def add_comment(self, comment: TicketComment) -> TicketComment:
        """افزودن نظر به تیکت"""
        try:
            # تحلیل احساسات نظر
            sentiment = self.sentiment_analyzer(comment.content)[0]
            comment.sentiment_score = float(sentiment["score"])
            
            # ذخیره نظر
            self.comments[comment.id] = comment.__dict__
            self._save_json("comments/comments.json", self.comments)
            
            # به‌روزرسانی تیکت
            ticket = self.tickets[comment.ticket_id]
            ticket["comments"].append({
                "id": comment.id,
                "user_id": comment.user_id,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "is_internal": comment.is_internal
            })
            self._save_json("tickets/tickets.json", self.tickets)
            
            logger.info(f"Added comment to ticket: {comment.ticket_id}")
            return comment
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            raise

    def update_ticket_status(self, ticket_id: str, status: TicketStatus) -> Ticket:
        """به‌روزرسانی وضعیت تیکت"""
        try:
            if ticket_id not in self.tickets:
                raise ValueError("Ticket not found")
            
            ticket = self.tickets[ticket_id]
            ticket["status"] = status
            ticket["updated_at"] = datetime.now().isoformat()
            
            if status == TicketStatus.RESOLVED:
                ticket["resolved_at"] = datetime.now().isoformat()
                ticket["resolution_time"] = self._calculate_resolution_time(ticket)
            elif status == TicketStatus.CLOSED:
                ticket["closed_at"] = datetime.now().isoformat()
                # به‌روزرسانی وضعیت کارشناس
                if ticket["assigned_to"]:
                    self.agents[ticket["assigned_to"]]["current_tickets"] -= 1
                    self._save_json("agents/agents.json", self.agents)
            
            self._save_json("tickets/tickets.json", self.tickets)
            return Ticket(**ticket)
        except Exception as e:
            logger.error(f"Error updating ticket status: {str(e)}")
            raise

    def _calculate_resolution_time(self, ticket: Dict[str, Any]) -> float:
        """محاسبه زمان حل تیکت"""
        try:
            created_at = datetime.fromisoformat(ticket["created_at"])
            resolved_at = datetime.fromisoformat(ticket["resolved_at"])
            resolution_time = (resolved_at - created_at).total_seconds() / 3600  # تبدیل به ساعت
            return round(resolution_time, 2)
        except Exception as e:
            logger.error(f"Error calculating resolution time: {str(e)}")
            return 0.0

    def get_ticket_analytics(self) -> Dict[str, Any]:
        """دریافت تحلیل‌های تیکتینگ"""
        try:
            analytics = {
                "ticket_stats": self._get_ticket_stats(),
                "performance_metrics": self._get_performance_metrics(),
                "customer_satisfaction": self._get_customer_satisfaction(),
                "agent_performance": self._get_agent_performance(),
                "category_analysis": self._get_category_analysis(),
                "sla_compliance": self._get_sla_compliance()
            }
            
            return analytics
        except Exception as e:
            logger.error(f"Error getting ticket analytics: {str(e)}")
            raise

    def _get_ticket_stats(self) -> Dict[str, Any]:
        """دریافت آمار تیکت‌ها"""
        try:
            total_tickets = len(self.tickets)
            open_tickets = sum(1 for t in self.tickets.values() if t["status"] == TicketStatus.OPEN)
            in_progress = sum(1 for t in self.tickets.values() if t["status"] == TicketStatus.IN_PROGRESS)
            resolved = sum(1 for t in self.tickets.values() if t["status"] == TicketStatus.RESOLVED)
            
            return {
                "total_tickets": total_tickets,
                "open_tickets": open_tickets,
                "in_progress": in_progress,
                "resolved": resolved,
                "resolution_rate": round(resolved / total_tickets * 100, 2) if total_tickets > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting ticket stats: {str(e)}")
            raise

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """دریافت معیارهای عملکرد"""
        try:
            resolution_times = [
                t["resolution_time"] for t in self.tickets.values()
                if t["resolution_time"] is not None
            ]
            
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            
            return {
                "average_resolution_time": round(avg_resolution_time, 2),
                "first_response_time": self._calculate_first_response_time(),
                "ticket_volume": self._calculate_ticket_volume()
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            raise

    def _calculate_first_response_time(self) -> float:
        """محاسبه میانگین زمان پاسخ اولیه"""
        try:
            response_times = []
            for ticket in self.tickets.values():
                if ticket["comments"]:
                    first_comment = min(ticket["comments"], key=lambda x: x["created_at"])
                    created_at = datetime.fromisoformat(ticket["created_at"])
                    first_response = datetime.fromisoformat(first_comment["created_at"])
                    response_time = (first_response - created_at).total_seconds() / 3600
                    response_times.append(response_time)
            
            return round(sum(response_times) / len(response_times), 2) if response_times else 0
        except Exception as e:
            logger.error(f"Error calculating first response time: {str(e)}")
            return 0.0

    def _calculate_ticket_volume(self) -> Dict[str, int]:
        """محاسبه حجم تیکت‌ها"""
        try:
            volume = {
                "daily": 0,
                "weekly": 0,
                "monthly": 0
            }
            
            now = datetime.now()
            for ticket in self.tickets.values():
                created_at = datetime.fromisoformat(ticket["created_at"])
                days_diff = (now - created_at).days
                
                if days_diff <= 1:
                    volume["daily"] += 1
                if days_diff <= 7:
                    volume["weekly"] += 1
                if days_diff <= 30:
                    volume["monthly"] += 1
            
            return volume
        except Exception as e:
            logger.error(f"Error calculating ticket volume: {str(e)}")
            raise

    def _get_customer_satisfaction(self) -> Dict[str, Any]:
        """دریافت رضایت مشتری"""
        try:
            satisfaction_scores = [
                t["customer_satisfaction"] for t in self.tickets.values()
                if t["customer_satisfaction"] is not None
            ]
            
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
            
            return {
                "average_satisfaction": round(avg_satisfaction, 2),
                "satisfaction_distribution": self._get_satisfaction_distribution()
            }
        except Exception as e:
            logger.error(f"Error getting customer satisfaction: {str(e)}")
            raise

    def _get_satisfaction_distribution(self) -> Dict[str, int]:
        """دریافت توزیع رضایت"""
        try:
            distribution = {
                "very_satisfied": 0,
                "satisfied": 0,
                "neutral": 0,
                "dissatisfied": 0
            }
            
            for ticket in self.tickets.values():
                if ticket["customer_satisfaction"] is not None:
                    score = ticket["customer_satisfaction"]
                    if score >= 0.8:
                        distribution["very_satisfied"] += 1
                    elif score >= 0.6:
                        distribution["satisfied"] += 1
                    elif score >= 0.4:
                        distribution["neutral"] += 1
                    else:
                        distribution["dissatisfied"] += 1
            
            return distribution
        except Exception as e:
            logger.error(f"Error getting satisfaction distribution: {str(e)}")
            raise

    def _get_agent_performance(self) -> Dict[str, Any]:
        """دریافت عملکرد کارشناسان"""
        try:
            performance = {}
            for agent_id, agent in self.agents.items():
                agent_tickets = [
                    t for t in self.tickets.values()
                    if t["assigned_to"] == agent_id
                ]
                
                resolved_tickets = [
                    t for t in agent_tickets
                    if t["status"] == TicketStatus.RESOLVED
                ]
                
                performance[agent_id] = {
                    "total_tickets": len(agent_tickets),
                    "resolved_tickets": len(resolved_tickets),
                    "resolution_rate": round(len(resolved_tickets) / len(agent_tickets) * 100, 2) if agent_tickets else 0,
                    "average_resolution_time": self._calculate_agent_resolution_time(agent_tickets)
                }
            
            return performance
        except Exception as e:
            logger.error(f"Error getting agent performance: {str(e)}")
            raise

    def _calculate_agent_resolution_time(self, tickets: List[Dict[str, Any]]) -> float:
        """محاسبه میانگین زمان حل تیکت برای کارشناس"""
        try:
            resolution_times = [
                t["resolution_time"] for t in tickets
                if t["resolution_time"] is not None
            ]
            
            return round(sum(resolution_times) / len(resolution_times), 2) if resolution_times else 0
        except Exception as e:
            logger.error(f"Error calculating agent resolution time: {str(e)}")
            return 0.0

    def _get_category_analysis(self) -> Dict[str, Any]:
        """تحلیل دسته‌بندی تیکت‌ها"""
        try:
            analysis = {}
            for category in TicketCategory:
                category_tickets = [
                    t for t in self.tickets.values()
                    if t["category"] == category
                ]
                
                analysis[category.value] = {
                    "total_tickets": len(category_tickets),
                    "resolved_tickets": sum(1 for t in category_tickets if t["status"] == TicketStatus.RESOLVED),
                    "average_resolution_time": self._calculate_category_resolution_time(category_tickets),
                    "priority_distribution": self._get_category_priority_distribution(category_tickets)
                }
            
            return analysis
        except Exception as e:
            logger.error(f"Error getting category analysis: {str(e)}")
            raise

    def _calculate_category_resolution_time(self, tickets: List[Dict[str, Any]]) -> float:
        """محاسبه میانگین زمان حل تیکت برای دسته‌بندی"""
        try:
            resolution_times = [
                t["resolution_time"] for t in tickets
                if t["resolution_time"] is not None
            ]
            
            return round(sum(resolution_times) / len(resolution_times), 2) if resolution_times else 0
        except Exception as e:
            logger.error(f"Error calculating category resolution time: {str(e)}")
            return 0.0

    def _get_category_priority_distribution(self, tickets: List[Dict[str, Any]]) -> Dict[str, int]:
        """دریافت توزیع اولویت برای دسته‌بندی"""
        try:
            distribution = {
                "critical": 0,
                "urgent": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
            
            for ticket in tickets:
                priority = ticket["priority"]
                distribution[priority] = distribution.get(priority, 0) + 1
            
            return distribution
        except Exception as e:
            logger.error(f"Error getting category priority distribution: {str(e)}")
            raise

    def _get_sla_compliance(self) -> Dict[str, Any]:
        """دریافت انطباق با SLA"""
        try:
            compliance = {
                "total_tickets": len(self.tickets),
                "within_sla": sum(1 for t in self.tickets.values() if t["sla_status"] == SLAStatus.WITHIN_SLA),
                "near_sla": sum(1 for t in self.tickets.values() if t["sla_status"] == SLAStatus.NEAR_SLA),
                "breached_sla": sum(1 for t in self.tickets.values() if t["sla_status"] == SLAStatus.BREACHED_SLA)
            }
            
            compliance["compliance_rate"] = round(compliance["within_sla"] / compliance["total_tickets"] * 100, 2) if compliance["total_tickets"] > 0 else 0
            
            return compliance
        except Exception as e:
            logger.error(f"Error getting SLA compliance: {str(e)}")
            raise 