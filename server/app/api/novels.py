"""小说管理 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.database import get_db
from ..models.models import Novel, Platform, NovelSnapshot
from ..schemas.schemas import NovelOut, NovelDetail, PageResult

router = APIRouter(prefix="/novels", tags=["novels"])


@router.get("", response_model=PageResult)
async def list_novels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform_id: int | None = None,
    rank_type: str | None = None,
    genre: str | None = None,
    keyword: str | None = None,
    sort_by: str = "current_rank",
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Novel).join(Platform)

    if platform_id:
        stmt = stmt.where(Novel.platform_id == platform_id)
    if rank_type:
        stmt = stmt.where(Novel.rank_type == rank_type)
    if genre:
        stmt = stmt.where(Novel.genre.ilike(f"%{genre}%"))
    if keyword:
        stmt = stmt.where(
            Novel.title.ilike(f"%{keyword}%") | Novel.author.ilike(f"%{keyword}%")
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    sort_col = getattr(Novel, sort_by, Novel.current_rank)
    if sort_by in ("score", "view_count", "favorite_count", "review_count"):
        stmt = stmt.order_by(desc(sort_col))
    else:
        stmt = stmt.order_by(sort_col)

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    novels = result.scalars().all()

    items = []
    for n in novels:
        out = NovelOut.model_validate(n)
        out.platform_name = n.platform.name if n.platform else ""
        items.append(out)

    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.get("/ranking")
async def get_ranking(
    platform_id: int | None = None,
    rank_type: str = "hot",
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Novel).join(Platform).where(Novel.current_rank.isnot(None))

    if platform_id:
        stmt = stmt.where(Novel.platform_id == platform_id)
    if rank_type:
        stmt = stmt.where(Novel.rank_type == rank_type)

    stmt = stmt.order_by(Novel.current_rank).limit(limit)
    result = await db.execute(stmt)
    novels = result.scalars().all()

    items = []
    for n in novels:
        out = NovelOut.model_validate(n)
        out.platform_name = n.platform.name if n.platform else ""
        items.append(out)
    return items


@router.get("/{novel_id}", response_model=NovelDetail)
async def get_novel(novel_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Novel)
        .options(selectinload(Novel.snapshots))
        .where(Novel.id == novel_id)
    )
    result = await db.execute(stmt)
    novel = result.scalar_one_or_none()
    if not novel:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Novel not found")

    out = NovelDetail.model_validate(novel)
    out.platform_name = novel.platform.name if novel.platform else ""
    out.snapshots.sort(key=lambda s: s.snapshot_time)
    return out
