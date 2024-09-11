from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.controllers.user_controller import router as user_router
from app.database import Base, engine, SessionLocal
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService
from sqlalchemy.exc import IntegrityError
from app.models.user import User as UserModel
import os

app = FastAPI()

templates_directory = os.path.join(os.path.dirname(__file__), 'templates')
templates = Jinja2Templates(directory=templates_directory)

Base.metadata.create_all(bind=engine)

app.include_router(user_router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    return int(user_id)  

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "users": users})

@app.get("/register", response_class=HTMLResponse)
async def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    service = UserService(db)
    user_create = UserCreate(name=name, email=email, password=password)
    try:
        user = service.create_user(user_create)
    except HTTPException as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e.detail)})
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": "An unexpected error occurred. Please try again."})
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/signup", response_class=HTMLResponse)
async def get_create_user_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse)
async def create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    service = UserService(db)
    user_create = UserCreate(name=name, email=email, password=password)
    try:
        user = service.create_user(user_create)
    except HTTPException as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": str(e.detail)})
    except Exception as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "An unexpected error occurred. Please try again."})
    
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/register")

@app.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    service = UserService(db)
    try:
        user = service.authenticate_user(email, password)
        if user:
            response = RedirectResponse(url="/dashboard", status_code=303)
            response.set_cookie(key="user_id", value=str(user.id))  
            return response
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": str(e.detail)})

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def read_profile(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")  

    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    service = UserService(db)
    user = service.get_user(int(user_id)) 
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="user_id")  
    return response

@app.put("/users/{user_id}", response_class=HTMLResponse)
async def update_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    name = form.get('name')
    email = form.get('email')
    password = form.get('password')

    user_update = UserUpdate(name=name, email=email, password=password)
    service = UserService(db)

    try:
        updated_user = service.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/user/update/{user_id}", response_class=HTMLResponse)
async def update_user_view(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("update_user.html", {"request": request, "user": user})

@app.post("/user/update/{user_id}")
async def update_user(user_id: int, name: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = name
    user.email = email
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/user/delete/{user_id}", response_class=HTMLResponse)
async def delete_user_view(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("confirm_delete.html", {"request": request, "user": user})

@app.post("/user/delete/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {"request": request, "detail": exc.detail}, status_code=exc.status_code)

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return templates.TemplateResponse("error.html", {"request": request, "detail": "A database integrity error occurred. Please check your input and try again."}, status_code=500)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("error.html", {"request": request, "detail": "An unexpected error occurred. Please try again later."}, status_code=500)
