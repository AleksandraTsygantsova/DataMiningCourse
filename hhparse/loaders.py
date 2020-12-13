from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import HhparseItem

#todo functions of preprocessing data

class HhparseItemLoader(ItemLoader):
    default_item_class = HhparseItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    #description_out = TakeFirst()
    #salary_out = TakeFirst()
    #key_skills_out = TakeFirst()
    company_url_out = TakeFirst()
    company_title_out = TakeFirst()
    company_site_out = TakeFirst()
    #company_type_of_business_out = TakeFirst()
    #company_description_out = TakeFirst()