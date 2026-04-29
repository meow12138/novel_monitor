"""爬虫适配器基类"""
import abc
import logging
from dataclasses import dataclass, field
from typing import Optional

import httpx

from ..core.config import SCRAPE_USER_AGENT, SCRAPE_TIMEOUT

logger = logging.getLogger(__name__)


@dataclass
class ScrapedNovel:
    """统一的抓取结果数据结构"""
    title: str
    author: str = ""
    cover_url: str = ""
    description: str = ""
    url: str = ""
    genre: str = ""
    status: str = ""
    word_count: int = 0
    chapter_count: int = 0
    score: float = 0.0
    rating_count: int = 0
    review_count: int = 0
    favorite_count: int = 0
    view_count: int = 0
    rank: int = 0
    rank_type: str = "hot"
    is_paid: bool = False
    language: str = "en"
    extra: dict = field(default_factory=dict)


class BaseScraper(abc.ABC):
    """所有平台爬虫的基类"""

    platform_code: str = ""
    base_url: str = ""

    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={"User-Agent": SCRAPE_USER_AGENT},
            timeout=SCRAPE_TIMEOUT,
            follow_redirects=True,
        )

    async def close(self):
        await self.client.aclose()

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        try:
            resp = await self.client.get(url, **kwargs)
            resp.raise_for_status()
            return resp
        except httpx.HTTPError as e:
            logger.error(f"[{self.platform_code}] HTTP error fetching {url}: {e}")
            raise

    async def _get_json(self, url: str, **kwargs) -> dict:
        resp = await self._get(url, **kwargs)
        return resp.json()

    @abc.abstractmethod
    async def scrape_ranking(self, rank_type: str = "hot", page: int = 1) -> list[ScrapedNovel]:
        """抓取排行榜，返回 ScrapedNovel 列表"""
        ...

    async def scrape_detail(self, novel_url: str) -> Optional[ScrapedNovel]:
        """抓取小说详情（可选实现）"""
        return None

    async def scrape_search(self, keyword: str) -> list[ScrapedNovel]:
        """搜索小说（可选实现）"""
        return []
