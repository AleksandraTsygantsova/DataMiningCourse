import datetime as dt
import json
import scrapy
from ..items import InstaUser, InstaFollow


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    api_url = '/graphql/query/'
    query_hash = {
        'following': "d04b0a864b4b54837c0d870b0e77e076",
        'followers': "",
    }

    def __init__(self, login, enc_password, user, *args, **kwargs):
        self.login = login
        self.enc_passwd = enc_password
        self.user = user
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_passwd,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                yield response.follow(f'/{self.user}', callback=self.user_parse)

    def user_parse(self, response):
        user = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']

        yield InstaUser(
            id=user['id'],
            username=user['username'],
            date_parse=dt.datetime.utcnow()
        )

        yield from self.get_api_request(response, user)

    def get_api_request(self, response, user, variables=None):
        if variables is None:
            variables = {
                "id": user['id'],
                "include_reel": 'true',
                "fetch_mutual": 'false',
                "first": 100,
            }
        url = f'{self.api_url}?query_hash={self.query_hash["following"]}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_followings, cb_kwargs={'user': user})


    def get_followings(self, response, user):
        follow_data = response.json()
        yield from self.get_followings_item(follow_data, user)
        if follow_data['data']['user']['edge_follow']['page_info']['has_next_page']:
            variables = {
                'id': user['id'],
                'first': 100,
                'after': follow_data['data']['user']['edge_follow']['page_info']['end_cursor'],
            }
            yield from self.get_api_request(response, user, variables)

    def get_followings_item(self, follow_data, user):
        for item in follow_data['data']['user']['edge_follow']['edges']:
            yield InstaFollow(
                from_user_id=user['id'],
                to_user_id=item['node']['id'],
                date_parse=dt.datetime.utcnow()
            )
            yield InstaUser(
                id=item['node']['id'],
                username=item['node']['username'],
                date_parse=dt.datetime.utcnow()
            )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])