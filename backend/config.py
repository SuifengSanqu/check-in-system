import os

if os.path.isdir("/data") and os.access("/data", os.W_OK):
    DATA_DIR = "/data"
else:
    DATA_DIR = "."

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/checkin.db")
JWT_SECRET_WEB = os.getenv("JWT_SECRET_WEB", "web-secret-key-change-in-production")
JWT_SECRET_MINIAPP = os.getenv("JWT_SECRET_MINIAPP", "miniapp-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

AES_KEY = os.getenv("AES_KEY", "0123456789abcdef0123456789abcdef").encode()

WECHAT_APPID = os.getenv("WECHAT_APPID", "")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")

DEFAULT_TIME_WINDOW_START = "06:00"
DEFAULT_TIME_WINDOW_END = "22:00"
