"""GoodNovel 爬虫"""
import logging
from bs4 import BeautifulSoup
from .base import BaseScraper, ScrapedNovel

logger = logging.getLogger(__name__)

RANKING_URLS = {
    "hot": "https://www.goodnovel.com/rankings/hot_novels",
    "trending": "https://www.goodnovel.com/rankings/trending_novels",
    "new": "https://www.goodnovel.com/rankings/new_novels",
    "completed": "https://www.goodnovel.com/rankings/completed_novels",
}


class GoodNovelScraper(BaseScraper):
    platform_code = "goodnovel"
    base_url = "https://www.goodnovel.com"

    async def scrape_ranking(self, rank_type: str = "hot", page: int = 1) -> list[ScrapedNovel]:
        url = RANKING_URLS.get(rank_type, RANKING_URLS["hot"])
        try:
            resp = await self._get(url)
        except Exception:
            logger.exception(f"Failed to fetch GoodNovel ranking: {rank_type}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        novels: list[ScrapedNovel] = []
        items = soup.select(".book-item, .ranking-item, [class*='book-card'], [class*='novel-item']")

        if not items:
            items = soup.select("li a[href*='/book/'], .book-list li, .rank-list li")

        for idx, item in enumerate(items, start=1):
            try:
                title_el = item.select_one("h3, h4, .book-name, [class*='title'], .name")
                if not title_el:
                    link = item if item.name == "a" else item.select_one("a")
                    title_el = link
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                link = item.select_one("a[href]") or item
                href = link.get("href", "") if link else ""
                novel_url = href if href.startswith("http") else f"{self.base_url}{href}"

                author_el = item.select_one(".author, [class*='author']")
                author = author_el.get_text(strip=True) if author_el else ""

                cover_el = item.select_one("img")
                cover = cover_el.get("src", "") or cover_el.get("data-src", "") if cover_el else ""

                desc_el = item.select_one(".intro, .desc, [class*='desc']")
                desc = desc_el.get_text(strip=True) if desc_el else ""

                genre_el = item.select_one(".genre, .tag, [class*='genre']")
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
                logger.debug(f"GoodNovel: failed to parse item {idx}", exc_info=True)
                continue

        logger.info(f"GoodNovel [{rank_type}]: scraped {len(novels)} novels")
        return novels
