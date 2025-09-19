from schemas.users_schemas import UserUpdate
from fastapi import Depends
from database import get_db
from models.users_models import User, UserRole, UserSocialAccount
from sqlalchemy.orm import Session
from models.users_models import AuthProviderType
from uuid import UUID

class UserService:
    """Service class for user CRUD operations and business logic"""
    
    def __init__(self, db: Depends(get_db)):
        self.db = db

    # ==================== USER METHODS ====================

    def create_user(self, user: User):

        exists_user = self.get_user_by_email(user.email)
        if exists_user:
            return exists_user

        self.db.add(user)
        self.db.commit()
        return user

    def get_user(self, user_id: UUID):
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str):
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

    def delete_user(self, user: User):
        self.db.delete(user)
        self.db.commit()
        return user

    def get_user_social_accounts(self, user: User):
        return user.social_accounts

    def get_user_social_account(self, provider_id: str):
        return self.db.query(UserSocialAccount).filter(UserSocialAccount.provider_id == provider_id).first()

    def make_user_admin(self, user: User):
        user.role = UserRole.ADMIN
        self.db.commit()
        self.db.refresh(user)
        return user

    def _create_user_social_account(self, user_social_account: UserSocialAccount):
        self.db.add(user_social_account)
        self.db.commit()
        self.db.refresh(user_social_account)
        return user_social_account

    def process_google_login(self, user_info: dict):

        print(user_info)

        user = self.get_user_by_email(user_info['email'])
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

        user_social_account = self.get_user_social_account(user_info['sub'])
        if not user_social_account:
            user_social_account = UserSocialAccount(
                user_id=user.id,
                provider=AuthProviderType.GOOGLE,
                provider_id=user_info['sub'],
                email=user_info['email'],
                is_verified=user_info['email_verified'],
                name=user_info['name'],
                given_name=user_info['given_name'],
                family_name=user_info['family_name'],
                picture=user_info['picture'],
            )
            self._create_user_social_account(user_social_account)
            
        else:
            user_social_account.update_last_used()
            self.db.commit()

        return user

# ==================== DEPENDENCY INJECTION ====================

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency injection for UserService"""
    return UserService(db)