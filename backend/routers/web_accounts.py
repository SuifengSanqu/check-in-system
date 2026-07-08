from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.all import WebUser, TargetAccount
from utils.auth import get_web_user
from utils.crypto import encrypt, decrypt
from services.scheduler import run_manual_checkin

router = APIRouter()


class AccountCreate(BaseModel):
    name: str
    site_url: str
    login_url: str
    login_username: str
    login_password: str
    checkin_selector: str = ""
    checkin_text: str = ""
    time_window_start: str = "06:00"
    time_window_end: str = "22:00"
    enabled: bool = True


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    site_url: Optional[str] = None
    login_url: Optional[str] = None
    login_username: Optional[str] = None
    login_password: Optional[str] = None
    checkin_selector: Optional[str] = None
    checkin_text: Optional[str] = None
    time_window_start: Optional[str] = None
    time_window_end: Optional[str] = None
    enabled: Optional[bool] = None


def account_to_dict(account: TargetAccount) -> dict:
    return {
        "id": account.id,
        "user_id": account.user_id,
        "name": account.name,
        "site_url": account.site_url,
        "login_url": account.login_url,
        "login_username": account.login_username,
        "checkin_selector": account.checkin_selector,
        "checkin_text": account.checkin_text,
        "time_window_start": account.time_window_start,
        "time_window_end": account.time_window_end,
        "enabled": account.enabled,
        "created_at": account.created_at.isoformat() if account.created_at else None,
    }


@router.get("")
def list_accounts(user: WebUser = Depends(get_web_user), db: Session = Depends(get_db)):
    accounts = db.query(TargetAccount).filter(TargetAccount.user_id == user.id).all()
    return {"accounts": [account_to_dict(a) for a in accounts]}


@router.post("")
def create_account(req: AccountCreate, user: WebUser = Depends(get_web_user), db: Session = Depends(get_db)):
    account = TargetAccount(
        user_id=user.id,
        name=req.name,
        site_url=req.site_url,
        login_url=req.login_url,
        login_username=req.login_username,
        login_password=encrypt(req.login_password),
        checkin_selector=req.checkin_selector,
        checkin_text=req.checkin_text,
        time_window_start=req.time_window_start,
        time_window_end=req.time_window_end,
        enabled=req.enabled,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account_to_dict(account)


@router.get("/{account_id}")
def get_account(account_id: int, user: WebUser = Depends(get_web_user), db: Session = Depends(get_db)):
    account = db.query(TargetAccount).filter(
        TargetAccount.id == account_id,
        TargetAccount.user_id == user.id,
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account_to_dict(account)


@router.put("/{account_id}")
def update_account(
    account_id: int,
    req: AccountUpdate,
    user: WebUser = Depends(get_web_user),
    db: Session = Depends(get_db),
):
    account = db.query(TargetAccount).filter(
        TargetAccount.id == account_id,
        TargetAccount.user_id == user.id,
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = req.model_dump(exclude_unset=True)
    if "login_password" in update_data:
        update_data["login_password"] = encrypt(update_data["login_password"])

    for key, value in update_data.items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)
    return account_to_dict(account)


@router.delete("/{account_id}")
def delete_account(account_id: int, user: WebUser = Depends(get_web_user), db: Session = Depends(get_db)):
    account = db.query(TargetAccount).filter(
        TargetAccount.id == account_id,
        TargetAccount.user_id == user.id,
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"message": "Account deleted"}


@router.post("/{account_id}/run")
def run_account_checkin(account_id: int, user: WebUser = Depends(get_web_user), db: Session = Depends(get_db)):
    account = db.query(TargetAccount).filter(
        TargetAccount.id == account_id,
        TargetAccount.user_id == user.id,
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    result = run_manual_checkin(account_id)
    return result
