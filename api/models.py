from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class User:
    telegram_id: int
    username: str
    joined_date: datetime
    email: Optional[str] = None
    last_active: Optional[datetime] = None

@dataclass
class Question:
    telegram_id: int
    question_text: str
    category: str
    status: str  # 'pending', 'answered', 'closed'
    created_at: datetime
    answered_at: Optional[datetime] = None
    answer_text: Optional[str] = None

@dataclass
class CVRequest:
    telegram_id: int
    email: str
    cv_type: str
    verification_code: str
    status: str
    request_date: datetime
    completion_date: Optional[datetime] = None
    linkedin_verified: bool = False

def to_dict(obj) -> Dict[str, Any]:
    """Convert dataclass instance to dictionary"""
    return {k: v for k, v in obj.__dict__.items() if v is not None}