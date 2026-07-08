import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import engine, Base
    Base.metadata.create_all(bind=engine)
    os.makedirs("screenshots", exist_ok=True)
    try:
        from services.scheduler import scheduler, schedule_all
        scheduler.start()
        schedule_all()
    except Exception as e:
        print(f"[startup] scheduler skipped: {e}", flush=True)
    yield
    try:
        from services.scheduler import scheduler
        scheduler.shutdown()
    except Exception:
        pass


app = FastAPI(title="统一签到系统", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import web_auth, web_accounts, web_records, miniapp
app.include_router(web_auth.router, prefix="/api/web/auth", tags=["Web Auth"])
app.include_router(web_accounts.router, prefix="/api/web/accounts", tags=["Web Accounts"])
app.include_router(web_records.router, prefix="/api/web/records", tags=["Web Records"])
app.include_router(miniapp.router, prefix="/api/miniapp", tags=["MiniApp"])


@app.get("/")
def root():
    return {"service": "check-in-system", "status": "running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


if os.path.isdir(STATIC_DIR) and os.path.isfile(os.path.join(STATIC_DIR, "index.html")):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/app/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
