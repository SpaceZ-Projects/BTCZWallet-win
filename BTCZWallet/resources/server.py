
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



class MarketServerThread(Thread):
    def __init__(self, flask, host, port, event):
        Thread.__init__(self, daemon=True)
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
            print(f"Server started successfully, and listening to {self.host}:{self.port}")
            self.event.set()
            self.http_server.serve_forever()
        except socket.gaierror as e:
            print(f"Error: DNS resolution failed for host {self.host}. Error: {e}")
        except Exception as e:
            print(f"Error in server thread: {e}")
        finally:
            print("Shutdown complete.")

    def shutdown(self):
        if self.http_server:
            try:
                self.event.clear()
                self.http_server.shutdown()
                self.http_server.server_close()
            except Exception as e:
                print(f"Error while shutting down the server: {e}")


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
        print(f"Request Path: {request.path}")
        if request.method == 'GET':
            if request.form:
                print(f"Request Form Data: {dict(request.form)}")


    def verify_signature(self):
        contact_id = request.headers.get('Authorization')
        timestamp = request.headers.get('X-Timestamp')
        signature = request.headers.get('X-Signature')

        if not contact_id or not timestamp or not signature:
            return False, (jsonify({'error': 'Missing headers'}), 400)

        contacts_ids = self.messages_storage.get_ids_contacts()
        if contact_id not in contacts_ids:
            return False, (jsonify({'error': 'Unauthorized'}), 401)

        try:
            request_time = datetime.fromisoformat(timestamp)
            if request_time.tzinfo is None:
                request_time = request_time.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if abs(now - request_time) > timedelta(seconds=60):
                return False, (jsonify({'error': 'Request expired'}), 403)
        except ValueError:
            return False, (jsonify({'error': 'Invalid timestamp'}), 400)

        try:
            if request.method == 'GET':
                body = request.args.to_dict(flat=True)
            else:
                body = {}

            message = f"{timestamp}.{json.dumps(body, separators=(',', ':'), sort_keys=True)}"
            expected_signature = hmac.new(
                contact_id.encode(),
                message.encode(),
                hashlib.sha512
            ).hexdigest()

            if not hmac.compare_digest(expected_signature, signature):
                return False, (jsonify({'error': 'Invalid signature'}), 403)

        except Exception as e:
            print(f"Signature verification error: {e}")
            return False, (jsonify({'error': 'Signature verification failed'}), 500)

        return True, None


    def handle_status(self):
        valid, response = self.verify_signature()
        if not valid:
            return response
        return jsonify({'status': 'online'}), 200
    

    def handle_items_list(self):
        valid, response = self.verify_signature()
        if not valid:
            return response
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
        return jsonify(result), 200
    

    def handle_item_id(self, item_id):
        valid, response = self.verify_signature()
        if not valid:
            return response
        item = self.market_storage.get_item(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        get_param = request.args.get("get")
        if get_param == "quantity":
            return jsonify({"quantity": item[6]}), 200
        

    def handle_price(self):
        valid, response = self.verify_signature()
        if not valid:
            return response
        btcz_price = self.settings.price()
        return jsonify({"price": btcz_price}), 200
    

    def handle_place_order(self):
        valid, response = self.verify_signature()
        if not valid:
            return response
        
        get_params = request.args
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
        valid, response = self.verify_signature()
        if not valid:
            return response
        contact_id = request.args.get("contact_id")
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
        return jsonify(result), 200
    
    

    def handle_cancel_order(self):
        valid, response = self.verify_signature()
        if not valid:
            return response
        
        get_params = request.args
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
        self.server_thread = MarketServerThread(self.flask, self.host, self.port, event)
        self.server_thread.start()
        if event.wait(timeout=5):
            self.server_status = True
            return True
        else:
            print("Server failed to start within the timeout period.")
            return None

    def stop(self):
        self.server_status = None
        self.server_thread.shutdown()