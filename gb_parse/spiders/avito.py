import scrapy

from gb_parse.loaders import AvitoApartment
from gb_parse.spiders.xpaths import AVITO_PAGE_XPATH, AVITO_XPATH


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["avito.ru"]
    start_urls = ["https://www.avito.ru/krasnodar/kvartiry/prodam-ASgBAgICAUSSA8YQ"]

    def __get_follow_xpath(self, response, xpath, callback, key):
        for selector in response.xpath(xpath):
            if key == "pagination":
                url = f"/krasnodar/kvartiry/prodam-ASgBAgICAUSSA8YQ?p={selector.extract()}"
            else:
                url = selector.extract()
            yield response.follow(url, callback=callback)

    def _get_follow_xpath(self, response, select_str, callback):
        pages = response.xpath(select_str).extract()
        for a in range(1, int(pages[len(pages) - 1])):
            link = self.start_urls[0] + f"?p={a}"
            yield response.follow(link, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow_xpath(
            response, AVITO_PAGE_XPATH["pagination"], self._parse_page
        )

    #    callbacks = {"pagination": self.parse, "apartment": self._parse_apartment}

    #    for key, xpath in AVITO_PAGE_XPATH.items():
    #        yield from self._get_follow_xpath(response, xpath, callbacks[key], key)

    def _parse_page(self, response, *args, **kwargs):
        pages = response.xpath(AVITO_PAGE_XPATH["apartment"]).extract()
        for link_part in pages:
            link = "https://www.avito.ru" + link_part
            yield response.follow(link, callback=self._parse_apartment)

    def _parse_apartment(self, response):
        loader = AvitoApartment(response=response)
        loader.add_value("url", response.url)
        for key, xpath in AVITO_XPATH.items():
            try:
                loader.add_xpath(key, xpath)
            except TypeError:
                pass

        yield loader.load_item()
