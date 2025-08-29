
import sqlite3

from toga import App
from ..framework import Os


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
            return data[0]
        except sqlite3.OperationalError:
            return None


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



class StorageTxs:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data
        self.data = Os.Path.Combine(str(self.app_data), 'transactions.dat')
        Os.FileStream(
            self.data,
            Os.FileMode.OpenOrCreate,
            Os.FileAccess.ReadWrite,
            Os.FileShare.ReadWrite
        )

    
    def create_transactions_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS transactions (
                type TEXT,
                category TEXT,
                address TEXT,
                txid TEXT,
                amount REAL,
                blocks INTEGER,
                fee INTEGER,
                timestamp INTEGER
            )
            '''
        )
        conn.commit()
        conn.close()


    def insert_transaction(self, tx_type, category, address, txid, amount, blocks, fee, timestamp):
        self.create_transactions_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO transactions (type, category, address, txid, amount, blocks, fee, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', 
            (tx_type, category, address, txid, amount, blocks, fee, timestamp)
        )
        conn.commit()
        conn.close()


    def get_transaction(self, txid):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM transactions WHERE txid = ?',
                (txid,)
            )
            transaction = cursor.fetchone()
            conn.close()
            return transaction
        except sqlite3.OperationalError:
            return []


    def get_transactions(self, option = None, tx_type = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if option:
                cursor.execute(
                    'SELECT txid FROM transactions WHERE type = ?',
                    (tx_type,)
                )
                transactions = [row[0] for row in cursor.fetchall()]
            else:
                cursor.execute('SELECT * FROM transactions')
                transactions = cursor.fetchall()
            conn.close()
            return transactions
        except sqlite3.OperationalError:
            return []
        

    def get_mobile_transactions(self, address):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM transactions WHERE category = mobile AND address = ?',
                (address,)
            )
            transactions = cursor.fetchall()
            conn.close()
            return transactions
        except sqlite3.OperationalError:
            return []
        

    def get_unconfirmed_transactions(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT txid FROM transactions WHERE blocks = 0')
            transactions = [row[0] for row in cursor.fetchall()]
            conn.close()
            return transactions
        except sqlite3.OperationalError:
            return []
        

    def update_transaction(self, txid, blocks):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE transactions
            SET blocks = ?
            WHERE txid = ?
            ''', (blocks, txid)
        )
        conn.commit()
        conn.close()

    



class StorageMessages:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data
        self.data = Os.Path.Combine(str(self.app_data), 'messages.dat')
        Os.FileStream(
            self.data,
            Os.FileMode.OpenOrCreate,
            Os.FileAccess.ReadWrite,
            Os.FileShare.ReadWrite
        )


    def is_exists(self):
        if not Os.File.Exists(self.data):
            return None
        return self.data

    
    def identity(self, category, username, address):
        self.create_identity_table()
        conn = sqlite3.connect(self.data)
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
            conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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

    def key(self, prv_key):
        self.create_key_table()
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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

    
    def tx(self, txid):
        self.create_txs_table()
        conn = sqlite3.connect(self.data)
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


    def insert_market(self, contact_id, hostname, secret):
        self.create_market_table()
        self.add_column('market', 'secret_key', 'TEXT')
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO market (contact_id, hostname, secret_key)
            VALUES (?, ?, ?)
            ''', 
            (contact_id, hostname, secret)
        )
        conn.commit()
        conn.close()


    def get_hostname(self, contact_id):
        try:
            self.add_column('market', 'secret_key', 'TEXT')
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT hostname, secret_key FROM market WHERE contact_id = ?',
                (contact_id,)
            )
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return None


    def get_txs(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT txid FROM txs')
            txs = [row[0] for row in cursor.fetchall()]
            conn.close()
            return txs
        except sqlite3.OperationalError:
            return []


    def get_contacts(self, option = None):
        try:
            conn = sqlite3.connect(self.data)
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
            conn = sqlite3.connect(self.data)
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
        

    def get_contact_address(self, contact_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT address FROM contacts WHERE contact_id = ?',
                (contact_id,)
            )
            contact = cursor.fetchone()
            conn.close()
            return contact
        except sqlite3.OperationalError:
            return None
        
    
    def get_id_contact(self, contact_id):
        try:
            conn = sqlite3.connect(self.data)
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
        

    def get_ids_contacts(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM contacts')
            data = cursor.fetchall()
            conn.close()
            return [row[0] for row in data]
        except sqlite3.OperationalError:
            return []
        

    def get_pending(self, option = None):
        try:
            conn = sqlite3.connect(self.data)
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
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT address FROM requests')
            txs = [row[0] for row in cursor.fetchall()]
            conn.close()
            return txs
        except sqlite3.OperationalError:
            return []
        
        
    def get_request(self, address):
        try:
            conn = sqlite3.connect(self.data)
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
        
    
    def get_messages(self, contact_id):
        try:
            conn = sqlite3.connect(self.data)
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
            conn = sqlite3.connect(self.data)
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
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT address FROM banned')
            txs = [row[0] for row in cursor.fetchall()]
            conn.close()
            return txs
        except sqlite3.OperationalError:
            return []
        

    def delete_pending(self, address):
        try:
            conn = sqlite3.connect(self.data)
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
            conn = sqlite3.connect(self.data)
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
            conn = sqlite3.connect(self.data)
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
            conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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

    def update_market(self, contact_id, hostname, secret):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE market
            SET hostname = ?, secret_key = ?
            WHERE contact_id = ?
            ''', (hostname, secret, contact_id)
        )
        conn.commit()
        conn.close()

    def create_pending_table(self):
        conn = sqlite3.connect(self.data)
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

    def create_messages_table(self):
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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

    def create_txs_table(self):
        conn = sqlite3.connect(self.data)
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

    def create_key_table(self):
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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
        conn = sqlite3.connect(self.data)
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


    def create_market_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS market (
                contact_id TEXT,
                hostname TEXT,
                secret_key TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def add_column(self, table_name, column_name, column_type):

        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]

        if column_name not in columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            conn.commit()

        conn.close()