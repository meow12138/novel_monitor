"""WebNovel (阅文海外) 爬虫"""
import logging
from bs4 import BeautifulSoup
from .base import BaseScraper, ScrapedNovel

logger = logging.getLogger(__name__)

RANKING_URLS = {
    "hot": "https://www.webnovel.com/ranking/novel/all_time/all",
    "trending": "https://www.webnovel.com/ranking/novel/week/all",
    "new": "https://www.webnovel.com/ranking/novel/new/all",
    "completed": "https://www.webnovel.com/ranking/novel/completed/all",
}


class WebNovelScraper(BaseScraper):
    platform_code = "webnovel"
    base_url = "https://www.webnovel.com"

    async def scrape_ranking(self, rank_type: str = "hot", page: int = 1) -> list[ScrapedNovel]:
        url = RANKING_URLS.get(rank_type, RANKING_URLS["hot"])
        try:
            resp = await self._get(url)
        except Exception:
            logger.exception(f"Failed to fetch WebNovel ranking: {rank_type}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        novels: list[ScrapedNovel] = []
        items = soup.select("li.j_rank_list_item, li[data-book-id], .rank-list .rank-item, .j_bookList li")

        if not items:
            items = soup.select("[class*='rank'] li, [class*='book'] li, .listItem")

        for idx, item in enumerate(items, start=1):
            try:
                title_el = item.select_one("h3 a, h4 a, .tit a, [class*='title'] a, a[class*='name']")
                if not title_el:
                    title_el = item.select_one("a")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                novel_url = href if href.startswith("http") else f"{self.base_url}{href}"

                author_el = item.select_one(".author, [class*='author'], .info span, p.author")
                author = author_el.get_text(strip=True) if author_el else ""

                cover_el = item.select_one("img")
                cover = cover_el.get("src", "") if cover_el else ""

                desc_el = item.select_one(".intro, [class*='desc'], p.fs12")
                desc = desc_el.get_text(strip=True) if desc_el else ""

                genre_el = item.select_one(".genre, [class*='tag'], .cls")
                genre = genre_el.get_text(strip=True) if genre_el else ""

                novels.append(ScrapedNovel(
                    title=title,
                    author=author,
                    cover_url=cover,
                    description=desc,
                    url=novel_url,
                    genre=genre,
                    rank=idx,
                    rank_type=rank_type,
                    language="en",
                ))
            except Exception:
                logger.debug(f"WebNovel: failed to parse item {idx}", exc_info=True)
                continue

        logger.info(f"WebNovel [{rank_type}]: scraped {len(novels)} novels")
        return novels
