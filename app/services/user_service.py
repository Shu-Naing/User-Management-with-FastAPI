import bcrypt
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Hash a plain password."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_user(self, user_create: UserCreate) -> UserModel:
        """Create a new user with hashed password and handle duplicate emails."""
        hashed_password = self.hash_password(user_create.password)
        db_user = UserModel(
            name=user_create.name,
            email=user_create.email,
            password=hashed_password
        )
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Email already registered")
        return db_user

    def get_user(self, user_id: int) -> UserModel:
        """Retrieve a user by ID."""
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_users(self, skip: int = 0, limit: int = 10) -> list[UserModel]:
        """Retrieve a list of users with pagination."""
        return self.db.query(UserModel).offset(skip).limit(limit).all()

    def update_user(self, user_id: int, user_update: UserUpdate) -> UserModel:
        """Update user details."""
        db_user = self.get_user(user_id)
        if db_user:
            if user_update.name:
                db_user.name = user_update.name
            if user_update.email:
                db_user.email = user_update.email
            if user_update.password:
                db_user.password = self.hash_password(user_update.password)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        else:
            raise HTTPException(status_code=404, detail="User not found")

    def delete_user(self, user_id: int) -> UserModel:
        """Delete a user by ID."""
        db_user = self.get_user(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return db_user
        else:
            raise HTTPException(status_code=404, detail="User not found")

    def authenticate_user(self, email: str, password: str) -> UserModel:
        """Authenticate a user with email and password."""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not db_user or not self.verify_password(password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return db_user
