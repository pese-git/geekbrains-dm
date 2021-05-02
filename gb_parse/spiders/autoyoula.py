import scrapy


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    def _get_follow(self, response, selector_str, callback):
        for itm in response.css(selector_str):
            url = itm.attrib["href"]
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv .ColumnItemList_container__5gTrc .ColumnItemList_item__32nYI a.blackLink",
            self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, ".Paginator_block__2XAPy .Paginator_button__u1e7D", self.brand_parse
        )

        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu.blackLink",
            self.car_parse,
        )

    def car_parse(self, response):
        title = response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first()
        images = response.css(".PhotoGallery_photoWrapper__3m7yM .PhotoGallery_photoImage__2mHGn")
        description = response.css(".AdvertCard_descriptionInner__KnuRi::text").extract_first()
        protected = response.css(
            ".AdvertEquipment_equipmentSection__3YpK5 div.AdvertEquipment_equipmentItem__Jk5c4::text"
        )
        comfort = response.css(
            ".AdvertEquipment_equipmentSection__3YpK5 div.AdvertEquipment_equipmentItem__Jk5c4::text"
        )
        ext = response.css(
            ".AdvertEquipment_equipmentSection__3YpK5 div.AdvertEquipment_equipmentItem__Jk5c4::text"
        )
        media = response.css(
            ".AdvertEquipment_equipmentSection__3YpK5 div.AdvertEquipment_equipmentItem__Jk5c4::text"
        )

        # characters_keys = response.css(".AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX div.AdvertSpecs_label__2JHnS::text").extract()
        # characters_values = response.css(".AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX div.AdvertSpecs_data__xK2Qx::text").extract()
        # characteristics = {}
        # for i in range(len(characters_keys)):
        #    characteristics[characters_keys[i]] = characters_values[i]

        data = {
            "url": response.url,
            "title": title,
            "images_urls": list(map(lambda img: img.attrib["src"], images)),
            "description": description,
            "protected": list(map(lambda row: row.extract(), protected)),
            "comfort": list(map(lambda row: row.extract(), comfort)),
            "ext": list(map(lambda row: row.extract(), ext)),
            "media": list(map(lambda row: row.extract(), media))
            # "characteristics": characteristics
        }
        print(data)
