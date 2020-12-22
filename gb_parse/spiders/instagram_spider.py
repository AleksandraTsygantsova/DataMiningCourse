import datetime as dt
import json
import scrapy
from ..items import InstaUser, InstaFollow
from scrapy.exceptions import CloseSpider


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    api_url = '/graphql/query/'
    query_hash = {
        'following': "d04b0a864b4b54837c0d870b0e77e076",
        'followers': "c76146de99bb02f6415203be841dd25a",
    }

    def __init__(self, login, enc_password, user_from, user_to, *args, **kwargs):
        self.login = login
        self.enc_passwd = enc_password
        self.user_from = user_from
        self.user_to = user_to
        self.user = [self.user_from]
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
                yield response.follow(f'/{self.user_from}', callback=self.user_parse)

    def user_parse(self, response):
        user = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']

        yield InstaUser(
            id=user['id'],
            username=user['username'],
            date_parse=dt.datetime.utcnow()
        )
        yield from self.get_api_following_request(response, user)
        yield from self.get_api_followers_request(response, user)

        if user['username'] == self.user_to:
            print(f'HandShake between {self.user_from} and {self.user_to} found')
            raise CloseSpider

    def get_api_following_request(self, response, user, variables=None):
        if variables is None:
            variables = {
                "id": user['id'],
                "include_reel": 'true',
                "fetch_mutual": 'false',
                "first": 100,
            }
        url_following = f'{self.api_url}?query_hash={self.query_hash["following"]}&variables={json.dumps(variables)}'
        yield response.follow(url_following, callback=self.get_followings, cb_kwargs={'user': user, 'query_hash': self.query_hash["following"]})

    def get_api_followers_request(self, response, user, variables=None):
        if variables is None:
            variables = {
                "id": user['id'],
                "include_reel": 'true',
                "fetch_mutual": 'false',
                "first": 100,
            }
        url_follower = f'{self.api_url}?query_hash={self.query_hash["followers"]}&variables={json.dumps(variables)}'
        yield response.follow(url_follower, callback=self.get_followings, cb_kwargs={'user': user, 'query_hash': self.query_hash["followers"]})

    def get_followings(self, response, user, query_hash):
        follow_data = response.json()
        yield from self.get_followings_item(response, follow_data, user, query_hash)
        if query_hash == self.query_hash["following"]:
            if follow_data['data']['user']['edge_follow']['page_info']['has_next_page']:
                variables = {
                    'id': user['id'],
                    'first': 100,
                    'after': follow_data['data']['user']['edge_follow']['page_info']['end_cursor'],
                }
                yield from self.get_api_following_request(response, user, variables)
        else:
            if follow_data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
                variables = {
                    'id': user['id'],
                    'first': 100,
                    'after': follow_data['data']['user']['edge_followed_by']['page_info']['end_cursor'],
                }
                yield from self.get_api_followers_request(response, user, variables)

    def get_followings_item(self, response, follow_data, user, query_hash):
        if query_hash == self.query_hash["following"]:
            for item in follow_data['data']['user']['edge_follow']['edges']:
                yield InstaFollow(
                    from_user_id=user['id'],
                    from_username=user['username'],
                    to_user_id=item['node']['id'],
                    to_username=item['node']['username'],
                    date_parse=dt.datetime.utcnow()
                )

                yield InstaUser(
                    id=item['node']['id'],
                    username=item['node']['username'],
                    date_parse=dt.datetime.utcnow()
                )

                self.user.append(item['node']['username'])

        else:
            for item in follow_data['data']['user']['edge_followed_by']['edges']:
                yield InstaFollow(
                    from_user_id=item['node']['id'],
                    from_username=item['node']['username'],
                    to_user_id=user['id'],
                    to_username=user['username'],
                    date_parse=dt.datetime.utcnow()
                )

                yield InstaUser(
                    id=item['node']['id'],
                    username=item['node']['username'],
                    date_parse=dt.datetime.utcnow()
                )

        try:
            self.user.pop(self.user.index(user['username']))

        except ValueError:
            pass

        for user in self.user:
            yield response.follow(url=f'https://www.instagram.com/{user}/', callback=self.user_parse)

    def check_mutual(self):
        pass

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])