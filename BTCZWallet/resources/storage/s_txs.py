
import sqlite3

from toga import App
from ...framework import Os



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
                'SELECT * FROM transactions WHERE address = ?',
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