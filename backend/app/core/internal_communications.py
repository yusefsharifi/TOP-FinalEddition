from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship

class MessageStatus(Enum):
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ARCHIVED = "archived"

class ForumCategory(Enum):
    GENERAL = "general"
    TECHNICAL = "technical"
    HR = "hr"
    PROJECTS = "projects"
    SOCIAL = "social"
    ANNOUNCEMENTS = "announcements"

class SuggestionStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"

class Message(BaseModel):
    id: int
    sender_id: int
    recipients: List[int]
    subject: str
    content: str
    attachments: List[Dict[str, Any]] = []
    status: MessageStatus
    created_at: datetime
    updated_at: datetime
    read_by: List[int] = []
    priority: int = 1
    tags: List[str] = []

class ForumPost(BaseModel):
    id: int
    author_id: int
    category: ForumCategory
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    likes: int = 0
    comments: List[Dict[str, Any]] = []
    tags: List[str] = []
    is_pinned: bool = False
    is_locked: bool = False
    views: int = 0

class Suggestion(BaseModel):
    id: int
    employee_id: int
    title: str
    description: str
    category: str
    status: SuggestionStatus
    created_at: datetime
    updated_at: datetime
    feedback: List[Dict[str, Any]] = []
    assigned_to: Optional[int] = None
    priority: int = 1
    impact_analysis: Optional[Dict[str, Any]] = None

class Event(BaseModel):
    id: int
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    location: str
    organizer_id: int
    attendees: List[int] = []
    category: str
    is_public: bool = True
    attachments: List[Dict[str, Any]] = []
    reminders: List[Dict[str, Any]] = []

class InternalCommunicationsSystem:
    def __init__(self):
        self.messages: Dict[int, Message] = {}
        self.forum_posts: Dict[int, ForumPost] = {}
        self.suggestions: Dict[int, Suggestion] = {}
        self.events: Dict[int, Event] = {}
        self.notifications: Dict[int, List[Dict[str, Any]]] = {}

    def send_message(self, sender_id: int, recipients: List[int], subject: str, content: str) -> int:
        """Send a new message to recipients"""
        message_id = len(self.messages) + 1
        message = Message(
            id=message_id,
            sender_id=sender_id,
            recipients=recipients,
            subject=subject,
            content=content,
            status=MessageStatus.SENT,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.messages[message_id] = message
        self._create_notifications(recipients, "new_message", message_id)
        return message_id

    def create_forum_post(self, author_id: int, category: ForumCategory, title: str, content: str) -> int:
        """Create a new forum post"""
        post_id = len(self.forum_posts) + 1
        post = ForumPost(
            id=post_id,
            author_id=author_id,
            category=category,
            title=title,
            content=content,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.forum_posts[post_id] = post
        return post_id

    def add_comment(self, post_id: int, author_id: int, content: str) -> bool:
        """Add a comment to a forum post"""
        if post_id not in self.forum_posts:
            return False
        post = self.forum_posts[post_id]
        comment = {
            "id": len(post.comments) + 1,
            "author_id": author_id,
            "content": content,
            "created_at": datetime.now(),
            "likes": 0
        }
        post.comments.append(comment)
        post.updated_at = datetime.now()
        return True

    def submit_suggestion(self, employee_id: int, title: str, description: str, category: str) -> int:
        """Submit a new suggestion"""
        suggestion_id = len(self.suggestions) + 1
        suggestion = Suggestion(
            id=suggestion_id,
            employee_id=employee_id,
            title=title,
            description=description,
            category=category,
            status=SuggestionStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.suggestions[suggestion_id] = suggestion
        self._create_notifications([employee_id], "new_suggestion", suggestion_id)
        return suggestion_id

    def create_event(self, title: str, description: str, start_date: datetime, 
                    end_date: datetime, location: str, organizer_id: int) -> int:
        """Create a new event"""
        event_id = len(self.events) + 1
        event = Event(
            id=event_id,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            location=location,
            organizer_id=organizer_id,
            created_at=datetime.now()
        )
        self.events[event_id] = event
        return event_id

    def mark_message_read(self, message_id: int, user_id: int) -> bool:
        """Mark a message as read by a user"""
        if message_id not in self.messages:
            return False
        message = self.messages[message_id]
        if user_id not in message.read_by:
            message.read_by.append(user_id)
            message.status = MessageStatus.READ
            message.updated_at = datetime.now()
        return True

    def update_suggestion_status(self, suggestion_id: int, status: SuggestionStatus) -> bool:
        """Update the status of a suggestion"""
        if suggestion_id not in self.suggestions:
            return False
        suggestion = self.suggestions[suggestion_id]
        suggestion.status = status
        suggestion.updated_at = datetime.now()
        self._create_notifications([suggestion.employee_id], "suggestion_status_update", suggestion_id)
        return True

    def get_user_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all notifications for a user"""
        return self.notifications.get(user_id, [])

    def get_forum_posts(self, category: Optional[ForumCategory] = None, 
                       page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get forum posts with pagination and optional category filter"""
        posts = list(self.forum_posts.values())
        if category:
            posts = [p for p in posts if p.category == category]
        
        # Sort by pinned status and creation date
        posts.sort(key=lambda x: (-x.is_pinned, -x.created_at.timestamp()))
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_posts = posts[start_idx:end_idx]
        
        return {
            "posts": paginated_posts,
            "total": len(posts),
            "page": page,
            "per_page": per_page,
            "total_pages": (len(posts) + per_page - 1) // per_page
        }

    def get_upcoming_events(self, days: int = 7) -> List[Event]:
        """Get upcoming events within specified days"""
        now = datetime.now()
        end_date = now + timedelta(days=days)
        return [
            event for event in self.events.values()
            if event.start_date >= now and event.start_date <= end_date
        ]

    def get_suggestions_by_status(self, status: SuggestionStatus) -> List[Suggestion]:
        """Get all suggestions with a specific status"""
        return [
            suggestion for suggestion in self.suggestions.values()
            if suggestion.status == status
        ]

    def get_communication_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics for internal communications"""
        return {
            "message_statistics": {
                "total_messages": len(self.messages),
                "messages_by_status": self._get_messages_by_status(),
                "average_response_time": self._calculate_average_response_time()
            },
            "forum_statistics": {
                "total_posts": len(self.forum_posts),
                "posts_by_category": self._get_posts_by_category(),
                "engagement_metrics": self._calculate_forum_engagement()
            },
            "suggestion_statistics": {
                "total_suggestions": len(self.suggestions),
                "suggestions_by_status": self._get_suggestions_by_status(),
                "implementation_rate": self._calculate_implementation_rate()
            },
            "event_statistics": {
                "total_events": len(self.events),
                "upcoming_events": len(self.get_upcoming_events()),
                "attendance_rate": self._calculate_attendance_rate()
            }
        }

    def _create_notifications(self, user_ids: List[int], notification_type: str, reference_id: int) -> None:
        """Create notifications for users"""
        for user_id in user_ids:
            if user_id not in self.notifications:
                self.notifications[user_id] = []
            self.notifications[user_id].append({
                "type": notification_type,
                "reference_id": reference_id,
                "created_at": datetime.now(),
                "is_read": False
            })

    def _get_messages_by_status(self) -> Dict[str, int]:
        """Get distribution of messages by status"""
        distribution = {status.value: 0 for status in MessageStatus}
        for message in self.messages.values():
            distribution[message.status.value] += 1
        return distribution

    def _calculate_average_response_time(self) -> float:
        """Calculate average message response time"""
        response_times = []
        for message in self.messages.values():
            if message.status == MessageStatus.READ and message.read_by:
                first_read = min(message.read_by)
                response_time = (first_read - message.created_at).total_seconds() / 3600  # in hours
                response_times.append(response_time)
        return sum(response_times) / len(response_times) if response_times else 0.0

    def _get_posts_by_category(self) -> Dict[str, int]:
        """Get distribution of forum posts by category"""
        distribution = {category.value: 0 for category in ForumCategory}
        for post in self.forum_posts.values():
            distribution[post.category.value] += 1
        return distribution

    def _calculate_forum_engagement(self) -> Dict[str, float]:
        """Calculate forum engagement metrics"""
        total_posts = len(self.forum_posts)
        total_comments = sum(len(post.comments) for post in self.forum_posts.values())
        total_likes = sum(post.likes for post in self.forum_posts.values())
        total_views = sum(post.views for post in self.forum_posts.values())
        
        return {
            "average_comments_per_post": total_comments / total_posts if total_posts > 0 else 0,
            "average_likes_per_post": total_likes / total_posts if total_posts > 0 else 0,
            "average_views_per_post": total_views / total_posts if total_posts > 0 else 0
        }

    def _get_suggestions_by_status(self) -> Dict[str, int]:
        """Get distribution of suggestions by status"""
        distribution = {status.value: 0 for status in SuggestionStatus}
        for suggestion in self.suggestions.values():
            distribution[suggestion.status.value] += 1
        return distribution

    def _calculate_implementation_rate(self) -> float:
        """Calculate the rate of implemented suggestions"""
        total_suggestions = len(self.suggestions)
        implemented = len([s for s in self.suggestions.values() 
                         if s.status == SuggestionStatus.IMPLEMENTED])
        return implemented / total_suggestions if total_suggestions > 0 else 0.0

    def _calculate_attendance_rate(self) -> float:
        """Calculate average event attendance rate"""
        total_attendees = sum(len(event.attendees) for event in self.events.values())
        total_events = len(self.events)
        return total_attendees / total_events if total_events > 0 else 0.0 