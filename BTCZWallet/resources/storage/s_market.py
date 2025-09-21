
import sqlite3

from toga import App
from ...framework import Os


class StorageMarket:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data
        self.data = Os.Path.Combine(str(self.app_data), 'marketplace.dat')
        Os.FileStream(
            self.data,
            Os.FileMode.OpenOrCreate,
            Os.FileAccess.ReadWrite,
            Os.FileShare.ReadWrite
        )

    def create_items_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS market_items (
                id TEXT,
                title TEXT,
                image TEXT,
                description TEXT,
                price REAL,
                currency TEXT,
                quantity INTEGER,
                timestamp INTEGER
            )
            '''
        )
        conn.commit()
        conn.close()


    def create_orders_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS market_orders (
                order_id TEXT,
                item_id TEXT,
                contact_id TEXT,
                total_price REAL,
                quantity INTEGER,
                comment TEXT,
                status TEXT,
                created INTEGER,
                expired INTEGER
            )
            '''
        )
        conn.commit()
        conn.close()


    def create_secret_keys_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS secret_keys (
                contact_id TEXT,
                secret_key TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def insert_item(self, id, title, image, description, price, currency, quantity, timestamp):
        self.create_items_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO market_items (id, title, image, description, price, currency, quantity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', 
            (id, title, image, description, price, currency, quantity, timestamp)
        )
        conn.commit()
        conn.close()


    def insert_order(self, order_id, item_id, contact_id, total_price, quantity, comment, status, created, expired):
        self.create_orders_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO market_orders (order_id, item_id, contact_id, total_price, quantity, comment, status, created, expired)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', 
            (order_id, item_id, contact_id, total_price, quantity, comment, status, created, expired)
        )
        conn.commit()
        conn.close()


    def insert_secret(self, contact_id, secret):
        self.create_secret_keys_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO secret_keys (contact_id, secret_key)
            VALUES (?, ?)
            ''', 
            (contact_id, secret)
        )
        conn.commit()
        conn.close()


    def get_secret(self, contact_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT secret_key FROM secret_keys WHERE contact_id = ?',
                (contact_id,)
            )
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return None


    def delete_item(self, item_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM market_items WHERE id = ?
                ''', 
                (item_id,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting item: {e}")


    def get_market_items(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM market_items')
            data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        

    def get_market_orders(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM market_orders')
            data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        

    def get_orders_by_contact_id(self, contact_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM market_orders WHERE contact_id = ?',
                (contact_id,)
            )
            data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        

    def get_item(self, item_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM market_items WHERE id = ?',
                (item_id,)
            )
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        
        
    def get_item_title(self, item_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT title FROM market_items WHERE id = ?',
                (item_id,)
            )
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        

    def get_order(self, order_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM market_orders WHERE order_id = ?',
                (order_id,)
            )
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        

    def search_title(self, title):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM market_items
                WHERE title LIKE ?
                ''',
                (f'%{title}%',)
            )
            data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        

    def update_item_quantity(self, id, quantity):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE market_items
            SET quantity = ?
            WHERE id = ?
            ''', (quantity, id)
        )
        conn.commit()
        conn.close()


    def update_order_status(self, order_id, status):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE market_orders
            SET status = ?
            WHERE order_id = ?
            ''', (status, order_id)
        )
        conn.commit()
        conn.close()