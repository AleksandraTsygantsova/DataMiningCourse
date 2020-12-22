import sqlite3
import pandas as pd

class CheckMutual:
    conn = sqlite3.connect('instagramparse.db')
    df = pd.read_sql("SELECT * FROM users JOIN followings WHERE users.id = followings.from_user_id", conn)
    cur = conn.cursor()

    def __init__(self, user_list):
        self.user_list = user_list

    def check_mutual(self):
        pass