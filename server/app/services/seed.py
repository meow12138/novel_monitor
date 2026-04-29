"""初始化种子数据 - 预置平台信息"""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Platform
from ..scrapers.registry import DEFAULT_PLATFORMS

logger = logging.getLogger(__name__)


async def seed_platforms(db: AsyncSession):
    for pdata in DEFAULT_PLATFORMS:
        existing = await db.execute(
            select(Platform).where(Platform.code == pdata["code"])
        )
        if existing.scalar_one_or_none():
            continue
        platform = Platform(
            name=pdata["name"],
            code=pdata["code"],
            website=pdata["website"],
            region=pdata["region"],
            category=pdata["category"],
            scraper_class=pdata["scraper_class"],
            description=pdata["description"],
            enabled=bool(pdata["scraper_class"]),
        )
        db.add(platform)
        logger.info(f"Seeded platform: {pdata['name']}")

    await db.commit()
