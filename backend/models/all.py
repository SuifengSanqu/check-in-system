from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base


class WebUser(Base):
    __tablename__ = "web_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    nickname = Column(String(64), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    accounts = relationship("TargetAccount", back_populates="user", cascade="all, delete-orphan")


class TargetAccount(Base):
    __tablename__ = "target_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("web_users.id"), nullable=False)
    name = Column(String(128), nullable=False)
    site_url = Column(String(512), nullable=False)
    login_url = Column(String(512), nullable=False)
    login_username = Column(String(256), nullable=False)
    login_password = Column(Text, nullable=False)

    # --- Custom selectors for login form ---
    login_username_selector = Column(String(256), default="")
    login_password_selector = Column(String(256), default="")
    login_button_selector = Column(String(256), default="")
    # "single": username+password on same page; "two_step": username first, then password
    login_flow = Column(String(16), default="single")

    # --- Post-login & check-in ---
    checkin_nav_url = Column(String(512), default="")
    checkin_selector = Column(String(256), default="")
    checkin_text = Column(String(256), default="")
    # JSON array: [{"action":"click","selector":".foo"},{"action":"wait","ms":2000}]
    checkin_extra_steps = Column(Text, default="")

    # --- Popup / banner dismissal ---
    cookie_banner_selector = Column(String(256), default="")
    # JSON array of selectors
    popup_selectors = Column(Text, default="")

    # --- Scheduling ---
    time_window_start = Column(String(5), default="06:00")
    time_window_end = Column(String(5), default="22:00")
    enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("WebUser", back_populates="accounts")
    records = relationship("CheckInRecord", back_populates="account", cascade="all, delete-orphan")


class CheckInRecord(Base):
    __tablename__ = "checkin_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("target_accounts.id"), nullable=False)
    execute_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(16), default="success")
    error_message = Column(Text, default="")
    screenshot_path = Column(String(512), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    account = relationship("TargetAccount", back_populates="records")


class MiniAppUser(Base):
    __tablename__ = "miniapp_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(128), unique=True, nullable=False, index=True)
    nickname = Column(String(64), default="")
    avatar_url = Column(String(512), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    checkins = relationship("MiniAppCheckIn", back_populates="user", cascade="all, delete-orphan")


class MiniAppCheckIn(Base):
    __tablename__ = "miniapp_checkins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("miniapp_users.id"), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_in_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("MiniAppUser", back_populates="checkins")
