
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


    def get_identity(self, option = None):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            if option == "category":
                cursor.execute(
                    "SELECT category FROM identity"
                )
                result = cursor.fetchone()
            elif option == "id":
                cursor.execute(
                    "SELECT id FROM identity"
                )
                result = cursor.fetchone()
            elif option == "username":
                cursor.execute(
                    "SELECT username FROM identity"
                )
                result = cursor.fetchone()
            elif option == "address":
                cursor.execute(
                    "SELECT address FROM identity"
                )
                result = cursor.fetchone()
            elif option is None:
                cursor.execute(
                    "SELECT category, id, username, address FROM identity"
                )
                result = cursor.fetchone()
            conn.close()
            return result
        except sqlite3.OperationalError:
            return None
    

    def add_contact(self, category, id, username, address):
        self.create_contacts_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO contacts (category, id, username, address)
            VALUES (?, ?, ?, ?)
            ''',
            (category, id, username, address)
        )
        conn.commit()
        conn.close()


    def add_pending(self, category, id, username, address):
        self.create_pending_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO pending (category, id, username, address)
            VALUES (?, ?, ?, ?)
            ''',
            (category, id, username, address)
        )
        conn.commit()
        conn.close()

    def add_request(self, address):
        self.create_requests_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO requests (address)
            VALUES (?)
            ''',
            (address,)
        )
        conn.commit()
        conn.close()

    def tx(self, txid):
        self.create_txs_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO txs (txid)
            VALUES (?)
            ''', 
            (txid,)
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

    def message(self, id, author, message, amount, timestamp):
        self.create_messages_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO messages (id, author, message, amount, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', 
            (id, author, message, amount, timestamp)
        )
        conn.commit()
        conn.close()


    def ban(self, address):
        self.create_messages_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO banned (address)
            VALUES (?)
            ''', 
            (address,)
        )
        conn.commit()
        conn.close()


    def get_contacts(self, option = None):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            if option == "address":
                cursor.execute('SELECT address FROM contacts')
                contacts = [row[0] for row in cursor.fetchall()]
            elif option is None:
                cursor.execute('SELECT * FROM contacts')
                contacts = cursor.fetchall()
            conn.close()
            return contacts
        except sqlite3.OperationalError:
            return []
        

    def get_pending(self, option = None):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            if option == "address":
                cursor.execute("SELECT address FROM pending")
                contacts = [row[0] for row in cursor.fetchall()]
            elif option is None:
                cursor.execute('SELECT * FROM pending')
                contacts = cursor.fetchall()
            conn.close()
            return contacts
        except sqlite3.OperationalError:
            return []
        
        
    def get_requests(self):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute('SELECT address FROM requests')
            txs = [row[0] for row in cursor.fetchall()]
            conn.close()
            return txs
        except sqlite3.OperationalError:
            return []
        

    def get_txs(self):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute('SELECT txid FROM txs')
            txs = [row[0] for row in cursor.fetchall()]
            conn.close()
            return txs
        except sqlite3.OperationalError:
            return []
        
    
    def get_messages(self, user_id):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT author, message, amount, timestamp FROM messages WHERE id = ?',
                (user_id,)
            )
            messages = cursor.fetchall()
            conn.close()
            return messages
        except sqlite3.OperationalError:
            return []
        

    def get_banned(self):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute('SELECT address FROM banned')
            txs = [row[0] for row in cursor.fetchall()]
            conn.close()
            return txs
        except sqlite3.OperationalError:
            return []
        

    def delete_pending(self, address):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM pending WHERE address = ?
                ''', 
                (address,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting pending contact: {e}")
        

    def delete_request(self, address):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM requests WHERE address = ?
                ''', 
                (address,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting request: {e}")


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

    def create_contacts_table(self):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS contacts (
                category TEXT,
                id TEXT,
                username TEXT,
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()

    def create_pending_table(self):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS pending (
                category TEXT,
                id TEXT,
                username TEXT,
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()

    def create_txs_table(self):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS txs (
                txid TEXT
            )
            '''
        )
        conn.commit()
        conn.close()

    def create_messages_table(self):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT,
                author TEXT,
                message TEXT,
                amount REAL,
                timestamp INTEGER
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

    def create_requests_table(self):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS requests (
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()

    def create_banned_table(self):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS banned (
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()