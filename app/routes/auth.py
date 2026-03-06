from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.model import User
from app.schemas.tenant import UserCreate, Token
from app.core.auth import get_current_user
from app.core.security import hash_password, create_access_token, verify_password
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=Token)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user exists (Database level check)
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash and Save
    hashed = hash_password(user_data.password)
    new_user = User(
        name=user_data.name, 
        email=user_data.email, 
        password_hash=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 3. Return Token
    token = create_access_token({"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer", "message": "Signup successful!"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "message": "Login successful!"}


@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email
    }
