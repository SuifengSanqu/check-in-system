import random
import json
import subprocess
import os
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from database import SessionLocal
from models.all import TargetAccount, CheckInRecord
from utils.crypto import decrypt

scheduler = BackgroundScheduler()

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")
if os.path.isdir("/data"):
    SCREENSHOTS_DIR = "/data/screenshots"


def schedule_all():
    scheduler.remove_all_jobs()

    db: Session = SessionLocal()
    try:
        from models.all import WebUser
        users = db.query(WebUser).all()
        for user in users:
            accounts = db.query(TargetAccount).filter(
                TargetAccount.user_id == user.id,
                TargetAccount.enabled == True,
            ).all()
            if not accounts:
                continue

            start_min = _parse_time(accounts[0].time_window_start)
            end_min = _parse_time(accounts[0].time_window_end)
            pool = list(range(start_min, end_min))

            if len(pool) < len(accounts):
                pool = [random.randint(start_min, end_min - 1) for _ in range(len(accounts))]
            else:
                pool = random.sample(pool, len(accounts))

            for account, minute in zip(accounts, pool):
                h, m = minute // 60, minute % 60
                scheduler.add_job(
                    func=execute_checkin,
                    trigger=CronTrigger(hour=h, minute=m),
                    args=[account.id],
                    id=f"checkin_{account.id}",
                    replace_existing=True,
                )
    finally:
        db.close()


def execute_checkin(account_id: int):
    db: Session = SessionLocal()
    try:
        account = db.query(TargetAccount).filter(TargetAccount.id == account_id).first()
        if not account:
            return

        today = datetime.now(timezone.utc).date()
        existing = db.query(CheckInRecord).filter(
            CheckInRecord.account_id == account_id,
        ).all()
        for r in existing:
            if r.execute_time and r.execute_time.date() == today and r.status == "success":
                return

        task_config = _build_random_config()

        params = {
            "login_url": account.login_url,
            "username": account.login_username,
            "password": decrypt(account.login_password),
            "checkin_selector": account.checkin_selector,
            "checkin_text": account.checkin_text,
            "random_config": task_config,
        }

        script_path = os.path.join(SCRIPTS_DIR, "checkin.js")
        env = os.environ.copy()
        env["NODE_PATH"] = "/usr/local/lib/node_modules"
        result = subprocess.run(
            ["node", script_path],
            input=json.dumps(params),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        if result.returncode == 0:
            output = json.loads(result.stdout)
            record = CheckInRecord(
                account_id=account_id,
                status=output.get("status", "success"),
                error_message=output.get("error", ""),
                screenshot_path=output.get("screenshot_path", ""),
            )
        else:
            record = CheckInRecord(
                account_id=account_id,
                status="failed",
                error_message=result.stderr[:500] if result.stderr else "Script execution failed",
            )

        db.add(record)
        db.commit()

        if record.status == "failed":
            _retry_checkin(account_id)

    except subprocess.TimeoutExpired:
        record = CheckInRecord(account_id=account_id, status="failed", error_message="Execution timeout (120s)")
        db.add(record)
        db.commit()
    except Exception as e:
        record = CheckInRecord(account_id=account_id, status="failed", error_message=str(e)[:500])
        db.add(record)
        db.commit()
    finally:
        db.close()


def _retry_checkin(account_id: int):
    delay_minutes = random.randint(5, 30)
    scheduler.add_job(
        func=execute_checkin,
        trigger=CronTrigger(minute=f"*/{delay_minutes}"),
        args=[account_id],
        id=f"retry_checkin_{account_id}",
        replace_existing=True,
        misfire_grace_time=60,
    )


def run_manual_checkin(account_id: int) -> dict:
    db: Session = SessionLocal()
    try:
        account = db.query(TargetAccount).filter(TargetAccount.id == account_id).first()
        if not account:
            return {"status": "error", "message": "Account not found"}

        task_config = _build_random_config()
        params = {
            "login_url": account.login_url,
            "username": account.login_username,
            "password": decrypt(account.login_password),
            "checkin_selector": account.checkin_selector,
            "checkin_text": account.checkin_text,
            "random_config": task_config,
        }

        script_path = os.path.join(SCRIPTS_DIR, "checkin.js")

        env = os.environ.copy()
        env["NODE_PATH"] = "/usr/local/lib/node_modules"
        result = subprocess.run(
            ["node", script_path],
            input=json.dumps(params),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        if result.returncode == 0:
            output = json.loads(result.stdout)
            record = CheckInRecord(
                account_id=account_id,
                status=output.get("status", "success"),
                error_message=output.get("error", ""),
                screenshot_path=output.get("screenshot_path", ""),
            )
        else:
            record = CheckInRecord(
                account_id=account_id,
                status="failed",
                error_message=result.stderr[:500] if result.stderr else "Script execution failed",
            )

        db.add(record)
        db.commit()

        return {
            "status": record.status,
            "error": record.error_message,
            "execute_time": record.execute_time.isoformat() if record.execute_time else None,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Execution timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


REAL_UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]


def _build_random_config() -> dict:
    return {
        "viewport": random.choice([
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900},
        ]),
        "user_agent": random.choice(REAL_UA_LIST),
        "typing_delay_min": 50,
        "typing_delay_max": 250,
        "click_delay_min": 300,
        "click_delay_max": 2000,
        "page_wait_min": 1000,
        "page_wait_max": 5000,
        "scroll_steps_min": 3,
        "scroll_steps_max": 8,
        "mouse_steps_min": 20,
        "mouse_steps_max": 40,
    }


def _parse_time(t: str) -> int:
    parts = t.split(":")
    return int(parts[0]) * 60 + int(parts[1])
