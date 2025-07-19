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

        start_date, end_date = self._parse_available_dates(response)
        item['available_start_date'] = start_date
        item['available_end_date'] = end_date

        item['variants'] = self._parse_variants(response)

        item['description'] = self._parse_description(response)

        item['main_flowers'] = self.clean_getall_str(
            response.css('div.blossom-options div.blossom-name::text').getall()
        )
        item['main_colors'] = self.clean_getall_str(
            response.css('div.color-options div.color-name::text').getall()
        )

        item['delivery_description'] = response.css('div.pdp-delivery-description div.cms-element-text::text').get().strip()

        item['delivery_cost_euro'] = self._parse_delivery_cost(response)
        item['image_urls'] = response.css('img.gallery-slider-thumbnails-image::attr(src)').getall()

        yield item

    def _parse_available_dates(self, response):
        """
        Parses the available start and end dates from the product page.
        :param response: scrapy response object containing the product page HTML
        :return: tuple of (available_start_date, available_end_date)
        """
        available_dates_text = response.css('div.deliveryPeriod::text').get('').strip()
        available_start_date = None
        available_end_date = None

        if available_dates_text:
            match = re.search(r'(\d{2}\.\d{2}\.) - (\d{2}\.\d{2}\.)', available_dates_text)
            if match:
                available_start_date = match.group(1).strip()[:-1]
                available_end_date = match.group(2).strip()[:-1]

        return available_start_date, available_end_date

    def _parse_description(self, response):
        """
        Parses the product description from the response, including text in child elements.
        :param response: scrapy response object containing the product page HTML
        :return: str with the cleaned description text
        """
        description_parts = response.css('div#description-content-container *::text').getall()
        return ' '.join(part.strip() for part in description_parts if part.strip())

    def _parse_variants(self, response):
        """
        Parses the product variants from the response, extracting size and price information.
        :param response: scrapy response object containing the product page HTML
        :return: list of dictionaries with size and price information
        """
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
        return variants

    def _parse_delivery_cost(self, response):
        """
        Parses the delivery cost from the response.
        :param response: scrapy response object containing the product page HTML
        :return: str with the delivery cost in Euro
        """
        delivery_cost_text = response.css('div.pdp-delivery-service-text div.cms-element-text::text').get('').strip()
        if delivery_cost_text:
            return delivery_cost_text.split(' ')[-2].replace(',', '.')
        return None

    def clean_getall_str(self, data_list):
        """
        Takes a list of strings from getall(), strips whitespace, returns a list of unique strings.
        :param data_list:
        :return: cleaned string
        """
        cleaned_items = [item.strip() for item in data_list if item.strip() and item.strip() != ',']
        return ', '.join(set(cleaned_items))