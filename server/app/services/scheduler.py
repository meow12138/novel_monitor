"""定时任务调度"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from ..core.config import SCRAPE_INTERVAL_MINUTES
from ..core.database import async_session
from ..models.models import Platform
from ..services.scrape_service import run_scrape_task

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scheduled_scrape_all():
    logger.info("Scheduled scrape starting...")
    async with async_session() as db:
        stmt = select(Platform).where(Platform.enabled == True, Platform.scraper_class != "")
        result = await db.execute(stmt)
        platforms = result.scalars().all()

        for p in platforms:
            try:
                task = await run_scrape_task(db, p.id, rank_type="hot")
                logger.info(f"Scheduled scrape [{p.name}]: {task.status}, items={task.items_scraped}")
            except Exception:
                logger.exception(f"Scheduled scrape failed for {p.name}")


def start_scheduler():
    scheduler.add_job(
        scheduled_scrape_all,
        trigger=IntervalTrigger(minutes=SCRAPE_INTERVAL_MINUTES),
        id="scrape_all",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started, interval={SCRAPE_INTERVAL_MINUTES}min")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
