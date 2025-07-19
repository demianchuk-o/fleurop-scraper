import scrapy
import re
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
        available_dates_text = response.css('div.deliveryPeriod::text').get('').strip()
        item['available_start_date'] = None
        item['available_end_date'] = None

        if available_dates_text:
            match = re.search(r'(\d{2}\.\d{2}\.) - (\d{2}\.\d{2}\.)', available_dates_text)
            if match:
                item['available_start_date'] = match.group(1).strip()[:-1]
                item['available_end_date'] = match.group(2).strip()[:-1]

        variants = []
        for variant_selector in response.css('label.product-detail-configurator-option-label.is-display-text'):
            size = variant_selector.css('div.option-label::text').get('').strip()
            price_text = variant_selector.css('div.option-price::text').get('').strip()

            price = None
            if price_text:
                if any(char.isdigit() for char in price_text):
                    price = re.sub(r'[^\d\,]', '', price_text).strip().replace(',', '.')
                else:
                    price = price_text

            if size:
                variants.append({
                    'size': size,
                    'price': price
                })
        item['variants'] = variants

        description_parts = response.css('div#description-content-container *::text').getall()
        item['description'] = ' '.join(part.strip() for part in description_parts if part.strip())

        item['main_flowers'] = self.clean_getall_str(
            response.css('div.blossom-options div.blossom-name::text').getall()
        )
        item['main_colors'] = self.clean_getall_str(
            response.css('div.color-options div.color-name::text').getall()
        )

        item['delivery_description'] = response.css('div.pdp-delivery-description div.cms-element-text::text').get().strip()

        cost_text = response.css('div.pdp-delivery-service-text div.cms-element-text::text').get('').strip()
        item['delivery_cost_euro'] = cost_text.split(' ')[-2].replace(',', '.') if cost_text else None
        item['image_urls'] = response.css('img.gallery-slider-thumbnails-image::attr(src)').getall()

        yield item

    def clean_getall_str(self, data_list):
        """
        Takes a list of strings from getall(), strips whitespace, returns a list of unique strings.
        :param data_list:
        :return: cleaned string
        """
        cleaned_items = [item.strip() for item in data_list if item.strip() and item.strip() != ',']
        return ', '.join(set(cleaned_items))