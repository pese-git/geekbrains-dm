# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from .settings import BOT_NAME
from pymongo import MongoClient


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class GbMongoPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client[BOT_NAME]

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item


class GbImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item.get("photos", []):
            yield Request(url)

    def item_completed(self, results, item, info):
        if item.get("photos"):
            item["photos"] = [itm[1] for itm in results]
        return item


class GbParseInstagramMongoPipline:
    def __init__(self):
        client = MongoClient()
        self.db = client[BOT_NAME]
        self.collection = self.db["tags"]

    def process_item(self, item, spider):
        if item.get("data").get("name"):
            if len(list(self.collection.find({"_id": item["_id"]}))) == 0:
                self.db["tags"].insert_one(item)
            return item
        self.db["posts"].insert_one(item)
        return item


class GbParseInstagramPostImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        img_url = item.get("data", {}).get("photo")
        if img_url:
            yield Request(img_url)

    def item_completed(self, results, item, info):
        if results:
            item["photos"] = [itm[1] for itm in results]
        return item
