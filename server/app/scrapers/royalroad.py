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
    import re
    nums = re.findall(r"[\d,]+\.?\d*", text.replace(" ", ""))
    if not nums:
        return 0
    num_str = nums[0].replace(",", "")
    multiplier = 1
    text_upper = text.upper()
    if "K" in text_upper:
        multiplier = 1000
    elif "M" in text_upper:
        multiplier = 1_000_000
    try:
        return int(float(num_str) * multiplier)
    except (ValueError, TypeError):
        return 0


class RoyalRoadScraper(BaseScraper):
    platform_code = "royalroad"
    base_url = "https://www.royalroad.com"

    async def _fetch_author(self, novel_url: str) -> str:
        try:
            resp = await self._get(novel_url)
            soup = BeautifulSoup(resp.text, "lxml")
            author_el = soup.select_one("h4.font-white a[href*='/profile/']")
            if author_el:
                return author_el.get_text(strip=True)
        except Exception:
            pass
        return ""

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

                stats = item.select(".stats .col-sm-6")
                view_count = 0
                favorite_count = 0
                chapter_count = 0
                page_count = 0

                for stat in stats:
                    text = stat.get_text(strip=True).lower()
                    i_el = stat.select_one("i")
                    cls = " ".join(i_el.get("class", [])) if i_el else ""

                    if "fa-users" in cls or "follower" in text:
                        favorite_count = _parse_number(text)
                    elif "fa-eye" in cls or "view" in text:
                        view_count = _parse_number(text)
                    elif "fa-book" in cls or "page" in text:
                        page_count = _parse_number(text)
                    elif "fa-list" in cls or "chapter" in text:
                        chapter_count = _parse_number(text)

                score = 0.0
                score_el = item.select_one("[title]")
                for el in item.select("span[title]"):
                    try:
                        val = float(el.get("title", "0"))
                        if 0 < val <= 5:
                            score = val
                            break
                    except (ValueError, TypeError):
                        continue

                genre_els = item.select("a.fiction-tag")
                genre = ", ".join(g.get_text(strip=True) for g in genre_els)

                desc_el = item.select_one("[id^='description-']")
                desc = desc_el.get_text(strip=True) if desc_el else ""

                status = ""
                for label in item.select("span.label"):
                    lt = label.get_text(strip=True).lower()
                    if lt in ("completed", "ongoing", "hiatus", "dropped"):
                        status = lt
                        break

                novels.append(ScrapedNovel(
                    title=title,
                    url=novel_url,
                    cover_url=cover,
                    description=desc,
                    genre=genre,
                    status=status,
                    score=score,
                    view_count=view_count,
                    favorite_count=favorite_count,
                    chapter_count=chapter_count,
                    word_count=page_count,
                    rank=idx,
                    rank_type=rank_type,
                    language="en",
                ))
            except Exception:
                logger.debug(f"RoyalRoad: failed to parse item {idx}", exc_info=True)
                continue

        for novel in novels[:20]:
            if not novel.author and novel.url:
                novel.author = await self._fetch_author(novel.url)

        logger.info(f"RoyalRoad [{rank_type}]: scraped {len(novels)} novels")
        return novels
