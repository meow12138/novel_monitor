"""Royal Road 爬虫"""
import logging
from bs4 import BeautifulSoup
from .base import BaseScraper, ScrapedNovel

logger = logging.getLogger(__name__)

RANKING_URLS = {
    "hot": "https://www.royalroad.com/fictions/best-rated",
    "trending": "https://www.royalroad.com/fictions/trending",
    "new": "https://www.royalroad.com/fictions/rising-stars",
    "popular": "https://www.royalroad.com/fictions/weekly-popular",
}


def _parse_number(text: str) -> int:
    text = text.strip().replace(",", "").replace(" ", "")
    multiplier = 1
    if text.upper().endswith("K"):
        multiplier = 1000
        text = text[:-1]
    elif text.upper().endswith("M"):
        multiplier = 1_000_000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except (ValueError, TypeError):
        return 0


class RoyalRoadScraper(BaseScraper):
    platform_code = "royalroad"
    base_url = "https://www.royalroad.com"

    async def scrape_ranking(self, rank_type: str = "hot", page: int = 1) -> list[ScrapedNovel]:
        url = RANKING_URLS.get(rank_type, RANKING_URLS["hot"])
        if page > 1:
            url += f"?page={page}"
        try:
            resp = await self._get(url)
        except Exception:
            logger.exception(f"Failed to fetch RoyalRoad ranking: {rank_type}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        novels: list[ScrapedNovel] = []
        items = soup.select(".fiction-list-item")

        for idx, item in enumerate(items, start=(page - 1) * 20 + 1):
            try:
                title_el = item.select_one("h2.fiction-title a")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                novel_url = f"{self.base_url}{href}" if not href.startswith("http") else href

                cover_el = item.select_one("img")
                cover = cover_el.get("src", "") if cover_el else ""

                stats = item.select(".stats .col-sm-6, .fiction-stats span")
                view_count = 0
                favorite_count = 0
                chapter_count = 0
                rating_count = 0

                for stat in stats:
                    text = stat.get_text(strip=True).lower()
                    i_el = stat.select_one("i")
                    cls = i_el.get("class", []) if i_el else []
                    cls_str = " ".join(cls)
                    val_el = stat.select_one("span, b")
                    val_text = val_el.get_text(strip=True) if val_el else text

                    if "eye" in cls_str or "view" in text or "follower" in text:
                        view_count = _parse_number(val_text)
                    elif "star" in cls_str or "favorite" in text or "bookmark" in text:
                        favorite_count = _parse_number(val_text)
                    elif "book" in cls_str or "chapter" in text or "page" in text:
                        chapter_count = _parse_number(val_text)
                    elif "list" in cls_str or "rating" in text:
                        rating_count = _parse_number(val_text)

                score_el = item.select_one("[data-score], .star, .rating")
                score = 0.0
                if score_el:
                    score_val = score_el.get("data-score") or score_el.get("title") or ""
                    try:
                        score = float(score_val.split("/")[0].strip()) if score_val else 0.0
                    except (ValueError, IndexError):
                        score = 0.0

                genre_els = item.select(".tags a, .tag")
                genre = ", ".join(g.get_text(strip=True) for g in genre_els)

                desc_el = item.select_one(".hidden-content, .margin-top-10 p, .description")
                desc = desc_el.get_text(strip=True) if desc_el else ""

                novels.append(ScrapedNovel(
                    title=title,
                    url=novel_url,
                    cover_url=cover,
                    description=desc,
                    genre=genre,
                    score=score,
                    view_count=view_count,
                    favorite_count=favorite_count,
                    chapter_count=chapter_count,
                    rating_count=rating_count,
                    rank=idx,
                    rank_type=rank_type,
                    language="en",
                ))
            except Exception:
                logger.debug(f"RoyalRoad: failed to parse item {idx}", exc_info=True)
                continue

        logger.info(f"RoyalRoad [{rank_type}]: scraped {len(novels)} novels")
        return novels
