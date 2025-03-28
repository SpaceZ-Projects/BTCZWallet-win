
import aiohttp
import json
import socket
import uuid
from urllib.parse import quote_plus
from io import BytesIO
from datetime import datetime
from threading import Thread, Event

from flask import (
    Flask, request, jsonify, render_template,
    send_file
)
from werkzeug.serving import make_server
import qrcode

from toga import App
from ..framework import Sys, Os

from .client import Client
from .storage import StorageInvoices


class WebServerThread(Thread):
    def __init__(self, flask, host, port, event):
        Thread.__init__(self)
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


class WebServer():
    def __init__(
        self,
        app:App,
        host:str = None,
        port:int = None,
    ):
        self.host = host
        self.port = port
        self.flask = Flask(__name__)
        Sys.Environment.SetEnvironmentVariable(
            'FLASK_ENV', 'production', Sys.EnvironmentVariableTarget.Process
        )
        self.flask.config["TEMPLATES_AUTO_RELOAD"] = True

        self.app = app
        self.commands = Client(self.app)
        self.storage = StorageInvoices(self.app)

        self.server_status = None
        self.valid_currencies = self.get_currencies_list()

        self.add_rules()

    def add_rules(self):
        self.flask.add_url_rule('/api/', 'api', self.get_method, methods=['GET'])
        self.flask.add_url_rule('/api/request_payment/', 'request_payment', self.request_payment, methods=['GET'])
        self.flask.add_url_rule('/generate_qr/<path:payment_link>', 'generate_qr', self.payment_qr, methods=['GET'])
        self.flask.add_url_rule('/api/check_payment/<invoice_id>', 'check_payment', self.check_payment, methods=['GET'])
        self.flask.add_url_rule('/invoice/<invoice_id>', 'get_invoice', self.get_invoice, methods=['GET'])
        self.flask.before_request(self.log_request)


    def log_request(self):
        print(f"Request Method: {request.method}")
        print(f"Request Path: {request.path}")
                
        if request.method == 'GET':
            if request.args:
                print(f"Request Parameters: {dict(request.args)}")
            else:
                print("No query parameters in GET request.")
                
        elif request.method == 'POST':
            if request.form:
                print(f"Request Form Data: {dict(request.form)}")
            elif request.is_json:
                print(f"Request JSON Body: {request.get_json()}")
            else:
                print("No form data or JSON body found in POST request.")
                
        print("-" * 50)


    def get_method(self):
        method = None
        
        if request.method == 'GET':
            method = request.args.get('method')

        if method == 'help':
            return self.help_menu()
        else:
            return jsonify({"message": "Invalid method parameter."}), 400


    def help_menu(self):
        return render_template(
            'help.html',
            host = self.host,
            port = self.port
        )
    

    async def request_payment(self):
        expect = request.args.get('expect')
        currency = request.args.get('currency')
        seller = request.args.get('seller')

        expired = request.args.get('expired')
        message = request.args.get('message', '')
        customer_mail = request.args.get('customerMail', '')
        cli_success_url = request.args.get('cliSuccessURL', '')
        cli_error_url = request.args.get('cliErrorURL', '')

        if not expect or not currency or not seller:
            return jsonify({"error": "Missing required parameters (expect, currency, seller)."}), 400
        
        if currency not in self.valid_currencies:
            return jsonify({"error": "Invalid currency."}), 400
        
        if seller.startswith("t"):
            result, _ = await self.commands.validateAddress(seller)
        elif seller.startswith("z"):
            result, _ = await self.commands.z_validateAddress(seller)
        else:
            return jsonify({"error": "Address not valid."}), 400
        if result is not None:
            result = json.loads(result)
            is_valid = result.get('isvalid')
            if is_valid is False:
                return jsonify({"error": "Address not valid."}), 400
        else:
            return jsonify({"error": "Address not valid."}), 400
        
        amount = expect
        if currency != "BTCZ":
            btcz_price = await self.fetch_btcz_price(currency)
            if not btcz_price:
                return jsonify({"error": "Error while fetching BTCZ price, try again later."}), 400
            amount_btcz = float(expect) / float(btcz_price)
            expect = int(amount_btcz)

        created = int(datetime.now().timestamp())
        try:
            expired = int(expired) if expired else 3600
        except ValueError:
            return jsonify({"error": "Invalid value for 'expired'. It should be a number."}), 400
        duration = created + expired
        
        payment_id = str(uuid.uuid4())
        payment_address,_ = await self.commands.getNewAddress()
        payment_link = payment_address
        qr_link = f"http://{self.host}:{self.port}/generate_qr/{quote_plus(payment_link)}"
        qr_simple = f"http://{self.host}:{self.port}/generate_qr/bitcoinz:{quote_plus(payment_address[0])}?amount={expect}"

        payment_response = {
            "id": payment_id,
            "address": payment_address,
            "link": payment_link,
            "qr": qr_link,
            "qr_simple": qr_simple
        }
        self.storage.invoice(
            payment_id, payment_address, seller, currency, amount, expect,
            message, customer_mail, cli_success_url, cli_error_url, created, duration, 0, 1
        )

        return jsonify(payment_response)
    
    
    def get_invoice(self, invoice_id):
        invoice_data = self.storage.get_invoice(invoice_id)
        if not invoice_data:
            return jsonify({"error": "Invoice not found."}), 404

        address = invoice_data[1]
        expect = invoice_data[5]
        paid = invoice_data[12]
        qr_link = f"http://{self.host}:{self.port}/generate_qr/{quote_plus(address)}"

        return render_template(
            'invoice.html',
            invoice_id = invoice_id,
            payment_address = address,
            expect_amount = expect,
            paid_amount = paid,
            qr_link = qr_link
        )
    
    def check_payment(self, invoice_id):
        invoice_data = self.storage.get_invoice(invoice_id)
        if not invoice_data:
            return jsonify({"error": "Invoice not found."}), 404
        
        current_timestamp = int(datetime.now().timestamp())
        address = invoice_data[1]
        currency = invoice_data[3]
        amount = invoice_data[4]
        expect = invoice_data[5]
        success = invoice_data[8]
        error = invoice_data[9]
        created = invoice_data[10]
        expired = invoice_data[11]
        paid = invoice_data[12]
        status = invoice_data[13]
        payment_response = {
            "generated": address,
            "btcz_expected": expect,
            "btcz_actual": paid,
            "currency": currency,
            "amount": amount,
            "timestamp_start": created,
            "timestamp_now": current_timestamp,
            "timestamp_stop": expired,
            "state": status
        }
        if status == 1:
            pass
        elif status == 5:
            payment_response["successURL"] = success
        elif status == 2:
            payment_response["errURL"] = error

        return jsonify(payment_response)
    
    
    def payment_qr(self, payment_link):
        qr = qrcode.make(payment_link)
        img_io = BytesIO()
        qr.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    
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
        
    def get_currencies_data(self):
        try:
            currencies_json = Os.Path.Combine(str(self.app.paths.app), 'resources', 'currencies.json')
            with open(currencies_json, 'r') as f:
                currencies_data = json.load(f)
                return currencies_data
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        
        
    def get_currencies_list(self):
        currencies_data = self.get_currencies_data()
        if currencies_data:
            currencies_items = [currency for currency in currencies_data.keys()]
            currencies_items.insert(0,'BTCZ')
            return currencies_items
        
        
    async def fetch_btcz_price(self, currency):
        api = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoinz&vs_currencies={currency.lower()}"
        try:
            async with aiohttp.ClientSession() as session:
                headers={'User-Agent': 'Mozilla/5.0'}
                async with session.get(api, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    btcz_price = data['bitcoinz']
                    price = btcz_price.get(currency.lower())
                    return price
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                return None
        except Exception:
            return None

    def stop(self):
        self.server_status = None
        self.server_thread.shutdown()