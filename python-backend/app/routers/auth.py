from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
from ..database import SessionLocal
from ..models.user import User, UserRole
from ..auth import authenticate_user, create_access_token, get_password_hash, get_current_user

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role: str = "PATIENT"

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)})  # Ensure sub is a string
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Token)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        password=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
        role=UserRole(request.role),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token(data={"sub": str(user.id)})  # Ensure sub is a string
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

