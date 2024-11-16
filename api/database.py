from pymongo import MongoClient
from datetime import datetime
from typing import Optional, List, Dict, Any
from .models import User, Question, CVRequest, to_dict

class Database:
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db = self.client.cv_bot
        
        # Collections
        self.users = self.db.users
        self.questions = self.db.questions
        self.cv_requests = self.db.cv_requests
        
        # Create indexes
        self._setup_indexes()
    
    def _setup_indexes(self):
        """Setup database indexes"""
        # Users indexes
        self.users.create_index("telegram_id", unique=True)
        self.users.create_index("email")
        
        # Questions indexes
        self.questions.create_index("telegram_id")
        self.questions.create_index("status")
        self.questions.create_index("category")
        
        # CV requests indexes
        self.cv_requests.create_index("telegram_id")
        self.cv_requests.create_index("verification_code", unique=True)
        self.cv_requests.create_index([("telegram_id", 1), ("cv_type", 1)])
    
    # User operations
    def upsert_user(self, user: User) -> None:
        """Create or update user"""
        self.users.update_one(
            {"telegram_id": user.telegram_id},
            {"$set": to_dict(user)},
            upsert=True
        )
    
    def get_user(self, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID"""
        data = self.users.find_one({"telegram_id": telegram_id})
        return User(**data) if data else None
    
    def update_user_activity(self, telegram_id: int) -> None:
        """Update user's last active timestamp"""
        self.users.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"last_active": datetime.utcnow()}}
        )
    
    # Question operations
    def add_question(self, question: Question) -> str:
        """Add new question"""
        result = self.questions.insert_one(to_dict(question))
        return str(result.inserted_id)
    
    def get_user_questions(self, telegram_id: int) -> List[Question]:
        """Get all questions for a user"""
        return [
            Question(**q) 
            for q in self.questions.find({"telegram_id": telegram_id})
        ]
    
    def update_question(self, question_id: str, answer: str) -> None:
        """Update question with answer"""
        self.questions.update_one(
            {"_id": question_id},
            {
                "$set": {
                    "status": "answered",
                    "answer_text": answer,
                    "answered_at": datetime.utcnow()
                }
            }
        )
    
    # CV request operations
    def add_cv_request(self, cv_request: CVRequest) -> None:
        """Add new CV request"""
        self.cv_requests.insert_one(to_dict(cv_request))
    
    def get_cv_request(self, verification_code: str) -> Optional[CVRequest]:
        """Get CV request by verification code"""
        data = self.cv_requests.find_one({"verification_code": verification_code})
        return CVRequest(**data) if data else None
    
    def update_cv_request_status(
        self, 
        verification_code: str, 
        status: str,
        linkedin_verified: bool = False
    ) -> None:
        """Update CV request status"""
        update_data = {
            "status": status,
            "linkedin_verified": linkedin_verified
        }
        if status == "completed":
            update_data["completion_date"] = datetime.utcnow()
        
        self.cv_requests.update_one(
            {"verification_code": verification_code},
            {"$set": update_data}
        )
    
    def get_user_cv_requests(self, telegram_id: int) -> List[CVRequest]:
        """Get all CV requests for a user"""
        return [
            CVRequest(**r) 
            for r in self.cv_requests.find({"telegram_id": telegram_id})
        ]