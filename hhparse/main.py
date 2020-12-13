from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hhparse.spiders.hh_spider import HhSpiderSpider


if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('hhparse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(HhSpiderSpider)
    crawl_proc.start()