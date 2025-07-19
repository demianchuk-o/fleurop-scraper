import scrapy

class FleuropProductItem(scrapy.Item):
    product_url = scrapy.Field()
    name = scrapy.Field()
    available_start_date = scrapy.Field()
    available_end_date = scrapy.Field()
    variants = scrapy.Field()
    description = scrapy.Field()
    main_flowers = scrapy.Field()
    main_colors = scrapy.Field()
    delivery_description = scrapy.Field()
    delivery_cost_euro = scrapy.Field()
    image_urls = scrapy.Field()