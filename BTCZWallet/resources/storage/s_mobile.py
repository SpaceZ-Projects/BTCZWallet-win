import sqlite3

from toga import App
from ...framework import Os



class StorageMobile:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data
        self.data = Os.Path.Combine(str(self.app_data), 'mobile.dat')
        Os.FileStream(
            self.data,
            Os.FileMode.OpenOrCreate,
            Os.FileAccess.ReadWrite,
            Os.FileShare.ReadWrite
        )

    
    def create_mobile_devices_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS mobile_devices (
                id TEXT,
                name TEXT,
                taddress TEXT,
                zaddress TEXT,
                status TEXT,
                timestamp INTEGER
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
                id TEXT,
                secret_key TEXT
            )
            '''
        )
        conn.commit()
        conn.close()

    
    def create_mining_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS mining (
                miner TEXT,
                address TEXT,
                pool TEXT,
                region TEXT,
                worker TEXT,
                shares REAL,
                balance REAL,
                immature REAL,
                paid REAL,
                solutions REAL,
                reward REAL
            )
            '''
        )
        conn.commit()
        conn.close()

    
    def insert_device(self, id, name, taddress, zaddress):
        self.create_mobile_devices_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO mobile_devices (id, name, taddress, zaddress, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', 
            (id, name, taddress, zaddress, None, None)
        )
        conn.commit()
        conn.close()

    
    def insert_secret(self, device_id, secret):
        self.create_secret_keys_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO secret_keys (id, secret_key)
            VALUES (?, ?)
            ''', 
            (device_id, secret)
        )
        conn.commit()
        conn.close()


    def insert_mining_stats(self, miner, address, pool, region, worker, shares, balance, immature, paid, solutions, reward):
        self.create_mining_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO mining (miner, address, pool, region, worker, shares, balance, immature, paid, solutions, reward)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', 
            (miner, address, pool, region, worker, shares, balance, immature, paid, solutions, reward)
        )
        conn.commit()
        conn.close()


    def get_secret(self, device_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT secret_key FROM secret_keys WHERE id = ?',
                (device_id,)
            )
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return None
        

    def get_mining_stats(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM mining')
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return None
        

    def update_mining_stats(self, miner, address, pool, region, worker, shares, balance, immature, paid, solutions, reward):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE mining
            SET miner = ?, address = ?, pool = ?, region = ?, worker = ?,
                shares = ?, balance = ?, immature = ?, paid = ?, solutions = ?, reward = ?
            ''', (miner, address, pool, region, worker, shares, balance, immature, paid, solutions, reward)
        )
        conn.commit()
        conn.close()


    def delete_device(self, device_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM mobile_devices WHERE id = ?
                ''', 
                (device_id,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting item: {e}")

    
    def delete_secret(self, device_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM secret_keys WHERE id = ?
                ''', 
                (device_id,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting item: {e}")


    def update_device_addresses(self, id, taddress, zaddress):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE mobile_devices
            SET taddress = ?, zaddress = ?
            WHERE id = ?
            ''', (taddress, zaddress, id)
        )
        conn.commit()
        conn.close()

    
    def update_device_status(self, id, status):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE mobile_devices
            SET status = ?
            WHERE id = ?
            ''', (status, id)
        )
        conn.commit()
        conn.close()


    def update_device_connected(self, id, timestamp):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE mobile_devices
            SET timestamp = ?
            WHERE id = ?
            ''', (timestamp, id)
        )
        conn.commit()
        conn.close()


    def get_auth_ids(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM mobile_devices')
            data = cursor.fetchall()
            conn.close()
            return [row[0] for row in data]
        except sqlite3.OperationalError:
            return []
        

    def get_devices(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM mobile_devices')
            data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        

    def get_connected_devices(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM mobile_devices WHERE status = ?",
                ("on",)
            )
            data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        

    def get_device_addresses(self, id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT taddress, zaddress FROM mobile_devices WHERE id = ?',
                (id,)
            )
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return None
        

    def get_addresses_list(self, address_type):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(f'SELECT {address_type} FROM mobile_devices')
            data = cursor.fetchall()
            conn.close()
            return [row[0] for row in data]
        except sqlite3.OperationalError:
            return []