from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.head_hunter import HeadHunterSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")

    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HeadHunterSpider)
    crawler_process.start()
