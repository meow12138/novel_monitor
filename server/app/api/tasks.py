"""抓取任务 API"""
from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db, async_session
from ..models.models import ScrapeTask, Platform
from ..schemas.schemas import ScrapeTaskOut, PageResult
from ..services.scrape_service import run_scrape_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=PageResult)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform_id: int | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ScrapeTask).join(Platform)

    if platform_id:
        stmt = stmt.where(ScrapeTask.platform_id == platform_id)
    if status:
        stmt = stmt.where(ScrapeTask.status == status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(desc(ScrapeTask.created_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    items = []
    for t in tasks:
        out = ScrapeTaskOut.model_validate(t)
        out.platform_name = t.platform.name if t.platform else ""
        items.append(out)

    return PageResult(items=items, total=total, page=page, page_size=page_size)


async def _run_task_bg(platform_id: int, rank_type: str):
    async with async_session() as db:
        await run_scrape_task(db, platform_id, rank_type)


@router.post("/run")
async def trigger_scrape(
    platform_id: int,
    rank_type: str = "hot",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    platform = await db.get(Platform, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    if not platform.enabled:
        raise HTTPException(status_code=400, detail="Platform is disabled")

    background_tasks.add_task(_run_task_bg, platform_id, rank_type)
    return {"ok": True, "message": f"Scrape task started for {platform.name}"}


@router.post("/run-all")
async def trigger_scrape_all(
    rank_type: str = "hot",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Platform).where(Platform.enabled == True, Platform.scraper_class != "")
    result = await db.execute(stmt)
    platforms = result.scalars().all()

    started = []
    for p in platforms:
        background_tasks.add_task(_run_task_bg, p.id, rank_type)
        started.append(p.name)

    return {"ok": True, "message": f"Started scrape for: {', '.join(started)}"}
