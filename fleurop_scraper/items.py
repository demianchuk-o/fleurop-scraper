import scrapy

class FleuropProductItem(scrapy.Item):
    product_url = scrapy.Field()
    name = scrapy.Field()
    available_dates = scrapy.Field()
    variants = scrapy.Field()
    description = scrapy.Field()
    main_flowers = scrapy.Field()
    main_colors = scrapy.Field()
    delivery_info = scrapy.Field()
    image_urls = scrapy.Field()