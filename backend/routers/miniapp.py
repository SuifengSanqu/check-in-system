from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, datetime, timezone

from database import get_db
from models.all import MiniAppUser, MiniAppCheckIn
from utils.auth import create_miniapp_token, get_miniapp_user
from config import WECHAT_APPID, WECHAT_SECRET

router = APIRouter()


class WeChatLoginRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    token: str
    user: dict


@router.post("/auth/login", response_model=TokenResponse)
def wechat_login(req: WeChatLoginRequest, db: Session = Depends(get_db)):
    if WECHAT_APPID and WECHAT_SECRET:
        import requests
        resp = requests.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": WECHAT_APPID,
                "secret": WECHAT_SECRET,
                "js_code": req.code,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        data = resp.json()
        if "errcode" in data and data["errcode"] != 0:
            raise HTTPException(status_code=400, detail=f"WeChat login failed: {data.get('errmsg')}")
        openid = data["openid"]
    else:
        openid = f"test_openid_{req.code}"

    user = db.query(MiniAppUser).filter(MiniAppUser.openid == openid).first()
    if not user:
        user = MiniAppUser(openid=openid, nickname="微信用户")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_miniapp_token(openid)
    return TokenResponse(
        token=token,
        user={"id": user.id, "nickname": user.nickname, "avatar_url": user.avatar_url},
    )


@router.post("/checkin")
def do_checkin(user: MiniAppUser = Depends(get_miniapp_user), db: Session = Depends(get_db)):
    today = date.today()
    existing = db.query(MiniAppCheckIn).filter(
        MiniAppCheckIn.user_id == user.id,
        MiniAppCheckIn.check_in_date == today,
    ).first()

    if existing:
        consecutive = _calc_consecutive(user.id, db)
        return {"already_checked_in": True, "consecutive_days": consecutive, "check_in_time": existing.check_in_time.isoformat()}

    record = MiniAppCheckIn(user_id=user.id, check_in_date=today, check_in_time=datetime.now(timezone.utc))
    db.add(record)
    db.commit()

    consecutive = _calc_consecutive(user.id, db)
    total = db.query(MiniAppCheckIn).filter(MiniAppCheckIn.user_id == user.id).count()

    return {
        "already_checked_in": False,
        "consecutive_days": consecutive,
        "total_days": total,
        "check_in_time": record.check_in_time.isoformat(),
    }


@router.get("/checkin/today")
def get_today_status(user: MiniAppUser = Depends(get_miniapp_user), db: Session = Depends(get_db)):
    today = date.today()
    record = db.query(MiniAppCheckIn).filter(
        MiniAppCheckIn.user_id == user.id,
        MiniAppCheckIn.check_in_date == today,
    ).first()

    consecutive = _calc_consecutive(user.id, db)
    return {
        "checked_in": record is not None,
        "check_in_time": record.check_in_time.isoformat() if record else None,
        "consecutive_days": consecutive,
    }


@router.get("/checkin/calendar")
def get_calendar(year: int, month: int, user: MiniAppUser = Depends(get_miniapp_user), db: Session = Depends(get_db)):
    from calendar import monthrange
    import datetime as dt

    _, last_day = monthrange(year, month)
    start = dt.date(year, month, 1)
    end = dt.date(year, month, last_day)

    records = db.query(MiniAppCheckIn).filter(
        MiniAppCheckIn.user_id == user.id,
        MiniAppCheckIn.check_in_date >= start,
        MiniAppCheckIn.check_in_date <= end,
    ).all()

    checked_dates = {r.check_in_date.day for r in records}
    return {"year": year, "month": month, "checked_days": sorted(checked_dates)}


@router.get("/records")
def list_records(
    limit: int = 30,
    user: MiniAppUser = Depends(get_miniapp_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(MiniAppCheckIn)
        .filter(MiniAppCheckIn.user_id == user.id)
        .order_by(MiniAppCheckIn.check_in_date.desc())
        .limit(limit)
        .all()
    )
    return {
        "records": [
            {
                "id": r.id,
                "check_in_date": r.check_in_date.isoformat(),
                "check_in_time": r.check_in_time.isoformat() if r.check_in_time else None,
            }
            for r in records
        ]
    }


def _calc_consecutive(user_id: int, db: Session) -> int:
    records = (
        db.query(MiniAppCheckIn)
        .filter(MiniAppCheckIn.user_id == user_id)
        .order_by(MiniAppCheckIn.check_in_date.desc())
        .all()
    )
    if not records:
        return 0

    today = date.today()
    if records[0].check_in_date < today:
        return 0

    count = 1
    for i in range(len(records) - 1):
        diff = (records[i].check_in_date - records[i + 1].check_in_date).days
        if diff == 1:
            count += 1
        else:
            break
    return count
