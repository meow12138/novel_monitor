"""爬虫注册表 - 集中管理所有平台爬虫"""
from .base import BaseScraper
from .webnovel import WebNovelScraper
from .royalroad import RoyalRoadScraper
from .goodnovel import GoodNovelScraper
from .dreame import DreameScraper
from .wattpad import WattpadScraper

SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "webnovel": WebNovelScraper,
    "royalroad": RoyalRoadScraper,
    "goodnovel": GoodNovelScraper,
    "dreame": DreameScraper,
    "wattpad": WattpadScraper,
}

DEFAULT_PLATFORMS = [
    {
        "name": "WebNovel",
        "code": "webnovel",
        "website": "https://www.webnovel.com",
        "region": "global",
        "category": "cn_overseas",
        "scraper_class": "WebNovelScraper",
        "description": "阅文集团旗下海外平台，全球最大中国网文英译站",
    },
    {
        "name": "GoodNovel",
        "code": "goodnovel",
        "website": "https://www.goodnovel.com",
        "region": "global",
        "category": "cn_overseas",
        "scraper_class": "GoodNovelScraper",
        "description": "新阅时代旗下，印尼/泰国市场表现突出",
    },
    {
        "name": "Dreame",
        "code": "dreame",
        "website": "https://www.dreame.com",
        "region": "global",
        "category": "cn_overseas",
        "scraper_class": "DreameScraper",
        "description": "无限进制旗下，土耳其收入榜第一",
    },
    {
        "name": "Royal Road",
        "code": "royalroad",
        "website": "https://www.royalroad.com",
        "region": "us",
        "category": "us_native",
        "scraper_class": "RoyalRoadScraper",
        "description": "欧美最大奇幻/LitRPG网文社区",
    },
    {
        "name": "Wattpad",
        "code": "wattpad",
        "website": "https://www.wattpad.com",
        "region": "global",
        "category": "us_native",
        "scraper_class": "WattpadScraper",
        "description": "全球最大UGC小说社区，用户以年轻人为主",
    },
    {
        "name": "Ficool",
        "code": "ficool",
        "website": "https://www.ficool.com",
        "region": "global",
        "category": "cn_overseas",
        "scraper_class": "",
        "description": "免费网文平台，覆盖言情、奇幻、BL",
    },
    {
        "name": "Bravonovel",
        "code": "bravonovel",
        "website": "https://www.bravonovel.com",
        "region": "global",
        "category": "cn_overseas",
        "scraper_class": "",
        "description": "掌阅系海外平台，主打霸总言情、奇幻",
    },
    {
        "name": "BabelNovel",
        "code": "babelnovel",
        "website": "https://babelnovel.com",
        "region": "global",
        "category": "cn_overseas",
        "scraper_class": "",
        "description": "中国网文英译社区",
    },
    {
        "name": "Tapas",
        "code": "tapas",
        "website": "https://tapas.io",
        "region": "us",
        "category": "us_native",
        "scraper_class": "",
        "description": "移动端优先漫画+小说平台，言情/YA类强势",
    },
    {
        "name": "Kakao Page",
        "code": "kakaopage",
        "website": "https://page.kakao.com",
        "region": "kr",
        "category": "kr",
        "scraper_class": "",
        "description": "韩国最大网文/漫画平台",
    },
    {
        "name": "小説家になろう",
        "code": "syosetu",
        "website": "https://syosetu.com",
        "region": "jp",
        "category": "jp",
        "scraper_class": "",
        "description": "日本最大网文平台，110万+作品，异世界类",
    },
    {
        "name": "Amazon Kindle",
        "code": "kindle",
        "website": "https://www.amazon.com/kindle-dbs/hz/bookshelf",
        "region": "global",
        "category": "ebook",
        "scraper_class": "",
        "description": "全球最大电子书市场排行榜",
    },
]


def get_scraper(platform_code: str) -> BaseScraper | None:
    cls = SCRAPER_REGISTRY.get(platform_code)
    if cls:
        return cls()
    return None
