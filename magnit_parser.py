import os
import time
import datetime as dt
import requests
import bs4
import pymongo
import dotenv
import re
from urllib.parse import urljoin

dotenv.load_dotenv('.env')


class MagnitParse:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'
    }

    monthes = {
        'января': '01',
        'февраля': '02',
        'марта': '03',
        'апреля': '04',
        'мая': '05',
        'июня': '06',
        'июля': '07',
        'августа': '08',
        'сентября': '09',
        'октября': '10',
        'ноября': '11',
        'декабря': '12',
    }

    def __init__(self, start_url):
        self.start_url = start_url
        client = pymongo.MongoClient(os.getenv('DATA_BASE'))
        self.db = client['gb_parse_11']

        self.product_template = {
            'url': lambda soup: urljoin(self.start_url, soup.get('href')),
            'promo_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__header'}).text,
            'product_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__title'}).text,
            "old_price": lambda soup: soup.find('div', attrs={'class': 'label__price label__price_old'}).text,
            "new_price": lambda soup: soup.find('div', attrs={'class': 'label__price label__price_new'}).text,
            'image_url': lambda soup: urljoin(self.start_url, soup.find('img').get('data-src')),
            "date_from": lambda soup: soup.find('div', attrs={'class': 'card-sale__date'}).text,
            "date_to": lambda soup: soup.find('div', attrs={'class': 'card-sale__date'}).text,
        }

    @staticmethod
    def _get(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    raise Exception
                return response
            except Exception:
                time.sleep(0.5)

    def soup(self, url) -> bs4.BeautifulSoup:
        response = self._get(url, headers=self.headers)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self):
        soup = self.soup(self.start_url)
        for product in self.parse(soup):
            self.save(product)

    def parse(self, soup):
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.find_all('a', recursive=False):
            pr_data = self.get_product(product)
            yield pr_data

    def get_product(self, product_soup) -> dict:

        result = {}
        for key, value in self.product_template.items():
            try:
                result[key] = value(product_soup)
            except Exception as e:
                continue

        result = self.transform_data(result)

        return result

    def transform_data(self, product_dict):

        # Transform Old price and New price from string to float
        product_dict = self.transform_data_price(product_dict, ['old_price', 'new_price'])
        # Transform sale_data to data_from and data_to
        product_dict = self.transform_data_sales_data(product_dict)

        return product_dict

    @staticmethod
    def transform_data_price(product, categories) -> dict:

        for category in categories:
            if category not in product:
                pass
            else:
                new_value = product[category].replace('\n', '.')
                try:
                    new_value = float(new_value[1:-1])
                except Exception:
                    continue
                product[category] = new_value

        return product

    def transform_data_sales_data(self, product) -> dict:

        if 'date_from' not in product:
            pass
        else:
            datetime = product['date_from']

            for key, value in self.monthes.items():
                datetime = re.sub(key, value, datetime)

            year = dt.date.today().year
            dates = re.findall(r'\d\d', datetime)

            try:
                product['date_from'] = dt.date(year, int(dates[1]), int(dates[0]))
            except Exception:
                pass

            try:
                product['date_to'] = dt.date(year, int(dates[3]), int(dates[2]))
            except Exception:
                pass

        return product


    def save(self, product):
        collection = self.db['magnit_11']
        collection.insert_one(product)

if __name__ == '__main__':
    parser = MagnitParse('https://magnit.ru/promo/?geo=moskva')
    parser.run()