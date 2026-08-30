from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass

class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    OPERATOR = "operator"

class InteractionType(Enum):
    QUESTION = "question"
    SUGGESTION = "suggestion"
    FEEDBACK = "feedback"
    COMMAND = "command"
    REPORT = "report"

@dataclass
class UserInteraction:
    id: str
    user_id: str
    user_role: UserRole
    type: InteractionType
    content: str
    timestamp: datetime
    context: Dict[str, Any]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class AIResponse:
    id: str
    interaction_id: str
    content: str
    recommendations: List[Dict[str, Any]]
    confidence_score: Decimal
    requires_followup: bool
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now() 