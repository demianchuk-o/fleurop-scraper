import scrapy
from fleurop_scraper.items import FleuropProductItem

class BouquetsSpider(scrapy.Spider):
    name = 'bouquets'
    start_urls = [
        'https://www.fleurop.de/alle-blumenstraeusse'
    ]

    def parse(self, response):
        product_urls = response.css('div.product-info a.product-name::attr(href)').getall()
        for product_url in product_urls:
            yield response.follow(product_url, self.parse_product)


    def parse_product(self, response):
        item = FleuropProductItem()
        item['product_url'] = response.url
        item['name'] = response.css('div.product-heading h1::text').get('').strip()
        item['available_dates'] = response.css('div.deliveryPeriod::text').get('').strip()

        variants = []
        for variant_selector in response.css('label.product-detail-configurator-option-label is-display-text'):
            size = variant_selector.css('span.option-label::text').get('').strip()
            price_text = variant_selector.css('div.option-price::text').get('').strip(),


            price = price_text.split(' ')[0].replace(',', '.') if price_text else None
            if size and price:
                variants.append({
                    'size': size,
                    'price': price
                })
        item['variants'] = variants

        description_parts = response.css('div#description-content-container *::text').getall()
        item['description'] = ' '.join(part.strip() for part in description_parts if part.strip())

        item['main_flowers'] = response.css('div.blossom-options div.blossom-name::text').getall()
        item['main_colors'] = response.css('div.color-options div.color-name::text').getall()

        item['delivery_description'] = response.css('div.pdp-delivery-description div.cms-element-text::text').get().strip()

        cost_text = response.css('div.pdp-delivery-service-text div.cms-element-text::text').get('').strip()
        item['delivery_cost_euro'] = cost_text.split(' ')[-2].replace(',', '.') if cost_text else None
        item['image_urls'] = response.css('img.gallery-slider-thumbnails-image.loaded.tns-complete::attr(src)').getall()

        yield item