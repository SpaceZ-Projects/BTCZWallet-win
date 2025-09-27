
import sqlite3

from toga import App
from ...framework import Os




class StorageAddresses:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data
        self.data = Os.Path.Combine(str(self.app_data), 'addresses.dat')
        Os.FileStream(
            self.data,
            Os.FileMode.OpenOrCreate,
            Os.FileAccess.ReadWrite,
            Os.FileShare.ReadWrite
        )

    
    def create_addresses_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS addresses (
                type TEXT,
                change TEXT,
                address TEXT,
                balance REAL
            )
            '''
        )
        conn.commit()
        conn.close()


    def create_address_book_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS address_book (
                name TEXT,
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def insert_address(self, address_type, change, address, balance):
        self.create_addresses_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO addresses (type, change, address, balance)
            VALUES (?, ?, ?, ?)
            ''', 
            (address_type, change, address, balance)
        )
        conn.commit()
        conn.close()


    def insert_book(self, name, address):
        self.create_address_book_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO address_book (name, address)
            VALUES (?, ?)
            ''', 
            (name, address)
        )
        conn.commit()
        conn.close()


    def get_addresses(self, full = None ,address_type = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if address_type:
                cursor.execute(
                    'SELECT * FROM addresses WHERE type = ?',
                    (address_type,)
                )
                addresses = cursor.fetchall()
            elif full:
                cursor.execute('SELECT * FROM addresses')
                addresses = cursor.fetchall()
            else:
                cursor.execute('SELECT address FROM addresses')
                addresses = [row[0] for row in cursor.fetchall()]
            conn.close()
            return addresses
        except sqlite3.OperationalError:
            return []
        

    def get_address_balance(self, address):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT balance FROM addresses WHERE address = ?',
                (address,)
            )
            data = cursor.fetchone()
            conn.close()
            if data:
                return data[0]
            return None
        except sqlite3.OperationalError:
            return None
        

    def get_address_book(self, option=None, name = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if name:
                cursor.execute(
                    'SELECT address FROM address_book WHERE name = ?',
                    (name,)
                )
                address = cursor.fetchone()
                conn.close()
                return address
            
            if option == "address":
                cursor.execute('SELECT address FROM address_book')
                addresses = [row[0] for row in cursor.fetchall()]
            elif option == "name":
                cursor.execute('SELECT name FROM address_book')
                addresses = [row[0] for row in cursor.fetchall()]
            else:
                cursor.execute('SELECT * FROM address_book')
                addresses = cursor.fetchall()
            conn.close()
            return addresses
        except sqlite3.OperationalError:
            return []


    def update_balance(self, address, balance):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE addresses
            SET balance = ?
            WHERE address = ?
            ''', (balance, address)
        )
        conn.commit()
        conn.close()

    
    def delete_address_book(self, address):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM address_book WHERE address = ?
                ''', 
                (address,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting item: {e}")