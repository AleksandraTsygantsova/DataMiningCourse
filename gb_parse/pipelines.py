import sqlite3
from .items import InstaUser, InstaFollow

conn = sqlite3.connect('instagramparse_demo.db')
cur = conn.cursor()

cur.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id,
        username,
        date_parse
    );

    CREATE TABLE IF NOT EXISTS followings(
        from_user_id,
        from_username,
        to_user_id,
        to_username,
        date_parse
    );
    """)

conn.close()

class GbParsePipeline:
    def __init__(self):
        self.conn = sqlite3.connect('instagramparse_demo.db')
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        if isinstance(item, InstaUser):
            values = tuple(item.values())
            self.cur.execute('INSERT INTO users VALUES (?,?,?)', values)
            self.conn.commit()

        elif isinstance(item, InstaFollow):
            values = tuple(item.values())
            self.cur.execute('INSERT INTO followings VALUES (?,?,?,?,?)', values)
            self.conn.commit()
        return item
