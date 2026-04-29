from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from ..core.database import Base


class Platform(Base):
    """抓取平台"""
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # webnovel / goodnovel / royalroad ...
    website = Column(String(500))
    region = Column(String(50))       # 地区: global / jp / kr / us / sea
    category = Column(String(50))     # 分类: cn_overseas / us_native / jp / kr / ebook / social
    enabled = Column(Boolean, default=True)
    scraper_class = Column(String(100))  # 对应的爬虫类名
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    novels = relationship("Novel", back_populates="platform", lazy="noload")
    scrape_tasks = relationship("ScrapeTask", back_populates="platform", lazy="noload")


class Novel(Base):
    """小说"""
    __tablename__ = "novels"
    __table_args__ = (
        Index("ix_novels_platform_rank", "platform_id", "current_rank"),
        Index("ix_novels_score", "score"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    title = Column(String(500), nullable=False)
    author = Column(String(200))
    cover_url = Column(String(1000))
    description = Column(Text)
    url = Column(String(1000))          # 原始链接
    genre = Column(String(200))         # 类型/标签
    status = Column(String(50))         # ongoing / completed
    word_count = Column(Integer)
    chapter_count = Column(Integer)
    score = Column(Float)               # 评分
    rating_count = Column(Integer)      # 评分人数
    review_count = Column(Integer)      # 评论数
    favorite_count = Column(Integer)    # 收藏/订阅数
    view_count = Column(Integer)        # 阅读量/点击数
    current_rank = Column(Integer)      # 当前排名
    rank_type = Column(String(50))      # 排名类型: hot / trending / new / completed
    is_paid = Column(Boolean)           # 是否付费
    language = Column(String(20))       # 语言: en / zh / ja / ko / es / pt ...
    last_chapter_time = Column(DateTime)  # 最新章节更新时间
    extra_data = Column(Text)           # JSON 扩展字段
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    platform = relationship("Platform", back_populates="novels", lazy="joined")
    snapshots = relationship("NovelSnapshot", back_populates="novel", lazy="noload")


class NovelSnapshot(Base):
    """小说数据快照 - 记录历史变化趋势"""
    __tablename__ = "novel_snapshots"
    __table_args__ = (
        Index("ix_snapshots_novel_time", "novel_id", "snapshot_time"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    rank = Column(Integer)
    score = Column(Float)
    rating_count = Column(Integer)
    review_count = Column(Integer)
    favorite_count = Column(Integer)
    view_count = Column(Integer)
    word_count = Column(Integer)
    chapter_count = Column(Integer)
    snapshot_time = Column(DateTime, default=datetime.utcnow)

    novel = relationship("Novel", back_populates="snapshots", lazy="noload")


class ScrapeTask(Base):
    """抓取任务"""
    __tablename__ = "scrape_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    task_type = Column(String(50), default="ranking")  # ranking / detail / search
    status = Column(String(20), default="pending")      # pending / running / success / failed
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    items_scraped = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    platform = relationship("Platform", back_populates="scrape_tasks", lazy="joined")
