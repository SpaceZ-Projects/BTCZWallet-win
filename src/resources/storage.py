
import sqlite3

from toga import App
from ..framework import Os

messages_data = 'messages.dat'


class Storage():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data
        self.data_path = Os.Path.Combine(str(self.app_data), messages_data)


    def is_exists(self):
        if not Os.File.Exists(self.data_path):
            return False
        return True
    

    def identity(self, category, id, username, address):
        self.create_identity_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO identity (category, id, username, address)
            VALUES (?, ?, ?, ?)
            ''', 
            (category, id, username, address)
        )
        conn.commit()
        conn.close()


    def key(self, prv_key):
        self.create_key_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO key (prv_key)
            VALUES (?)
            ''', 
            (prv_key,)
        )
        conn.commit()
        conn.close()


    def create_identity_table(self):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS identity (
                category TEXT,
                id TEXT,
                username TEXT,
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def create_key_table(self):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS key (
                prv_key TEXT
            )
            '''
        )
        conn.commit()
        conn.close()