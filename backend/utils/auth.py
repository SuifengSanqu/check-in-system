from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import JWT_SECRET_WEB, JWT_SECRET_MINIAPP, JWT_ALGORITHM, JWT_EXPIRE_HOURS
from database import get_db
from models.all import WebUser, MiniAppUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/web/auth/login")


def create_web_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {"user_id": user_id, "exp": expire, "type": "web"}
    return jwt.encode(payload, JWT_SECRET_WEB, algorithm=JWT_ALGORITHM)


def create_miniapp_token(openid: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {"openid": openid, "exp": expire, "type": "miniapp"}
    return jwt.encode(payload, JWT_SECRET_MINIAPP, algorithm=JWT_ALGORITHM)


async def get_web_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> WebUser:
    try:
        payload = jwt.decode(token, JWT_SECRET_WEB, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "web":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("user_id")
        user = db.query(WebUser).filter(WebUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_miniapp_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> MiniAppUser:
    try:
        payload = jwt.decode(token, JWT_SECRET_MINIAPP, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "miniapp":
            raise HTTPException(status_code=401, detail="Invalid token type")
        openid = payload.get("openid")
        user = db.query(MiniAppUser).filter(MiniAppUser.openid == openid).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
