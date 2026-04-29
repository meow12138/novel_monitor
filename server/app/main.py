"""FastAPI 应用入口"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .core.database import init_db, async_session
from .api import platforms, novels, tasks, dashboard
from .services.scheduler import start_scheduler, stop_scheduler
from .services.seed import seed_platforms

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "web" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with async_session() as db:
        await seed_platforms(db)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Novel Monitor - 海外爆款小说监控系统",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api")
app.include_router(platforms.router, prefix="/api")
app.include_router(novels.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
