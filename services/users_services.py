from passlib.context import CryptContext
from schemas.users_schemas import UserUpdate
from fastapi import Depends
from dependencies import get_db
from models.users_models import User
from sqlalchemy.orm import Session

class UserService:
    """Service class for user CRUD operations and business logic"""
    
    def __init__(self, db: Depends(get_db)):
        self.db = db

    # ==================== USER METHODS ====================

    def create_user(self, email: str):

        exists_user = self.get_user(email)
        if exists_user:
            return exists_user

        user = User(email=email)
        user = self.db.add(user)
        self.db.commit()
        return user
    
    def get_user(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_all_users(self):
        return self.db.query(User).filter(User.disabled == False).all()

    def update_user(self, user: User, user_update: UserUpdate):
        user_update = user_update.model_dump(exclude_unset=True)
        for key, value in user_update.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)

        return user

    def process_google_login(self, user_info: dict):

        user = self.get_user(user_info['email'])
        if not user:
            user = User(
                email=user_info['email'],
                full_name=user_info['name'],
                given_name=user_info['given_name'],
                family_name=user_info['family_name'],
                picture=user_info['picture'],
            )
            self.create_user(user)
        else:
            user_update = UserUpdate(
                full_name=user.full_name or user_info['name'] ,
                given_name=user.given_name or user_info['given_name'] ,
                family_name=user.family_name or user_info['family_name'] ,
                picture=user.picture or user_info['picture'],
            )
            self.update_user(user, user_update)
        return user

# ==================== DEPENDENCY INJECTION ====================

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency injection for UserService"""
    return UserService(db)