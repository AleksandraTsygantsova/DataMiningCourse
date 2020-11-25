# Задача организовать сбор данных,
# необходимо иметь метод сохранения данных в .json файлы
#
# Результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл
# скачанные данные сохраняются в Json файлы, для каждой категории товаров должен быть
# создан отдельный файл и содержать товары исключительно соответсвующие данной категории.


import os
from pathlib import Path
import json
import time

import requests

class Parser:

    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'
    }
    _params = {
        'records_per_page': 50
    }

    def __init__(self, start_url, category_url):
        self.start_url = start_url
        self.category_url = category_url

    @staticmethod
    def _get(*args, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    # todo Создать класс исключение
                    raise Exception
                return response
            except Exception:
                time.sleep(0.25)

    def parse_categories(self, url):
        params = self._params
        response = self._get(url, params=params, headers=self._headers)
        categories: dict = response.json()

        return categories

    def parse(self, url, category):
        params = self._params
        category_num = category.get('parent_group_code')
        params.update({'categories': category_num})

        while url:
            response: requests.Response = self._get(url, params=params, headers=self._headers)
            if params:
                params = {}
            data: dict = response.json()
            url = data.get('next')
            yield data.get('results')

    def run(self):
        for category in self.parse_categories(self.category_url):
            for products in self.parse(self.start_url, category):

                data = {'parent_group_code': category.get('parent_group_code'),
                        'parent_group_name': category.get('parent_group_name'),
                        'products': products}

                self._save_to_file(data, category)
                time.sleep(0.1)

    @staticmethod
    def _save_to_file(product, category):
        path = Path(os.path.dirname(__file__)).joinpath('products').joinpath(f'{category["parent_group_name"]}.json')
        with open(path, 'w', encoding='UTF-8') as file:
            json.dump(product, file, ensure_ascii=False)

if __name__ == '__main__':
    parser = Parser('https://5ka.ru/api/v2/special_offers/', 'https://5ka.ru/api/v2/categories/')
    parser.run()