from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserUpdate, User
from app.services.user_service import UserService
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(user)

@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    db_user = service.get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/users/", response_model=list[User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_users(skip=skip, limit=limit)

@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    service = UserService(db)
    db_user = service.update_user(user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    db_user = service.delete_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
