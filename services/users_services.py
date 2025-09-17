from passlib.context import CryptContext
from schemas.users_schemas import UserInDB, UserUpdate, UserCreate
from fastapi import Depends
from dependencies import get_db

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

    def create_user(self, user: UserCreate):
        self.db[user.username] = UserInDB(
            username=user.username,
            hashed_password=self.get_password_hash(user.password),
        ).model_dump()
        return user
    
    def get_user(self, username: str):
        if username in self.db:
            user_dict = self.db[username]
            return UserInDB(**user_dict)

    def get_all_users(self):
        return list(self.db.values())

    def update_user(self, user: UserInDB, user_update: UserUpdate):
        user_update = user_update.model_dump(exclude_unset=True)
        for key, value in user_update.items():
            self.db[user.username][key] = value
        return self.db[user.username]

    def process_google_login(self, user_info: dict):

        user = self.get_user(user_info['email'])
        if not user:
            user = UserInDB(
                username=user_info['email'],
                full_name=user_info['name'],
                given_name=user_info['given_name'],
                family_name=user_info['family_name'],
                email_verified=user_info['email_verified'],
                picture=user_info['picture'],
            )
            self._create_user_sso(user)
        else:
            user_update = UserUpdate(
                full_name=user.full_name or user_info['name'] ,
                given_name=user.given_name or user_info['given_name'] ,
                family_name=user.family_name or user_info['family_name'] ,
                picture=user.picture or user_info['picture'],
            )
            self.update_user(user, user_update)
        return user

    def _create_user_sso(self, user: UserInDB):
        self.db[user.username] = user.model_dump()
        return user

# ==================== DEPENDENCY INJECTION ====================

def get_user_service(db: dict = Depends(get_db)) -> UserService:
    """Dependency injection for UserService"""
    return UserService(db)