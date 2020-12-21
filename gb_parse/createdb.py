import sqlite3

conn = sqlite3.connect('instagramparse.db')
cur = conn.cursor()

cur.executescript("""
    create table users(
        id,
        username,
        date_parse
    );

    create table followings(
        from_user_id,
        to_user_id,
        date_parse
    );
    """)

conn.close()
