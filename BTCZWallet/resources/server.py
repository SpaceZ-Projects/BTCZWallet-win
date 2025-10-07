
import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone
import hmac
import hashlib
from threading import Thread, Event
from flask import Flask, request, jsonify
from werkzeug.serving import make_server
import socket

from toga import App
from ..framework import Sys, Os

from .client import Client
from .units import Units


def get_secret(id, storage):
    secret = storage.get_secret(id)
    if secret:
        return secret[0]
    return None


def encrypt_data(id, storage, units, data):
    secret = get_secret(id, storage)
    encrypted = units.encrypt_data(secret, data)
    return encrypted


def decrypt_data(id, storage, units, data):
    secret = get_secret(id, storage)
    decrypted = units.decrypt_data(secret, data)
    return decrypted


def verify_signature(list_ids, storage, units = None):
    id = request.headers.get('Authorization')
    timestamp = request.headers.get('X-Timestamp')
    signature = request.headers.get('X-Signature')

    if not id or not timestamp or not signature:
        return False, (jsonify({'error': 'Missing headers'}), 400)

    if id not in list_ids:
        return False, (jsonify({'error': 'Unauthorized'}), 401)

    try:
        request_time = datetime.fromisoformat(timestamp)
        if request_time.tzinfo is None:
            request_time = request_time.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - request_time
        if delta < timedelta(seconds=-5) or delta > timedelta(seconds=30):
            return False, (jsonify({'error': 'Request expired'}), 403)
    except ValueError:
        return False, (jsonify({'error': 'Invalid timestamp'}), 400)

    try:
        secret = get_secret(id, storage)

        if "data" in request.args:
            ciphertext_b64 = request.args.get("data")
            try:
                plaintext_json = decrypt_data(id, storage, units, ciphertext_b64)
                body = json.loads(plaintext_json)
            except Exception as e:
                return False, (jsonify({"error": "Decryption failed"}), 400)
            
        elif request.method == 'GET':
            body = request.args.to_dict(flat=True)
        else:
            body = {}
        secret = get_secret(id, storage)
        message = f"{timestamp}.{json.dumps(body, separators=(',', ':'), sort_keys=True)}"
        expected_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            return False, (jsonify({'error': 'Invalid signature'}), 403)

    except Exception as e:
        print(f"Signature verification error: {e}")
        return False, (jsonify({'error': 'Signature verification failed'}), 500)

    return True, None



class ServerThread(Thread):
    def __init__(self, app:App, flask, host, port, event):
        Thread.__init__(self, daemon=True)

        self.app = app
        self.flask = flask
        self.host = host
        self.port = port
        self.event = event

    def run(self):
        try:
            self.http_server = make_server(
                self.host,
                self.port,
                self.flask,
                threaded=True
            )
            self.event.set()
            self.http_server.serve_forever()
        except socket.gaierror as e:
            print(f"Error: DNS resolution failed for host {self.host}. Error: {e}")
        except Exception as e:
            print(e)

    def shutdown(self):
        if self.http_server:
            try:
                self.event.clear()
                self.http_server.shutdown()
                self.http_server.server_close()
            except Exception as e:
                print(e)


class MarketServer():
    def __init__(
        self,
        app:App,
        host:str = None,
        port:int = None,
        market_storage = None,
        messages_storage = None,
        settings = None,
        notify = None
    ):
        self.host = host
        self.port = port
        self.market_storage = market_storage
        self.messages_storage = messages_storage
        self.settings = settings
        self.notify = notify

        self.app = app
        self.commands = Client(self.app)
        self.units = Units(self.app, self.commands)
        self.server_status = None

        self.flask = Flask(
            __name__,
            static_folder=Os.Path.Combine(str(self.app.paths.data), "items"),
            static_url_path="/static"
        )
        Sys.Environment.SetEnvironmentVariable(
            'FLASK_ENV', 'production', Sys.EnvironmentVariableTarget.Process
        )

        self.add_rules()

    def add_rules(self):
        self.flask.add_url_rule('/status', 'status', self.handle_status, methods=['GET'])
        self.flask.add_url_rule('/items', 'items', self.handle_items_list, methods=['GET'])
        self.flask.add_url_rule('/orders', 'orders', self.handle_orders_list, methods=['GET'])
        self.flask.add_url_rule('/item/<string:item_id>', 'item', self.handle_item_id, methods=['GET'])
        self.flask.add_url_rule('/price', 'price', self.handle_price, methods=['GET'])
        self.flask.add_url_rule('/place_order', 'place_order', self.handle_place_order, methods=['GET'])
        self.flask.add_url_rule('/cancel_order', 'cancel_order', self.handle_cancel_order, methods=['GET'])
        self.flask.before_request(self.log_request)


    def log_request(self):
        self.app.add_background_task(self.get_request_log)
    
    def get_request_log(self, widget):
        if request.method == 'GET':
            if request.args:
                self.app.console.server_log(f"[MARKET]Request Data: {dict(request.form)}")

            self.app.console.server_log(
                f"[MARKET]{request.remote_addr} {request.method} {request.path}"
            )


    def handle_status(self):
        contacts_ids = self.messages_storage.get_ids_contacts()
        valid, response = verify_signature(contacts_ids, self.market_storage)
        if not valid:
            return response
        return jsonify({'status': 'online'}), 200
    

    def handle_items_list(self):
        contacts_ids = self.messages_storage.get_ids_contacts()
        valid, response = verify_signature(contacts_ids, self.market_storage)
        if not valid:
            return response
        contact_id = request.headers.get('Authorization')
        market_items = self.market_storage.get_market_items()
        if not market_items:
            return jsonify([]), 200
        sorted_items = sorted(market_items, key=lambda x: x[7], reverse=True)
        result = []
        for item in sorted_items:
            image_filename = item[2]
            image_url = (
                f"{request.host_url.rstrip('/')}/static/{image_filename}"
                if image_filename else None
            )
            item_dict = {
                "id": item[0],
                "title": item[1],
                "image": image_url,
                "description": item[3],
                "price": item[4],
                "currency": item[5],
                "quantity": item[6],
                "timestamp": item[7],
            }
            result.append(item_dict)
        encrypted_data = encrypt_data(contact_id, self.market_storage, self.units, json.dumps(result))
        return jsonify({"data": encrypted_data})
    

    def handle_item_id(self, item_id):
        contacts_ids = self.messages_storage.get_ids_contacts()
        valid, response = verify_signature(contacts_ids, self.market_storage, self.units)
        if not valid:
            return response
        contact_id = request.headers.get('Authorization')

        item = self.market_storage.get_item(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        encrypted_data = request.args.get("data")
        decrypted_json = decrypt_data(contact_id, self.market_storage, self.units, encrypted_data)
        get_params = json.loads(decrypted_json)

        quantity = get_params.get("get")
        if quantity:
            return jsonify({"quantity": item[6]}), 200
        

    def handle_price(self):
        contacts_ids = self.messages_storage.get_ids_contacts()
        valid, response = verify_signature(contacts_ids, self.market_storage)
        if not valid:
            return response
        btcz_price = self.settings.price()
        return jsonify({"price": btcz_price}), 200
    

    def handle_place_order(self):
        contacts_ids = self.messages_storage.get_ids_contacts()
        valid, response = verify_signature(contacts_ids, self.market_storage, self.units)
        if not valid:
            return response
        
        contact_id = request.headers.get('Authorization')
        
        encrypted_data = request.args.get("data")
        decrypted_json = decrypt_data(contact_id, self.market_storage, self.units, encrypted_data)
        get_params = json.loads(decrypted_json)

        required_params = ["id", "contact_id", "total_price", "quantity"]
        missing = [p for p in required_params if not get_params.get(p)]
        if missing:
            return jsonify({"error": f"Missing required parameters: {', '.join(missing)}"}), 400
        
        item_id = get_params.get("id")
        contact_id = get_params.get("contact_id")
        contacts_order = self.market_storage.get_orders_by_contact_id(contact_id)
        for order in contacts_order:
            order_item_id = order[1]
            order_status = order[6]
            if order_status == "pending" and order_item_id == item_id:
                return jsonify({"failed": "Pending order with this item already exists."}), 400
            
        total_price = get_params.get("total_price")
        quantity = get_params.get("quantity")
        comment = get_params.get("comment")
        
        status = "pending"
        order_id = str(uuid.uuid4())
        created = int(datetime.now(timezone.utc).timestamp())
        expired = 3600
        duration = created + expired

        self.market_storage.insert_order(
            order_id, item_id, contact_id, total_price, int(quantity), comment, status, created, duration)
        
        item = self.market_storage.get_item(item_id)
        available_items = item[6] - int(quantity)
        self.market_storage.update_item_quantity(item_id, available_items)
        self.notify.send_note(
            title="New Order",
            text=f"Order ID : {order_id}"
        )

        return jsonify({"result": "success"}), 200
    

    def handle_orders_list(self):
        contacts_ids = self.messages_storage.get_ids_contacts()
        valid, response = verify_signature(contacts_ids, self.market_storage)
        if not valid:
            return response
        contact_id = request.headers.get('Authorization')
        if not contact_id:
            return jsonify({"error": "Missing required parameter: contact_id"}), 400
        
        try:
            market_orders = self.market_storage.get_orders_by_contact_id(contact_id)
        except Exception:
            return jsonify({"error": "Internal server error while retrieving orders"}), 500
        
        if not market_orders:
            return jsonify([]), 200
        
        sorted_orders = sorted(market_orders, key=lambda x: x[7], reverse=True)
        result = []
        now = int(datetime.now(timezone.utc).timestamp())
        for order in sorted_orders:
            expired = order[8]
            item_title = self.market_storage.get_item_title(order[1])
            remaining_seconds = expired - now
            item_dict = {
                "order_id": order[0],
                "item_id": order[1],
                "item_title": item_title[0],
                "total_price": order[3],
                "quantity": order[4],
                "comment": order[5],
                "status": order[6],
                "remaining": remaining_seconds
            }
            result.append(item_dict)
        encrypted_data = encrypt_data(contact_id, self.market_storage, self.units, json.dumps(result))
        return jsonify({"data": encrypted_data})
    
    

    def handle_cancel_order(self):
        contacts_ids = self.messages_storage.get_ids_contacts()
        valid, response = verify_signature(contacts_ids, self.market_storage, self.units)
        if not valid:
            return response
        contact_id = request.headers.get('Authorization')
        
        encrypted_data = request.args.get("data")
        decrypted_json = decrypt_data(contact_id, self.market_storage, self.units, encrypted_data)
        get_params = json.loads(decrypted_json)

        required_params = ["order_id"]
        missing = [p for p in required_params if not get_params.get(p)]
        if missing:
            return jsonify({"error": f"Missing required parameters: {', '.join(missing)}"}), 400
        
        order_id = get_params.get("order_id")
        order = self.market_storage.get_order(order_id)

        status = order[6]

        if status == "expired":
            return jsonify({"result": "expired", "reason": "Order already cancelled"}), 200

        if status == "cancelled":
            return jsonify({"result": "failed", "reason": "Order already cancelled"}), 200
        
        if status != "pending":
            return jsonify({"error": "Order cannot be cancelled in its current state"}), 400

        self.market_storage.update_order_status(order_id, "cancelled")
        item = self.market_storage.get_item(order[1])
        quantity = order[4] + item[6]
        self.market_storage.update_item_quantity(order[1] ,quantity)

        return jsonify({"result": "success"}), 200
        
    
    def start(self):
        event = Event()
        self.server_thread = ServerThread(self.app, self.flask, self.host, self.port, event)
        self.server_thread.start()
        if event.wait(timeout=5):
            self.app.console.server_log(f"🛒: Server started and listening to {self.host}:{self.port}")
            self.server_status = True
            return True
        else:
            self.app.console.error_log("Server failed to start within the timeout period.")
            return None

    def stop(self):
        self.app.console.warning_log("🛒: Shutdown server")
        self.server_status = None
        self.server_thread.shutdown()




class MobileServer():
    def __init__(
        self,
        app:App,
        main,
        host:str = None,
        port:int = None,
        mobile_storage = None,
        txs_storage = None,
        addresses_storage = None,
        settings = None,
        notify = None
    ):
        self.host = host
        self.port = port
        self.mobile_storage = mobile_storage
        self.txs_storage = txs_storage
        self.addresses_storage = addresses_storage
        self.settings = settings
        self.notify = notify

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.units = Units(self.app, self.commands)
        self.server_status = None
        self.current_blocks = None
        
        self.flask = Flask(__name__)
        Sys.Environment.SetEnvironmentVariable(
            'FLASK_ENV', 'production', Sys.EnvironmentVariableTarget.Process
        )

        self.add_rules()

    def add_rules(self):
        self.flask.add_url_rule('/status', 'status', self.handle_status, methods=['GET'])
        self.flask.add_url_rule('/addresses', 'addresses', self.handle_addresses, methods=['GET'])
        self.flask.add_url_rule('/book', 'book', self.handle_book, methods=['GET'])
        self.flask.add_url_rule('/balances', 'balances', self.handle_balances, methods=['GET'])
        self.flask.add_url_rule('/mining', 'mining', self.handle_mining, methods=['GET'])
        self.flask.add_url_rule('/transactions', 'transactions', self.handle_transactions, methods=['GET'])
        self.flask.add_url_rule('/cashout', 'cashout', self.handle_cashout, methods=['GET'])
        self.flask.before_request(self.log_request)


    def log_request(self):
        self.app.add_background_task(self.get_request_log)

    def get_request_log(self, widget):
        if request.method == 'GET':
            if request.args:
                self.app.console.server_log(f"[MOBILE]Request Data: {dict(request.form)}")

            self.app.console.server_log(
                f"[MOBILE]{request.remote_addr} {request.method} {request.path}"
            )
    

    def handle_status(self):
        mobile_ids = self.mobile_storage.get_auth_ids()
        valid, response = verify_signature(mobile_ids, self.mobile_storage)
        if not valid:
            return response
        self.update_device_status()
        height = self.current_blocks
        currency = self.settings.currency()
        price = self.settings.price()
        version = self.app.version
        data = {
            'version': version,
            'height': height,
            'currency': currency,
            'price': price
        }

        mobile_id = request.headers.get("Authorization")
        encrypted_data = encrypt_data(mobile_id, self.mobile_storage, self.units, json.dumps(data))

        return jsonify({"data": encrypted_data}), 200
    

    def handle_addresses(self):
        mobile_ids = self.mobile_storage.get_auth_ids()
        valid, response = verify_signature(mobile_ids, self.mobile_storage)
        if not valid:
            return response
        self.update_device_status()
        mobile_id = request.headers.get('Authorization')
        taddress, zaddress = self.mobile_storage.get_device_addresses(mobile_id)
        data = {
            'transparent': taddress,
            'shielded': zaddress
        }
        encrypted_data = encrypt_data(mobile_id, self.mobile_storage, self.units, json.dumps(data))

        return jsonify({"data": encrypted_data}), 200
    
    
    async def handle_book(self):
        mobile_ids = self.mobile_storage.get_auth_ids()
        valid, response = verify_signature(mobile_ids, self.mobile_storage, self.units)
        if not valid:
            return response
        self.update_device_status()

        mobile_id = request.headers.get('Authorization')

        encrypted_data = request.args.get("data")
        decrypted_json = decrypt_data(mobile_id, self.mobile_storage, self.units, encrypted_data)
        params = json.loads(decrypted_json)

        if "get" in params:
            result = []
            address_book = self.addresses_storage.get_address_book()
            for data in address_book:
                book_dict = {
                    "name": data[0],
                    "address": data[1]
                }
                result.append(book_dict)
            encrypted_data = encrypt_data(mobile_id, self.mobile_storage, self.units, json.dumps(result))
            return jsonify({"data": encrypted_data})
        
        elif "name" in params:
            name = params.get('name')
            address = params.get('address')

            is_valid = await self.is_valid(address)
            if not is_valid:
                return jsonify({"error": "Invalid address"}), 400
            
            address_book = self.addresses_storage.get_address_book("address")
            if address in address_book:
                return jsonify({"error": "Address is already exists"}), 400
            
            address_book = self.addresses_storage.get_address_book("name")
            if name in address_book:
                return jsonify({"error": "Name is already exists"}), 400
            
            self.addresses_storage.insert_book(name, address)
            return jsonify({"result": "success"}), 200
    
    
    def handle_balances(self):
        mobile_ids = self.mobile_storage.get_auth_ids()
        valid, response = verify_signature(mobile_ids, self.mobile_storage)
        if not valid:
            return response
        self.update_device_status()
        mobile_id = request.headers.get('Authorization')
        taddress, zaddress = self.mobile_storage.get_device_addresses(mobile_id)
        tbalance = self.addresses_storage.get_address_balance(taddress)
        zbalance = self.addresses_storage.get_address_balance(zaddress)
        data = {
            'transparent': tbalance,
            'shielded': zbalance
        }
        encrypted_data = encrypt_data(mobile_id, self.mobile_storage, self.units, json.dumps(data))
        return jsonify({"data": encrypted_data}), 200
    

    def handle_mining(self):
        mobile_ids = self.mobile_storage.get_auth_ids()
        valid, response = verify_signature(mobile_ids, self.mobile_storage)
        if not valid:
            return response
        if not self.main.mining_page.mining_status:
            return jsonify({"error": "Mining is currently turned off"}), 400
        
        mobile_id = request.headers.get('Authorization')
        stats = self.mobile_storage.get_mining_stats()
        if stats:
            mining_dict = {
                "miner": stats[0],
                "address": stats[1],
                "pool": stats[2],
                "region": stats[3],
                "worker": stats[4],
                "shares": stats[5],
                "balance": stats[6],
                "immature": stats[7],
                "paid": stats[8],
                "solutions": stats[9],
                "reward": stats[10],
            }
            encrypted_data = encrypt_data(mobile_id, self.mobile_storage, self.units, json.dumps(mining_dict))
            return jsonify({"data": encrypted_data})

        return jsonify({"error": "No mining stats found"}), 404
    

    def handle_transactions(self):
        mobile_ids = self.mobile_storage.get_auth_ids()
        valid, response = verify_signature(mobile_ids, self.mobile_storage)
        if not valid:
            return response
        self.update_device_status()
        transactions_data = []
        result = []
        mobile_id = request.headers.get('Authorization')
        addresses = self.mobile_storage.get_device_addresses(mobile_id)
        for address in addresses:
            address_data = self.txs_storage.get_mobile_transactions(address)
            for data in address_data:
                transactions_data.append(data)
        if transactions_data:
            for data in transactions_data:
                tx_dict = {
                    "type": data[0],
                    "category": data[1],
                    "address": data[2],
                    "txid": data[3],
                    "amount": data[4],
                    "blocks": data[5],
                    "fee": data[6],
                    "timestamp": data[7]
                }
                result.append(tx_dict)
            encrypted_data = encrypt_data(mobile_id, self.mobile_storage, self.units, json.dumps(result))
        return jsonify({"data": encrypted_data}), 200
    

    async def handle_cashout(self):
        mobile_ids = self.mobile_storage.get_auth_ids()
        valid, response = verify_signature(mobile_ids, self.mobile_storage, self.units)
        if not valid:
            return response
        self.update_device_status()
        mobile_id = request.headers.get('Authorization')

        encrypted_data = request.args.get("data")
        decrypted_json = decrypt_data(mobile_id, self.mobile_storage, self.units, encrypted_data)
        get_params = json.loads(decrypted_json)

        required_params = ["type", "address", "amount", "fee"]
        missing = [p for p in required_params if not get_params.get(p)]
        if missing:
            return jsonify({"error": f"Missing required parameters: {', '.join(missing)}"}), 400
        
        
        tx_type = get_params.get("type")
        address = get_params.get("address")
        amount = float(get_params.get("amount"))
        txfee = float(get_params.get("fee"))

        is_valid = await self.is_valid(address)
        if not is_valid:
            return jsonify({"error": "Invalid destination address"}), 400

        taddress, zaddress = self.mobile_storage.get_device_addresses(mobile_id)
        if tx_type == "transparent":
            balance = self.addresses_storage.get_address_balance(taddress)
            from_address = taddress
        else:
            balance = self.addresses_storage.get_address_balance(zaddress)
            from_address = zaddress

        if balance < amount + txfee:
            return jsonify({"error": "Insufficient balance"}), 400
        
        amount_str = f"{amount:.8f}"
        txfee_str = f"{txfee:.8f}"
        
        return await self.send_single(from_address, address, amount_str, txfee_str)
        

    async def send_single(self, from_address, address, amount, txfee):
        operation, _= await self.commands.z_sendMany(from_address, address, amount, txfee)
        if not operation:
            return jsonify({"error": "Unable to create operation. Please try again later."}), 500
        transaction_status, _= await self.commands.z_getOperationStatus(operation)
        transaction_status = json.loads(transaction_status)
        if isinstance(transaction_status, list) and transaction_status:
            status = transaction_status[0].get('status')
            if status not in ["executing", "success"]:
                return jsonify({"error": f"Operation could not start. Status: {status}"}), 500
            await asyncio.sleep(1)
            while True:
                transaction_result, _= await self.commands.z_getOperationResult(operation)
                transaction_result = json.loads(transaction_result)
                if isinstance(transaction_result, list) and transaction_result:
                    status = transaction_result[0].get('status')
                    result = transaction_result[0].get('result', {})
                    txid = result.get('txid')
                    if status == "failed":
                        return jsonify({"error": "Transaction send failed"}), 500
                    elif status == "success":
                        category = "send"
                        if from_address.startswith('z'):
                            tx_type = "shielded"
                            blocks = self.main.home_page.current_blocks
                        elif from_address.startswith("t"):
                            tx_type = "transparent"
                            blocks = 0
                        amount = float(amount)
                        self.store_shielded_transaction(tx_type, category, from_address, txid, -amount, blocks, txfee)
                        return jsonify({"result": "success"}), 200
                                
                await asyncio.sleep(3)
        

    def store_shielded_transaction(self, tx_type, category, from_address, txid, amount, blocks, txfee):
        timesent = int(datetime.now().timestamp())
        self.txs_storage.insert_transaction(tx_type, category, from_address, txid, amount, blocks, txfee, timesent)


    
    async def is_valid(self, address):
        if address.startswith("t"):
            result, _ = await self.commands.validateAddress(address)
        elif address.startswith("z"):
            result, _ = await self.commands.z_validateAddress(address)
        else:
            return None
        if result is not None:
            result = json.loads(result)
            is_valid = result.get('isvalid')
            if is_valid is True:
                return True
            return None


    def update_device_status(self):
        mobile_id = request.headers.get('Authorization')
        timestamp = int(datetime.now(timezone.utc).timestamp())
        self.mobile_storage.update_device_connected(mobile_id, timestamp)
        self.mobile_storage.update_device_status(mobile_id, "on")
        
    
    def start(self):
        event = Event()
        self.server_thread = ServerThread(self.app, self.flask, self.host, self.port, event)
        self.server_thread.start()
        if event.wait(timeout=5):
            self.app.console.server_log(f"📱: Server started and listening to {self.host}:{self.port}")
            self.server_status = True
            return True
        else:
            self.app.console.error_log("Server failed to start within the timeout period.")
            return None

    def stop(self):
        self.app.console.warning_log("📱: Shutdown server")
        self.server_status = None
        self.server_thread.shutdown()