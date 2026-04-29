"""平台管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.models import Platform, Novel
from ..schemas.schemas import PlatformOut, PlatformCreate, PlatformUpdate

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("", response_model=list[PlatformOut])
async def list_platforms(db: AsyncSession = Depends(get_db)):
    stmt = select(Platform).order_by(Platform.id)
    result = await db.execute(stmt)
    platforms = result.scalars().all()

    out = []
    for p in platforms:
        count_stmt = select(func.count()).select_from(Novel).where(Novel.platform_id == p.id)
        count_result = await db.execute(count_stmt)
        novel_count = count_result.scalar() or 0
        item = PlatformOut.model_validate(p)
        item.novel_count = novel_count
        out.append(item)
    return out


@router.get("/{platform_id}", response_model=PlatformOut)
async def get_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    platform = await db.get(Platform, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    count_stmt = select(func.count()).select_from(Novel).where(Novel.platform_id == platform_id)
    count_result = await db.execute(count_stmt)
    out = PlatformOut.model_validate(platform)
    out.novel_count = count_result.scalar() or 0
    return out


@router.post("", response_model=PlatformOut)
async def create_platform(body: PlatformCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Platform).where(Platform.code == body.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Platform code already exists")
    platform = Platform(**body.model_dump())
    db.add(platform)
    await db.commit()
    await db.refresh(platform)
    out = PlatformOut.model_validate(platform)
    out.novel_count = 0
    return out


@router.put("/{platform_id}", response_model=PlatformOut)
async def update_platform(platform_id: int, body: PlatformUpdate, db: AsyncSession = Depends(get_db)):
    platform = await db.get(Platform, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(platform, key, val)
    await db.commit()
    await db.refresh(platform)
    count_stmt = select(func.count()).select_from(Novel).where(Novel.platform_id == platform_id)
    count_result = await db.execute(count_stmt)
    out = PlatformOut.model_validate(platform)
    out.novel_count = count_result.scalar() or 0
    return out


@router.delete("/{platform_id}")
async def delete_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    platform = await db.get(Platform, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    await db.delete(platform)
    await db.commit()
    return {"ok": True}
