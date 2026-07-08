from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from models.all import WebUser, CheckInRecord
from utils.auth import get_web_user

router = APIRouter()


@router.get("")
def list_records(
    account_id: int = None,
    from_date: str = None,
    to_date: str = None,
    user: WebUser = Depends(get_web_user),
    db: Session = Depends(get_db),
):
    query = db.query(CheckInRecord).join(CheckInRecord.account).filter(
        CheckInRecord.account.has(user_id=user.id)
    )

    if account_id:
        query = query.filter(CheckInRecord.account_id == account_id)
    if from_date:
        query = query.filter(CheckInRecord.execute_time >= from_date)
    if to_date:
        query = query.filter(CheckInRecord.execute_time <= to_date + " 23:59:59")

    records = query.order_by(CheckInRecord.execute_time.desc()).limit(100).all()
    return {
        "records": [
            {
                "id": r.id,
                "account_id": r.account_id,
                "account_name": r.account.name if r.account else "",
                "execute_time": r.execute_time.isoformat() if r.execute_time else None,
                "status": r.status,
                "error_message": r.error_message,
                "screenshot_path": r.screenshot_path,
            }
            for r in records
        ]
    }


@router.get("/stats")
def get_stats(user: WebUser = Depends(get_web_user), db: Session = Depends(get_db)):
    records = db.query(CheckInRecord).join(CheckInRecord.account).filter(
        CheckInRecord.account.has(user_id=user.id)
    ).all()

    total = len(records)
    success = len([r for r in records if r.status == "success"])
    failed = len([r for r in records if r.status == "failed"])

    today_records = [r for r in records if r.execute_time and r.execute_time.date() == date.today()]
    today_success = len([r for r in today_records if r.status == "success"])

    return {
        "total": total,
        "success": success,
        "failed": failed,
        "today_total": len(today_records),
        "today_success": today_success,
    }
