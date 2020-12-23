import sqlite3
import pandas as pd

class CheckMutual:
    conn = sqlite3.connect('instagramparse_demo.db')
    df = pd.read_sql("SELECT * FROM users JOIN followings WHERE users.id = followings.from_user_id", conn)
    cur = conn.cursor()

    def check_mutual(self, followings, followers):
        mutuals = list(set(followings) & set(followers))
        return mutuals

class GetFollow_List:
    conn = sqlite3.connect('instagramparse_demo.db')
    df = pd.read_sql("SELECT * FROM users JOIN followings WHERE users.id = followings.from_user_id", conn)
    cur = conn.cursor()

    def get_followings_list(self, user):
        df_followings = self.df.loc[self.df['from_username'] == user]['to_username'].values
        return df_followings

    def get_followers_list(self, user):
        df_followers = self.df.loc[self.df['to_username'] == user]['from_username'].values
        return df_followers


