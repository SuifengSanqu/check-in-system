import sqlite3
from config import DATABASE_URL


_TARGET_ACCOUNT_COLUMNS = {
    "login_username_selector": "VARCHAR(256) DEFAULT ''",
    "login_password_selector": "VARCHAR(256) DEFAULT ''",
    "login_button_selector": "VARCHAR(256) DEFAULT ''",
    "login_flow": "VARCHAR(16) DEFAULT 'single'",
    "checkin_nav_url": "VARCHAR(512) DEFAULT ''",
    "checkin_extra_steps": "TEXT DEFAULT ''",
    "cookie_banner_selector": "VARCHAR(256) DEFAULT ''",
    "popup_selectors": "TEXT DEFAULT ''",
}


def run_migrations():
    if not DATABASE_URL.startswith("sqlite:///"):
        return

    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='target_accounts'")
    if not cursor.fetchone():
        conn.close()
        return

    cursor.execute("PRAGMA table_info(target_accounts)")
    existing = {row[1] for row in cursor.fetchall()}

    for col_name, col_def in _TARGET_ACCOUNT_COLUMNS.items():
        if col_name not in existing:
            cursor.execute(f"ALTER TABLE target_accounts ADD COLUMN {col_name} {col_def}")

    conn.commit()
    conn.close()
