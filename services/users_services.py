from pydantic import BaseModel
from passlib.context import CryptContext
from schemas.users_schemas import UserInDB
import os
from fastapi import Depends
from dependencies import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

class TokenData(BaseModel):
    username: str | None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """Service class for user CRUD operations and business logic"""
    
    def __init__(self, db: dict):
        self.db = db
    
    # ==================== AUTHENTICATION METHODS ====================

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    # ==================== USER METHODS ====================

    def get_user(self, username: str):
        if username in self.db:
            user_dict = self.db[username]
            return UserInDB(**user_dict)

    def get_user_by_email(self, email: str):
        for user in self.db.values():
            if user.email == email:
                return UserInDB(**user)
        return None

    def get_all_users(self):
        return list(self.db.values())

    def create_user(self, user: UserInDB):
        self.db[user.username] = user.model_dump()
        return user

    def process_google_login(self, user_info: dict):

        user = self.get_user_by_email(user_info['email'])
        if not user:
            user = UserInDB(
                username=user_info['email'],
                email=user_info['email'],
                full_name=user_info['name'],
            )
            self.create_user(user)
        return user

# ==================== DEPENDENCY INJECTION ====================

def get_user_service(db: dict = Depends(get_db)) -> UserService:
    """Dependency injection for UserService"""
    return UserService(db)