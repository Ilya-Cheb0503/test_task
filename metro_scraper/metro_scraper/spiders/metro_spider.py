import scrapy

class ProductItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()
    old_price = scrapy.Field()
    brand = scrapy.Field()

class ProductSpider(scrapy.Spider):
    name = 'product_spider'
    start_urls = ['https://online.metro-cc.ru/virtual/novinky-v-METRO-37160?from=under_search']
    prefix = 'https://online.metro-cc.ru' 

    def start_requests(self):
        for page in range(1, 33):
            url = f'https://online.metro-cc.ru/virtual/novinky-v-METRO-37160?from=under_search&page={page}'
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        self.logger.info(f"Получен ответ от {response.url} с кодом {response.status}")
        content_elements = response.css('.catalog-2-level-product-card.product-card.subcategory-or-type__products-item.with-prices-drop')

        if not content_elements:
            self.logger.warning("Не найдено элементов с указанным классом.")
            return

        for element in content_elements:
            try:
                element_id = element.attrib.get('id')
                photo_link_element = element.css('[data-gtm="product-card-photo-link"]')
                price = element.css('.product-price__sum-rubles::text').get().strip()
                old_price = element.css('.product-unit-prices__old-wrapper .product-price__sum-rubles::text').get(default=None)

                if photo_link_element:
                    title = photo_link_element.attrib.get('title')
                    link = photo_link_element.attrib.get('href')
                    full_link = self.prefix + link

                    yield scrapy.Request(full_link, callback=self.parse_product, meta={
                        'item': {
                            'id': element_id,
                            'title': title,
                            'link': full_link,
                            'price': price,
                            'old_price': old_price
                        }
                    })

            except Exception as e:
                self.logger.warning(f"Ошибка при извлечении данных: {e}")

    def parse_product(self, response):
        attributions_list = response.css('.product-attributes__list.style--product-page-short-list')
        brend = attributions_list.css('.product-attributes__list-item-link.reset-link.active-blue-text::text').get(default='').strip().replace('\n', '').replace(' ', '')

        item = response.meta['item']
        item['brand'] = brend
        yield item
