# app/repositories/user_repository.py

from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 10):
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, name: str, email: str):
        user = self.get_user(user_id)
        if user:
            user.name = name
            user.email = email
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, user_id: int):
        user = self.get_user(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
        return user
