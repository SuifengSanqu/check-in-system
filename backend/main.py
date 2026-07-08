import os
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
HAVE_STATIC = os.path.isdir(STATIC_DIR) and os.path.isfile(os.path.join(STATIC_DIR, "index.html"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import engine, Base
    Base.metadata.create_all(bind=engine)
    data_dir = "/data" if os.path.isdir("/data") else "."
    os.makedirs(os.path.join(data_dir, "screenshots"), exist_ok=True)
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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

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


@app.get("/api/health")
def health():
    return {"status": "ok"}


if HAVE_STATIC:
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_spa(full_path: str):
        file_path = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
    @app.get("/")
    def root():
        return {"service": "check-in-system", "status": "running", "note": "Frontend not built"}
