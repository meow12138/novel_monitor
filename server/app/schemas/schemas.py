from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ---- Platform ----

class PlatformBase(BaseModel):
    name: str
    code: str
    website: Optional[str] = None
    region: Optional[str] = None
    category: Optional[str] = None
    enabled: bool = True
    scraper_class: Optional[str] = None
    description: Optional[str] = None


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    region: Optional[str] = None
    category: Optional[str] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None


class PlatformOut(PlatformBase):
    id: int
    created_at: datetime
    updated_at: datetime
    novel_count: int = 0

    model_config = {"from_attributes": True}


# ---- Novel ----

class NovelBase(BaseModel):
    title: str
    author: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    genre: Optional[str] = None
    status: Optional[str] = None
    word_count: Optional[int] = None
    chapter_count: Optional[int] = None
    score: Optional[float] = None
    rating_count: Optional[int] = None
    review_count: Optional[int] = None
    favorite_count: Optional[int] = None
    view_count: Optional[int] = None
    current_rank: Optional[int] = None
    rank_type: Optional[str] = None
    is_paid: Optional[bool] = None
    language: Optional[str] = None


class NovelOut(NovelBase):
    id: int
    platform_id: int
    platform_name: str = ""
    first_seen_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NovelDetail(NovelOut):
    snapshots: list["SnapshotOut"] = []


# ---- Snapshot ----

class SnapshotOut(BaseModel):
    id: int
    rank: Optional[int] = None
    score: Optional[float] = None
    rating_count: Optional[int] = None
    review_count: Optional[int] = None
    favorite_count: Optional[int] = None
    view_count: Optional[int] = None
    word_count: Optional[int] = None
    chapter_count: Optional[int] = None
    snapshot_time: datetime

    model_config = {"from_attributes": True}


# ---- ScrapeTask ----

class ScrapeTaskOut(BaseModel):
    id: int
    platform_id: int
    platform_name: str = ""
    task_type: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    items_scraped: int = 0
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Dashboard ----

class DashboardStats(BaseModel):
    total_novels: int
    total_platforms: int
    active_platforms: int
    today_scraped: int
    recent_tasks: list[ScrapeTaskOut]
    top_novels: list[NovelOut]


# ---- Common ----

class PageResult(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
