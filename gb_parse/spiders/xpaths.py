AUTO_YOULA_PAGE_XPATH = {
    "brands": "//div[@data-target='transport-main-filters']/"
    "div[contains(@class, 'TransportMainFilters_brandsList')]//"
    "a[@data-target='brand']/@href",
}

AUTO_YOULA_BRAND_XPATH = {
    "pagination": '//a[@data-target-id="button-link-serp-paginator"]/@href',
    "car": '//article[@data-target="serp-snippet"]//a[@data-target="serp-snippet-title"]/@href',
}

AUTO_YOULA_CAR_XPATH = {
    "title": {"xpath": "//div[@data-target='advert-title']/text()"},
    "photos": {"xpath": "//figure/picture/img/@src"},
    "characteristics": {
        "xpath": "//h3[contains(text(), 'Характеристики')]/..//"
        "div[contains(@class, 'AdvertSpecs_row')]"
    },
    "price": {"xpath": '//div[@data-target="advert"]//div[@data-target="advert-price"]/text()'},
    "descriptions": {
        "xpath": '//div[@data-target="advert"]//'
        'div[@data-target="advert-info-descriptionFull"]/text()'
    },
    "author": {
        "xpath": '//script[contains(text(), "window.transitState = decodeURIComponent")]',
        "re": r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar",
    },
}

HH_PAGE_XPATH = {
    "pagination": '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
    "vacancy": '//div[contains(@data-qa, "vacancy-serp__vacancy")]//'
    'a[@data-qa="vacancy-serp__vacancy-title"]/@href',
}

HH_VACANCY_XPATH = {
    "title": '//h1[@data-qa="vacancy-title"]/text()',
    "salary": '//p[@class="vacancy-salary"]/span/text()',
    "description": '//div[@data-qa="vacancy-description"]//text()',
    "skills": '//div[@class="bloko-tag-list"]//'
    'div[contains(@data-qa, "skills-element")]/'
    'span[@data-qa="bloko-tag__text"]/text()',
    "author": '//a[@data-qa="vacancy-company-name"]/@href',
}


AVITO_PAGE_XPATH = {
    "pagination": '//div[@data-marker="pagination-button"]//span[contains(@data-marker,"page")]/text()',
    "apartment": '//div[@data-marker="item"]//a/@href',
}

AVITO_XPATH = {
    "title": '//div[@class="item-view-content"]//'
    'div[@class="item-view-content-left"]/span[@class="title-info-title-text"]/text()',
    "amount": '//div[@class="item-view-content"]//'
    'div[@class="item-price-wrapper"]//span[@itemprop="price"]/text()',
    "currency_symbol": '//div[@class="item-view-content"]//'
    'div[@class="item-price-wrapper"]//span[@class="font_arial-rub"]/text()',
    "description": '//div[@class="item-view-content"]//'
    'div[@class="item-description"]/div[@itemprop="description"]/p/text()',
    "address": '//div[@class="item-view-content"]//'
    'div[@class="item-address"]//div[@itemprop="address"]'
    '//span[@class="item-address__string"]//text()',
    "author": '//div[@class="item-view-content"]//'
    'div[@class="seller-info-value"]/div[@class="seller-info-name js-seller-info-name"]/a/@href',
}
