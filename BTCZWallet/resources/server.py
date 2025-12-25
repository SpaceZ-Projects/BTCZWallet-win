
import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
import hmac
import hashlib
from threading import Thread, Event
from flask import Flask, request, jsonify, stream_with_context, Response
from werkzeug.serving import make_server
import socket
from threading import Lock
from collections import deque

from toga import App
from ..framework import Sys


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



class SSEBroker:
    def __init__(self):
        self.listeners = {}
        self.lock = Lock()

    def listen(self, mobile_id):
        q = deque()
        with self.lock:
            self.listeners[mobile_id] = q
        return q

    def push(self, action: str):
        with self.lock:
            for q in self.listeners.values():
                q.append(action)

    def remove(self, mobile_id):
        with self.lock:
            self.listeners.pop(mobile_id, None)

    def connected_count(self) -> int:
        with self.lock:
            return len(self.listeners)


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
        messages_storage = None,
        settings = None,
        units = None,
        rpc = None,
        notify = None
    ):
        self.host = host
        self.port = port
        self.mobile_storage = mobile_storage
        self.txs_storage = txs_storage
        self.addresses_storage = addresses_storage
        self.messages_storage = messages_storage
        self.settings = settings
        self.units = units
        self.rpc = rpc
        self.notify = notify

        self.app = app
        self.main = main
        self.server_status = None
        self.current_blocks = None
        self.read_messages = []
        self.unread_messages = []
        self.processed_timestamps = set()
        
        self.flask = Flask(__name__)
        Sys.Environment.SetEnvironmentVariable(
            'FLASK_ENV', 'production', Sys.EnvironmentVariableTarget.Process
        )

        self.broker = SSEBroker()

        self.add_rules()

    def add_rules(self):
        self.flask.add_url_rule("/stream", "stream", self.stream)
        self.flask.add_url_rule('/status', 'status', self.handle_status)
        self.flask.add_url_rule('/addresses', 'addresses', self.handle_addresses)
        self.flask.add_url_rule('/book', 'book', self.handle_book)
        self.flask.add_url_rule('/balance', 'balance', self.handle_balance)
        self.flask.add_url_rule('/balances', 'balances', self.handle_balances)
        self.flask.add_url_rule('/mining', 'mining', self.handle_mining)
        self.flask.add_url_rule('/transactions', 'transactions', self.handle_transactions)
        self.flask.add_url_rule('/cashout', 'cashout', self.handle_cashout)
        self.flask.add_url_rule('/contacts', 'contacts', self.handle_contacts)
        self.flask.add_url_rule('/messages', 'messages', self.handle_messages)
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


    def stream(self):
        mobile_ids = self.mobile_storage.get_auth_ids()
        valid, response = verify_signature(mobile_ids, self.mobile_storage)
        if not valid:
            return response
        self.update_device_status()
        mobile_id = request.headers.get('Authorization')
        q = self.broker.listen(mobile_id)
        def event_stream():
            try:
                last_ping = time.time()
                while True:
                    if q:
                        action = q.popleft()
                        yield f"data: {action}\n\n"
                    else:
                        now = time.time()
                        if now - last_ping >= 15:
                            yield ": ping\n\n"
                            last_ping = now
                        time.sleep(0.1)
            finally:
                self.broker.remove(mobile_id)
        return Response(
            stream_with_context(event_stream()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
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
            self.broker.push("update_book")
            return jsonify({"result": "success"}), 200
    

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
            return jsonify({"data": encrypted_data}), 200

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
        
        return await self.make_tx(from_address, address, amount_str, txfee_str, mobile_id=mobile_id)
    

    async def handle_contacts(self):
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
            option = params.get('get')

            if option == "identity":
                identity = self.messages_storage.get_identity()
                if identity:
                    address = identity[2]
                    result = {"address": address}
                else:
                    return jsonify({"error": "Identity not found"}), 404

            elif option == "contacts":
                contacts = self.messages_storage.get_contacts()
                for data in contacts:
                    contact_dict = {
                        "category": data[0],
                        "contact_id": data[2],
                        "username": data[3]
                    }
                    result.append(contact_dict)

            elif option == "pending":
                pending = self.messages_storage.get_pending()
                for data in pending:
                    pending_dict = {
                        "category": data[0],
                        "contact_id": data[1],
                        "username": data[2]
                    }
                    result.append(pending_dict)
                    
            encrypted_data = encrypt_data(mobile_id, self.mobile_storage, self.units, json.dumps(result))
            return jsonify({"data": encrypted_data}), 200
        
        elif "request" in params:
            address = params.get('request')

            is_valid = await self.is_valid(address, True)
            if not is_valid:
                return jsonify({"error": "Invalid shielded address"}), 400
            contacts = self.messages_storage.get_contacts("address")
            if address in contacts:
                return jsonify({"error": "This address is already in your contacts list"}), 400
            pending = self.messages_storage.get_pending()
            if address in pending:
                return jsonify({"error": "This address is already in your pending list"}), 400
            requests = self.messages_storage.get_requests()
            if address in requests:
                return jsonify({"error": "This address is already in your requests list"}), 400
            banned = self.messages_storage.get_banned()
            if address in banned:
                return jsonify({"error": "This address has been banned"}), 400
            
            amount = 0.0001
            txfee = 0.0001
            id = self.units.generate_id()
            category, username, from_address = self.messages_storage.get_identity()
            memo = {"type":"request","category":category,"id":id,"username":username,"address":from_address}
            memo_str = json.dumps(memo)

            return await self.make_tx(from_address, address, amount, txfee, memo_str, id, "request")
        
        elif "accept" in params:
            pending_id = params.get('accpet')
            data = self.messages_storage.get_pending_single(pending_id)
            if not data:
                return jsonify({"error": "Pending not found"}), 400

            amount = 0.0001
            txfee = 0.0001
            id = self.units.generate_id()
            category, username, from_address = self.messages_storage.get_identity()
            memo = {"type":"identity","category":category,"id":id,"username":username,"address":from_address}
            memo_str = json.dumps(memo)

            return await self.make_tx(from_address, data[3], amount, txfee, memo_str, id, "accept", data)
        
        elif "reject" in params:
            reject_id = params.get('reject')
            address = self.messages_storage.get_pending_address(reject_id)
            if not address:
                return jsonify({"error": "Pending not found"}), 400
            
            self.messages_storage.ban(address[0])
            self.messages_storage.delete_pending(address[0])

            return jsonify({"result": "success"}), 200
        
        elif "ban" in params:
            ban_id = params.get('ban')
            address = self.messages_storage.get_contact_address(ban_id)
            banned = self.messages_storage.get_banned()
            if address[0] in banned:
                return jsonify({"error": "Contact already banned"})
            
            self.messages_storage.ban(address[0])
            self.messages_storage.delete_contact(address[0])

            return jsonify({"result": "success"}), 200
        

    async def handle_messages(self):
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
            option = params.get('get')
            if option == "read":
                messages = self.messages_storage.get_messages()
                for data in messages:
                    timestamp = data[4]
                    if timestamp not in self.read_messages:
                        self.read_messages.append(timestamp)
                        self.processed_timestamps.add(timestamp)
                        message_dict = {
                            "id": data[0],
                            "author": data[1],
                            "message": data[2],
                            "amount": data[3],
                            "timestamp": data[4]
                        }
                        result.append(message_dict)

            elif option == "unread":
                unread_messages = self.messages_storage.get_unread_messages()
                for data in unread_messages:
                    timestamp = data[4]
                    if timestamp not in self.unread_messages:
                        self.unread_messages.append(timestamp)
                        self.processed_timestamps.add(timestamp)
                        unread_message_dict = {
                            "id": data[0],
                            "author": data[1],
                            "message": data[2],
                            "amount": data[3],
                            "timestamp": data[4]
                        }
                        result.append(unread_message_dict)

            encrypted_data = encrypt_data(mobile_id, self.mobile_storage, self.units, json.dumps(result))
            return jsonify({"data": encrypted_data}), 200

        elif "clean" in params:
            clean_id = params.get('clean')
            unread_messages = self.messages_storage.get_unread_messages(clean_id)
            if unread_messages:
                for data in unread_messages:
                    author = data[0]
                    text = data[1]
                    amount = data[2]
                    timestamp = data[3]
                    edited = data[4]
                    replied = data[5]
                    self.messages_storage.message(clean_id, author, text, amount, timestamp, edited, replied)
                self.messages_storage.delete_unread(clean_id)
            return jsonify({"result": "success"}), 200
        
        elif "send" in params:
            contact_id = params.get('send')
            message = params.get('message')
            fee = params.get('amount')

            amount = float(fee) - 0.0001
            txfee = 0.0001
            user = self.messages_storage.get_contact(contact_id)
            _, username, from_address = self.messages_storage.get_identity()
            timestamp = await self.get_message_timestamp()
            if timestamp is not None:
                data = ["you", message, timestamp]
                memo = {"type":"message","id":user[1],"username":username,"text":message, "timestamp":timestamp}
                memo_str = json.dumps(memo)

                return await self.make_tx(from_address, user[4], amount, txfee, memo_str, contact_id, "message", data)
            return jsonify({"error", "Failed to get timestamp"})
    

    async def handle_balance(self):
        mobile_ids = self.mobile_storage.get_auth_ids()
        valid, response = verify_signature(mobile_ids, self.mobile_storage, self.units)
        if not valid:
            return response
        self.update_device_status()
        mobile_id = request.headers.get('Authorization')

        encrypted_data = request.args.get("data")
        decrypted_json = decrypt_data(mobile_id, self.mobile_storage, self.units, encrypted_data)
        params = json.loads(decrypted_json)
        if "address" in params:
            address = params.get('address')
            balance,_ = await self.rpc.z_getBalance(address)
            if balance:
                result = {"balance": balance}
                encrypted_data = encrypt_data(mobile_id, self.mobile_storage, self.units, json.dumps(result))
                return jsonify({"data": encrypted_data}), 200
    
    
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
        

    async def make_tx(self, from_address, address, amount, txfee, memo = None, id=None, option = None, data = None, mobile_id = None):
        if memo and id:
            operation,_ = await self.rpc.SendMemo(from_address, address, amount, txfee, memo)
        else:
            operation, _= await self.rpc.z_sendMany(from_address, address, amount, txfee)
        if not operation:
            return jsonify({"error": "Unable to create operation. Please try again later."}), 500
        transaction_status, _= await self.rpc.z_getOperationStatus(operation)
        if isinstance(transaction_status, list) and transaction_status:
            status = transaction_status[0].get('status')
            if status not in ["executing", "success"]:
                return jsonify({"error": f"Operation could not start. Status: {status}"}), 500
            await asyncio.sleep(1)
            while True:
                transaction_result, _= await self.rpc.z_getOperationResult(operation)
                if isinstance(transaction_result, list) and transaction_result:
                    status = transaction_result[0].get('status')
                    result = transaction_result[0].get('result', {})
                    txid = result.get('txid')
                    if status == "failed":
                        return jsonify({"error": "Transaction failed"}), 500
                    elif status == "success":
                        if not option:
                            category = "send"
                            if from_address.startswith('z'):
                                tx_type = "shielded"
                                blocks = self.main.home_page.current_blocks
                            elif from_address.startswith("t"):
                                tx_type = "transparent"
                                blocks = 0
                            amount = float(amount)
                            self.store_transaction(tx_type, category, from_address, txid, -amount, blocks, txfee)
                            self.broker.push("update_transactions")
                        else:
                            if option == "request":
                                self.messages_storage.tx(txid)
                                self.messages_storage.add_request(id, address)

                            elif option == "accept":
                                category = data[0]
                                contact_id = data[1]
                                username = data[2]
                                address = data[3]
                                self.messages_storage.tx(txid)
                                self.messages_storage.delete_pending(address)
                                self.messages_storage.add_contact(category, id, contact_id, username, address)

                            elif option == "message":
                                author = data[0]
                                message = data[1]
                                timestamp = data[2]
                                self.messages_storage.message(id, author, message, amount, timestamp)
                            self.broker.push("update_messages")

                        return jsonify({"result": "success"}), 200
                                
                await asyncio.sleep(3)
        

    def store_transaction(self, tx_type, category, from_address, txid, amount, blocks, txfee):
        timesent = int(datetime.now().timestamp())
        self.txs_storage.insert_transaction(tx_type, category, from_address, txid, amount, blocks, txfee, timesent)

    
    async def is_valid(self, address, z_only=False):
        if z_only:
            if not address.startswith("z"):
                return None
            result, _ = await self.rpc.z_validateAddress(address)
        else:
            if address.startswith("t"):
                result, _ = await self.rpc.validateAddress(address)
            elif address.startswith("z"):
                result, _ = await self.rpc.z_validateAddress(address)
            else:
                return None
        if result is not None:
            if result.get('isvalid') is True:
                return True
        return None
    

    async def get_message_timestamp(self):
        blockchaininfo, _ = await self.rpc.getBlockchainInfo()
        if blockchaininfo is not None:
            timestamp = blockchaininfo.get('mediantime')
            if timestamp in self.processed_timestamps:
                highest_timestamp = max(self.processed_timestamps)
                timestamp = highest_timestamp + 1
            self.processed_timestamps.add(timestamp)
            return timestamp


    def update_device_status(self):
        mobile_id = request.headers.get('Authorization')
        timestamp = int(datetime.now(timezone.utc).timestamp())
        self.mobile_storage.update_device_connected(mobile_id, timestamp)
        
    
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
        self.read_messages.clear()
        self.unread_messages.clear()
        self.processed_timestamps.clear()
        self.app.console.warning_log("📱: Shutdown server")
        self.server_status = None
        self.server_thread.shutdown()