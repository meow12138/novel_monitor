"""仪表盘 API"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.models import Novel, Platform, ScrapeTask
from ..schemas.schemas import DashboardStats, ScrapeTaskOut, NovelOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    total_novels = (await db.execute(select(func.count()).select_from(Novel))).scalar() or 0
    total_platforms = (await db.execute(select(func.count()).select_from(Platform))).scalar() or 0
    active_platforms = (await db.execute(
        select(func.count()).select_from(Platform).where(Platform.enabled == True)
    )).scalar() or 0

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_scraped = (await db.execute(
        select(func.coalesce(func.sum(ScrapeTask.items_scraped), 0))
        .where(ScrapeTask.created_at >= today_start, ScrapeTask.status == "success")
    )).scalar() or 0

    task_stmt = select(ScrapeTask).join(Platform).order_by(desc(ScrapeTask.created_at)).limit(10)
    task_result = await db.execute(task_stmt)
    recent_tasks = []
    for t in task_result.scalars().all():
        out = ScrapeTaskOut.model_validate(t)
        out.platform_name = t.platform.name if t.platform else ""
        recent_tasks.append(out)

    novel_stmt = (
        select(Novel).join(Platform)
        .where(Novel.current_rank.isnot(None))
        .order_by(Novel.current_rank)
        .limit(10)
    )
    novel_result = await db.execute(novel_stmt)
    top_novels = []
    for n in novel_result.scalars().all():
        out = NovelOut.model_validate(n)
        out.platform_name = n.platform.name if n.platform else ""
        top_novels.append(out)

    return DashboardStats(
        total_novels=total_novels,
        total_platforms=total_platforms,
        active_platforms=active_platforms,
        today_scraped=today_scraped,
        recent_tasks=recent_tasks,
        top_novels=top_novels,
    )
