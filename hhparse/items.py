# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HhparseItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    key_skills = scrapy.Field()
    company_url = scrapy.Field()
    company_title = scrapy.Field()
    company_site = scrapy.Field()
    company_type_of_business = scrapy.Field()
    company_description = scrapy.Field()
    pass


