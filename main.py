import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram_social import InstagramSocialSpider

if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    users = [
        # 'apple',
        # 'burton',
        "milanovich_daria",
        "raikoandrei",
    ]

    crawler_process.crawl(
        InstagramSocialSpider,
        login=os.getenv("INST_LOGIN"),
        password=os.getenv("INST_PSWORD"),
        users=users,
        log_level=None,
    )
    crawler_process.start()
