import bs4
import requests
from urllib.parse import urljoin
from database import DataBase
import time


class GbBlogParse:

    _headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:82.0) Gecko/20100101 Firefox/82.0",
    }

    def __init__(self, start_url: str, db: DataBase):
        self.start_url = start_url
        self.page_done = set()
        self.db = db
        self._api_url = 'https://geekbrains.ru/api/v2/comments'

    def __get(self, url) -> bs4.BeautifulSoup:
        response = requests.get(url)
        self.page_done.add(url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        return soup

    @staticmethod
    def _get_api(*args, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    # todo Создать класс исключение
                    raise Exception
                return response
            except Exception:
                time.sleep(0.25)

    def run(self, url=None):
        if not url:
            url = self.start_url

        if url not in self.page_done:
            soup = self.__get(url)
            posts, pagination = self.parse(soup)

            for post_url in posts:
                page_data = self.page_parse(self.__get(post_url), post_url)
                self.save(page_data)
            for p_url in pagination:
                self.run(p_url)

    def parse(self, soup):
        ul_pag = soup.find('ul', attrs={'class': 'gb__pagination'})
        paginations = set(
            urljoin(self.start_url, url.get('href')) for url in ul_pag.find_all('a') if url.attrs.get('href'))
        posts = set(
            urljoin(self.start_url, url.get('href')) for url in soup.find_all('a', attrs={'class': 'post-item__title'}))
        return posts, paginations

    def page_parse(self, soup, url) -> dict:
        data = {
            'post_data': {
                'url': url,
                'title': soup.find('h1').text,
                'image': soup.find('div', attrs={'class': 'blogpost-content'}).find('img').get('src') if soup.find(
                    'div', attrs={'class': 'blogpost-content'}).find('img') else None,
                'date': soup.find('div', attrs={'class': 'blogpost-date-views'}).find('time').get('datetime'),
            },
            'writer': {'name': soup.find('div', attrs={'itemprop': 'author'}).text,
                       'url': urljoin(self.start_url,
                                      soup.find('div', attrs={'itemprop': 'author'}).parent.get('href'))},
            'comments': [],
            'tags': [],


        }
        for tag in soup.find_all('a', attrs={'class': "small"}):
            tag_data = {
                'url': urljoin(self.start_url, tag.get('href')),
                'name': tag.text
            }
            data['tags'].append(tag_data)


        for comment in self.get_comments(soup):
            comment_path = comment['comment']
            author_path = comment_path['user']
            comment_data = {
                'comment': comment_path['body'],
                'author_id': author_path['id'],
                'url': comment_path['id']
            }
            data['comments'].append(comment_data)

        return data

    def get_comments(self, soup) -> dict:
        post_id = soup.find('div', attrs={'class': 'referrals-social-buttons-small-wrapper'}).get('data-minifiable-id')
        params = {'commentable_type': 'Post',
                  'commentable_id':	post_id,
                  'order': 'desc'}

        response: requests.Response = self._get_api(self._api_url, params=params, headers=self._headers)
        data = response.json()

        return data


    def save(self, page_data: dict):
        self.db.create_post(page_data)


if __name__ == '__main__':
    db = DataBase('sqlite:///gb_blog.db')
    parser = GbBlogParse('https://geekbrains.ru/posts', db)

    parser.run()