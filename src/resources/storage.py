
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
        return self.data_path
    
    def identity(self, category, username, address):
        self.create_identity_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO identity (category, username, address)
            VALUES (?, ?, ?)
            ''', 
            (category, username, address)
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
                    "SELECT category, username, address FROM identity"
                )
                result = cursor.fetchone()
            conn.close()
            return result
        except sqlite3.OperationalError:
            return None
    

    def add_contact(self, category, id, contact_id, username, address):
        self.create_contacts_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO contacts (category, id, contact_id, username, address)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (category, id, contact_id, username, address)
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

    def add_request(self, id, address):
        self.create_requests_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO requests (id, address)
            VALUES (?, ?)
            ''',
            (id, address)
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


    def unread_message(self, id, author, message, amount, timestamp):
        self.create_unread_messages_table()
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO unread_messages (id, author, message, amount, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', 
            (id, author, message, amount, timestamp)
        )
        conn.commit()
        conn.close()


    def ban(self, address):
        self.create_banned_table()
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
            elif option == "contact_id":
                cursor.execute('SELECT contact_id FROM contacts')
                contacts = [row[0] for row in cursor.fetchall()]
            elif option is None:
                cursor.execute('SELECT * FROM contacts')
                contacts = cursor.fetchall()
            conn.close()
            return contacts
        except sqlite3.OperationalError:
            return []
        

    def get_contact_username(self, contact_id):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT username FROM contacts WHERE contact_id = ?',
                (contact_id,)
            )
            contact = cursor.fetchone()
            conn.close()
            return contact
        except sqlite3.OperationalError:
            return None
        
    
    def get_id_contact(self, contact_id):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM contacts WHERE contact_id = ?',
                (contact_id,)
            )
            id = cursor.fetchone()
            conn.close()
            return id
        except sqlite3.OperationalError:
            return None
        

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
        
        
    def get_request(self, address):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM requests WHERE address = ?',
                (address,)
            )
            request = cursor.fetchone()
            conn.close()
            return request
        except sqlite3.OperationalError:
            return None
        

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
        
    
    def get_messages(self, contact_id):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT author, message, amount, timestamp FROM messages WHERE id = ?',
                (contact_id,)
            )
            messages = cursor.fetchall()
            conn.close()
            return messages
        except sqlite3.OperationalError:
            return []
        

    def get_unread_messages(self, contact_id):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT author, message, amount, timestamp FROM unread_messages WHERE id = ?',
                (contact_id,)
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


    def delete_contact(self, address):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM contacts WHERE address = ?
                ''', 
                (address,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting contact: {e}")
        

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


    def delete_unread(self, contact_id):
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM unread_messages WHERE id = ?
                ''', 
                (contact_id,)
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
                username TEXT,
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def edit_username(self, old_username, new_username):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE identity
            SET username = ?
            WHERE username = ?
            ''', (new_username, old_username)
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
                contact_id TEXT,
                username TEXT,
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()

    def update_contact_username(self, username, contact_id):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE contacts
            SET username = ?
            WHERE contact_id = ?
            ''', (username, contact_id)
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

    def create_unread_messages_table(self):
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS unread_messages (
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
                id TEXT,
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