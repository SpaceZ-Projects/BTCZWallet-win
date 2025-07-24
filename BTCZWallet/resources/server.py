
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


class WebServerThread(Thread):
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
                self.http_server.shutdown()
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
        self.flask.add_url_rule('/item/<string:item_id>', 'item', self.handle_item_id, methods=['GET'])
        self.flask.add_url_rule('/price', 'price', self.handle_price, methods=['GET'])
        self.flask.add_url_rule('/place_order', 'place_order', self.handle_place_order, methods=['GET'])
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
    

    async def handle_place_order(self):
        valid, response = self.verify_signature()
        if not valid:
            return response
        get_params = request.args
        item_id = get_params.get("id")
        contact_id = get_params.get("contact_id")
        total_price = get_params.get("total_price")
        quantity = get_params.get("quantity")
        comment = get_params.get("comment")

        address, _ = await self.commands.getNewAddress()
        if not address:
            return jsonify({"error": "Failed to generate invoice address"}), 400
        
        status = "pending"
        order_id = str(uuid.uuid4())
        created = int(datetime.now().timestamp())
        expired = 3600
        duration = created + expired

        self.market_storage.insert_order(
            order_id, item_id, contact_id, total_price, int(quantity), comment, address, status, created, duration)
        
        item = self.market_storage.get_item(item_id)
        available_items = item[6] - int(quantity)
        self.market_storage.update_item_quantity(item_id, available_items)
        self.notify.send_note(
            title="New Order",
            text=f"Order ID : {order_id}"
        )

        return jsonify({"result": "success"}), 200
    
    
    def start(self):
        event = Event()
        self.server_thread = WebServerThread(self.flask, self.host, self.port, event)
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