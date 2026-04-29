"""Wattpad 爬虫 - 基于公开 API"""
import logging
from .base import BaseScraper, ScrapedNovel

logger = logging.getLogger(__name__)

RANKING_TAGS = {
    "hot": "romance",
    "fantasy": "fantasy",
    "scifi": "sciencefiction",
    "werewolf": "werewolf",
    "teen": "teenfiction",
}


class WattpadScraper(BaseScraper):
    platform_code = "wattpad"
    base_url = "https://www.wattpad.com"

    async def scrape_ranking(self, rank_type: str = "hot", page: int = 1) -> list[ScrapedNovel]:
        tag = RANKING_TAGS.get(rank_type, "romance")
        api_url = f"https://www.wattpad.com/v5/hotlist?tags={tag}&limit=20&offset={(page - 1) * 20}&mature=0"
        try:
            resp = await self._get(api_url, headers={
                "Accept": "application/json",
            })
            data = resp.json()
        except Exception:
            logger.exception(f"Failed to fetch Wattpad ranking: {rank_type}")
            return []

        novels: list[ScrapedNovel] = []
        stories = data if isinstance(data, list) else data.get("stories", data.get("results", []))

        for idx, story in enumerate(stories, start=(page - 1) * 20 + 1):
            try:
                title = story.get("title", "")
                if not title:
                    continue

                author_info = story.get("user", {})
                author = author_info.get("name", "") or author_info.get("username", "")
                cover = story.get("cover", "")
                desc = story.get("description", "")
                story_url = f"{self.base_url}/story/{story.get('id', '')}"

                tags = story.get("tags", [])
                genre = ", ".join(tags[:5]) if tags else ""

                novels.append(ScrapedNovel(
                    title=title,
                    author=author,
                    cover_url=cover,
                    description=desc,
                    url=story_url,
                    genre=genre,
                    view_count=story.get("readCount", 0),
                    favorite_count=story.get("numParts", 0),
                    review_count=story.get("commentCount", 0),
                    rank=idx,
                    rank_type=rank_type,
                    language=story.get("language", {}).get("id", "en") if isinstance(story.get("language"), dict) else "en",
                    status="completed" if story.get("completed") else "ongoing",
                ))
            except Exception:
                logger.debug(f"Wattpad: failed to parse item {idx}", exc_info=True)
                continue

        logger.info(f"Wattpad [{rank_type}]: scraped {len(novels)} novels")
        return novels
