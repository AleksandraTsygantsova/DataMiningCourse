import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram_spider import InstagramSpider
import dotenv
dotenv.load_dotenv('.env')

import sqlite3
import pandas as pd

class HandShakers:
    def __init__(self, user_from, user_to):
        # matching methods
        self.user_from = user_from
        self.user_to = user_to
        self.user_list = []
        self.user_match = ''
        # db methods
        self.conn = sqlite3.connect('instagramparse.db')
        self.cur = self.conn.cursor()
        # scrapy methods
        self.crawl_settings = Settings()
        self.crawl_settings.setmodule('gb_parse.settings')
        self.crawl_proc = CrawlerProcess(settings=self.crawl_settings)

    def parse(self):
        self.crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'),
                              enc_password=os.getenv('PASSWORD'), user_from=self.user_from, user_to=self.user_to)
        self.crawl_proc.start()
        print('Database ready')

    def find_relation(self):
        df = pd.read_sql("SELECT * FROM users JOIN followings WHERE users.id = followings.from_user_id", self.conn,
                         index_col=None)
        # get id's of user from and user to
        user_from_id = df.loc[df['username'] == self.user_from]['id'].values[0]
        user_to_id = df.loc[df['username'] == self.user_to]['id'].values[0]

        if len(self.user_list) == 0:
            self.user_list.append(user_from_id)

        # start circle of check followings and followers
        for user in self.user_list:
            if self.check_is_following(df, user, user_to_id) is True:
                user_match_username = df.loc[df['id'] == self.user_match]['username'].values[0]
                print(f'Matching found from {self.user_from} to {self.user_to}: '
                      f'{self.user_to} followed by {user_match_username}')
            else:
                print('...')
                self.find_relation()

    def check_is_following(self, df, user_from_id, user_to_id):
        df_filter = df.loc[df['id'] == user_from_id]

        start = 0
        for i in range(1, len(df_filter)+1):
            user_id = df_filter[start:i]['to_user_id'].values[0]
            if user_id == user_to_id:
                self.user_match = user_id
                self.user_list.append(user_id)
                try:
                    self.user_list.pop(self.user_list.index(user_from_id))
                except ValueError:
                    pass
                return True
            else:
                start += 1

# Введите имена пользователей между которыми необходимо найти связь.
user_from = 'rune.the.cat'
user_to = 'just_one_mari'

handshaker = HandShakers(user_from=user_from, user_to=user_to)
handshaker.parse()
handshaker.find_relation()


