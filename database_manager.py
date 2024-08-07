import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name='user_ratings.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_ratings (
                user_id INTEGER PRIMARY KEY,
                rating INTEGER
            )
        ''')
        self.conn.commit()

    def set_user_rating(self, user_id, rating):
        self.cursor.execute('''
            INSERT OR REPLACE INTO user_ratings (user_id, rating)
            VALUES (?, ?)
        ''', (user_id, rating))
        self.conn.commit()

    def get_user_rating(self, user_id):
        self.cursor.execute('SELECT rating FROM user_ratings WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        if self.conn:
            self.conn.close()

    def __del__(self):
        self.close()