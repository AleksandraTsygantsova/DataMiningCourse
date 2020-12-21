# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Insta(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()

class InstaUser(Insta):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    id = scrapy.Field()
    username = scrapy.Field()

class InstaFollow(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    from_user_id = scrapy.Field()
    to_user_id = scrapy.Field()
