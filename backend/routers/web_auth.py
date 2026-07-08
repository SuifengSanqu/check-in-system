from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from passlib.context import CryptContext

from database import get_db
from models.all import WebUser
from utils.auth import create_web_token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: str = ""

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 64:
            raise ValueError("Username must be 3-64 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    user: dict


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(WebUser).filter(WebUser.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = WebUser(
        username=req.username,
        password_hash=pwd_context.hash(req.password),
        nickname=req.nickname or req.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_web_token(user.id)
    return TokenResponse(token=token, user={"id": user.id, "username": user.username, "nickname": user.nickname})


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(WebUser).filter(WebUser.username == req.username).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_web_token(user.id)
    return TokenResponse(token=token, user={"id": user.id, "username": user.username, "nickname": user.nickname})
