import sqlite3
import pandas as pd

def connect_to_db():
    conn = sqlite3.connect('instagramparse_demo.db')
    df = pd.read_sql("SELECT * FROM users JOIN followings WHERE users.id = followings.from_user_id", conn)
    cur = conn.cursor()
    return conn, df, cur

def check_mutual(followings, followers):
    mutuals = list(set(followings) & set(followers))
    return mutuals

def get_followings_list(user, df):
    followings = df.loc[df['from_username'] == user]['to_username'].values
    return followings

def get_followers_list(user, df):
    followers = df.loc[df['to_username'] == user]['from_username'].values
    return followers

class GenerateNewUserToParse:
    conn, df, cur = connect_to_db()

    def run_generator(self, user):
        # проверка взаимных подписок
        followings = get_followings_list(user, self.df)
        followers = get_followers_list(user, self.df)
        mutuals = check_mutual(followings, followers)
        return mutuals

