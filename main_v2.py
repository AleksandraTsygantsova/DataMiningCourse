from check_mutual import CheckMutual, GetFollow_List

import os
import time
from gb_parse.spiders.instagram_spider import InstagramSpider
import dotenv
dotenv.load_dotenv('.env')

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.log import configure_logging
configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

class Parser:
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)

    def start_crawl(self, user_list):
        print(f'Parse process for user {[user_list]} started')
        runner = self.crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'),
                              enc_password=os.getenv('PASSWORD'), user_from=user_list)
        self.crawl_proc.start()
        print(f'Parse process for user {[user_list]} finished')
        print('Reactor stopping, system sleep for a 15 sec.')
        time.sleep(15)

    def parse(self, user_list):
        self.start_crawl(user_list)
        self.crawl_proc.start()

class HandShaker:
    check = CheckMutual()
    follow = GetFollow_List()
    parser = Parser()

    def __init__(self, user_from, user_to):
        self.user_from = user_from
        self.user_to = user_to

        self.users_to_parse = []
        self.already_parsed_users =[]
        self.followers = []
        self.followings = []

    def check_mutual(self, user):
        followings = self.follow.get_followings_list(user)
        followers = self.follow.get_followers_list(user)
        mutuals_list = self.check.check_mutual(followings, followers)
        return mutuals_list

    def create_new_parsing_list(self, user):
        mutuals_list = self.check_mutual(user)
        self.already_parsed_users.append(user)
        new_unique_users = list(set(mutuals_list) - set(self.already_parsed_users))
        #print(f'New mutual users founded: {len(mutuals_list)}')
        #print(f'New unique users added to parse-list: {len(new_unique_users)}')
        self.users_to_parse = new_unique_users


    def run(self):
        if len(self.users_to_parse) == 0:
            self.users_to_parse.append(self.user_from)

        self.parser.parse(self.users_to_parse)
        for user in self.users_to_parse:
            if self.user_to in self.check_mutual(user):
                print(f'HandShake founded between {self.user_from} and {self.user_to} by {user}')
                break
            else:
                self.create_new_parsing_list(user)

        self.run()

    def result(self):
        pass

handshaker = HandShaker('rune.the.cat', 'valya_matveyeva')
handshaker.run()



