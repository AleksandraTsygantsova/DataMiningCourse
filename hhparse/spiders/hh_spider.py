import scrapy
from ..loaders import HhparseItemLoader
from scrapy.selector import Selector


class HhSpiderSpider(scrapy.Spider):
    db_type = 'MONGO'
    name = 'hh_spider'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    xpath = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
        'jobs': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    }

    jobs_shape = {
        'title': '//h1[@data-qa="vacancy-title"]/text()',
        'salary': '//p[@class="vacancy-salary"]//text()',
        'description': '//div[@data-qa="vacancy-description"]//text()',
        'key_skills': '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()',
        'company_url': '//a[@data-qa="vacancy-company-name"]/@href'
    }

    company_shape = {
        'company_title': '//h1/span[contains(@class, "company-header-title-name")]/text()',
        'company_site': '//a[contains(@data-qa, "company-site")]/@href',
        'company_type_of_business': '//dib[@class="employer-sidebar-block__header"]//p/text()',
        'company_description': '//div[contains(@data-qa, "company-description")]//text()'
    }

    def parse(self, response, **kwargs):
        for page in response.xpath(self.xpath['pagination']):
            yield response.follow(page, callback=self.parse_jobs)


    def parse_jobs(self, response, **kwargs):
        for job in response.xpath(self.xpath['jobs']):
            yield response.follow(job, callback=self.parse_data)

    def parse_data(self, response, **kwargs):
        selector = Selector(response=response)
        loader = HhparseItemLoader(selector=selector)
        loader.add_value('url', response.url)

        for key, value in self.jobs_shape.items():
            loader.add_xpath(key, value)

        yield loader.load_item()
        yield response.follow(response.xpath(self.jobs_shape['company_url']).get(), callback=self.parse_company)

    def parse_company(self, response, **kwargs):
        selector = Selector(response=response)
        loader = HhparseItemLoader(selector=selector)

        for key, value in self.company_shape.items():
            loader.add_xpath(key, value)

        yield loader.load_item()







