"""抓取服务 - 执行爬虫任务并写入数据库"""
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Platform, Novel, NovelSnapshot, ScrapeTask
from ..scrapers.base import ScrapedNovel
from ..scrapers.registry import get_scraper

logger = logging.getLogger(__name__)


async def run_scrape_task(db: AsyncSession, platform_id: int, rank_type: str = "hot") -> ScrapeTask:
    platform = await db.get(Platform, platform_id)
    if not platform:
        raise ValueError(f"Platform {platform_id} not found")

    task = ScrapeTask(
        platform_id=platform_id,
        task_type="ranking",
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(task)
    await db.flush()

    scraper = get_scraper(platform.code)
    if not scraper:
        task.status = "failed"
        task.error_message = f"No scraper implemented for {platform.code}"
        task.finished_at = datetime.utcnow()
        await db.commit()
        return task

    try:
        results = await scraper.scrape_ranking(rank_type=rank_type)
        count = 0
        for item in results:
            count += await _upsert_novel(db, platform_id, item)
        task.items_scraped = count
        task.status = "success"
    except Exception as e:
        logger.exception(f"Scrape task failed for {platform.code}")
        task.status = "failed"
        task.error_message = str(e)
    finally:
        task.finished_at = datetime.utcnow()
        await scraper.close()

    await db.commit()
    return task


async def _upsert_novel(db: AsyncSession, platform_id: int, item: ScrapedNovel) -> int:
    stmt = select(Novel).where(
        Novel.platform_id == platform_id,
        Novel.title == item.title,
    )
    result = await db.execute(stmt)
    novel = result.scalar_one_or_none()

    if novel:
        novel.author = item.author or novel.author
        novel.cover_url = item.cover_url or novel.cover_url
        novel.description = item.description or novel.description
        novel.url = item.url or novel.url
        novel.genre = item.genre or novel.genre
        novel.status = item.status or novel.status
        novel.word_count = item.word_count or novel.word_count
        novel.chapter_count = item.chapter_count or novel.chapter_count
        novel.score = item.score or novel.score
        novel.rating_count = item.rating_count or novel.rating_count
        novel.review_count = item.review_count or novel.review_count
        novel.favorite_count = item.favorite_count or novel.favorite_count
        novel.view_count = item.view_count or novel.view_count
        novel.current_rank = item.rank
        novel.rank_type = item.rank_type
        novel.is_paid = item.is_paid
        novel.language = item.language or novel.language
        novel.updated_at = datetime.utcnow()
    else:
        novel = Novel(
            platform_id=platform_id,
            title=item.title,
            author=item.author,
            cover_url=item.cover_url,
            description=item.description,
            url=item.url,
            genre=item.genre,
            status=item.status,
            word_count=item.word_count,
            chapter_count=item.chapter_count,
            score=item.score,
            rating_count=item.rating_count,
            review_count=item.review_count,
            favorite_count=item.favorite_count,
            view_count=item.view_count,
            current_rank=item.rank,
            rank_type=item.rank_type,
            is_paid=item.is_paid,
            language=item.language,
        )
        db.add(novel)
        await db.flush()

    snapshot = NovelSnapshot(
        novel_id=novel.id,
        rank=item.rank,
        score=item.score,
        rating_count=item.rating_count,
        review_count=item.review_count,
        favorite_count=item.favorite_count,
        view_count=item.view_count,
        word_count=item.word_count,
        chapter_count=item.chapter_count,
    )
    db.add(snapshot)
    return 1
