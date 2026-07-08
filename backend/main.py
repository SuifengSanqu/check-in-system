import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import engine, Base
from routers import web_auth, web_accounts, web_records, miniapp
from services.scheduler import scheduler, schedule_all

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    os.makedirs("screenshots", exist_ok=True)
    scheduler.start()
    try:
        schedule_all()
    except Exception:
        pass
    yield
    scheduler.shutdown()


app = FastAPI(title="统一签到系统", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(web_auth.router, prefix="/api/web/auth", tags=["Web Auth"])
app.include_router(web_accounts.router, prefix="/api/web/accounts", tags=["Web Accounts"])
app.include_router(web_records.router, prefix="/api/web/records", tags=["Web Records"])
app.include_router(miniapp.router, prefix="/api/miniapp", tags=["MiniApp"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

