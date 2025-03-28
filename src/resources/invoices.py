
import asyncio
import webbrowser
from datetime import datetime
import json

from toga import (
    Window, Box, Button, Label, ScrollContainer,
    TextInput, ImageView, App, Selection
)
from ..framework import (
    FlatStyle, Color, DockStyle, Forms, Command,
    ClipBoard, Os, Drawing, Relation, AlignContent,
    Sys
)

from toga.style.pack import Pack
from toga.colors import (
    rgb, GRAY, BLACK, GREENYELLOW, WHITE, RED
)
from toga.constants import COLUMN, CENTER, BOLD, ROW

from .client import Client
from .utils import Utils
from .storage import StorageInvoices



class InvoiceInfo(Window):
    def __init__(self):
        super().__init__()

        hours, remainder = divmod(expired_in, 3600)
        minutes, seconds = divmod(remainder, 60)
        text = f"Expired in {hours:02}:{minutes:02}:{seconds:02}"
        self.invoice_expired.text = text



class NewInvoice(Window):
    def __init__(self):
        super().__init__(
            size=(650,440),
            resizable=False,
            minimizable=False,
            closable=False
        )

        self.utils = Utils(self.app)

        self.title = "New Invoice"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self.valid_currencies = self.get_currencies_list()

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.currency_label = Label(
            text="Currency :",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1
            )
        )

        self.currencies_selection = Selection(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12
            ),
            items=[
                {"currency": ""}
            ],
            accessor="currency"
        )
        self.currencies_selection._impl.native.DropDownHeight = 150

        self.currency_label_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )
        self.currencies_selection_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )

        self.expect_label = Label(
            text="Expect Amount :",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1
            )
        )

        self.expect_input = TextInput(
            placeholder=" required",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                width = 100
            )
        )

        self.expect_label_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )
        self.expect_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )

        self.seller_label = Label(
            text="Seller Address :",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1
            )
        )

        self.seller_input = TextInput(
            placeholder=" required",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                width = 250
            )
        )

        self.seller_label_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )
        self.seller_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )

        self.duration_label = Label(
            text="Duration (s) :",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1
            )
        )

        self.duration_input = TextInput(
            placeholder=" default 3600",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                width = 150
            )
        )

        self.duration_label_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )
        self.duration_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )

        self.mail_label = Label(
            text="Mail Address :",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1
            )
        )

        self.mail_input = TextInput(
            placeholder="",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                width = 250
            )
        )

        self.mail_label_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )
        self.mail_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )

        self.success_label = Label(
            text="Success URL :",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1
            )
        )

        self.success_input = TextInput(
            placeholder=" optional",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                width = 250
            )
        )

        self.success_label_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )
        self.success_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )

        self.error_label = Label(
            text="Error URL :",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1
            )
        )

        self.error_input = TextInput(
            placeholder=" optional",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                width = 250
            )
        )

        self.error_label_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )
        self.error_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                height = 50
            )
        )

        self.labels_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                flex = 1,
                padding = 1
            )
        )
        self.inputs_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                flex = 1
            )
        )

        self.options_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                flex = 1,
                alignment = CENTER,
                padding = 10
            )
        )

        self.close_button = Button(
            text="Close",
            style=Pack(
                color = RED,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_new_invoice_window
        )
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

        self.confirm_button = Button(
            text="Confirm",
            style=Pack(
                color = GRAY,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (0,0,10,20),
                width = 100
            )
        )
        self.confirm_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.confirm_button._impl.native.MouseEnter += self.confirm_button_mouse_enter
        self.confirm_button._impl.native.MouseLeave += self.confirm_button_mouse_leave

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER,
                background_color = rgb(30,33,36)
            )
        )
        self.currencies_selection.items.clear()
        for currency in self.valid_currencies:
            self.currencies_selection.items.append(currency)

        self.content = self.main_box
        self.main_box.add(
            self.options_box,
            self.buttons_box
        )
        self.options_box.add(
            self.labels_box,
            self.inputs_box
        )
        self.labels_box.add(
            self.currency_label_box,
            self.expect_label_box,
            self.seller_label_box,
            self.duration_label_box,
            self.mail_label_box,
            self.success_label_box,
            self.error_label_box
        )
        self.inputs_box.add(
            self.currencies_selection_box,
            self.expect_input_box,
            self.seller_input_box,
            self.duration_input_box,
            self.mail_input_box,
            self.success_input_box,
            self.error_input_box
        )
        self.currency_label_box.add(
            self.currency_label
        )
        self.currencies_selection_box.add(
            self.currencies_selection
        )
        self.expect_label_box.add(
            self.expect_label
        )
        self.expect_input_box.add(
            self.expect_input
        )
        self.seller_label_box.add(
            self.seller_label
        )
        self.seller_input_box.add(
            self.seller_input
        )
        self.duration_label_box.add(
            self.duration_label
        )
        self.duration_input_box.add(
            self.duration_input
        )
        self.mail_label_box.add(
            self.mail_label
        )
        self.mail_input_box.add(
            self.mail_input
        )
        self.success_label_box.add(
            self.success_label
        )
        self.success_input_box.add(
            self.success_input
        )
        self.error_label_box.add(
            self.error_label
        )
        self.error_input_box.add(
            self.error_input
        )
        self.buttons_box.add(
            self.close_button,
            self.confirm_button
        )


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


    def confirm_button_mouse_enter(self, sender, event):
        self.confirm_button.style.color = BLACK
        self.confirm_button.style.background_color = GREENYELLOW

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.style.color = GRAY
        self.confirm_button.style.background_color = rgb(30,33,36)


    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)


    def close_new_invoice_window(self, button):
        self.close()


class Host(Window):
    def __init__(self, invoices:Window, server):
        super().__init__(
            size=(350,150),
            resizable=False,
            minimizable=False,
            closable=False
        )

        self.utils = Utils(self.app)

        self.title = "Host Setup"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self.invoices = invoices
        self.server = server

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.host_input = TextInput(
            placeholder=" Host",
            style=Pack(
                font_size = 12,
                font_weight = BOLD,
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )
        self.port_input = TextInput(
            placeholder=" Port",
            style=Pack(
                font_size = 12,
                font_weight = BOLD,
                color = WHITE,
                background_color = rgb(30,33,36)
            )
        )

        self.inputs_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (0,5,0,5)
            )
        )

        self.close_button = Button(
            text="Close",
            style=Pack(
                color = RED,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_host_window
        )
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

        self.start_button = Button(
            text="Start",
            style=Pack(
                color = GRAY,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (0,0,10,20),
                width = 100
            ),
            on_press=self.verify_host
        )
        self.start_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.start_button._impl.native.MouseEnter += self.start_button_mouse_enter
        self.start_button._impl.native.MouseLeave += self.start_button_mouse_leave

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER,
                background_color = rgb(30,33,36)
            )
        )
        self.content = self.main_box

        self.content = self.main_box
        self.main_box.add(
            self.inputs_box,
            self.buttons_box
        )
        self.inputs_box.add(
            self.host_input,
            self.port_input
        )
        self.buttons_box.add(
            self.close_button,
            self.start_button
        )

    def verify_host(self, button):
        def on_result(widget, result):
            if result is None:
                self.invoices.update_host_button("start")
                self.close()
        host = self.host_input.value
        port = self.port_input.value
        if not host:
            return
        if not port:
            return
        self.server.host = host
        self.server.port = port
        result = self.server.start()
        if result is True:
            self.info_dialog(
                title="Success",
                message=f"Server started successfully, and listening to {host}:{port}",
                on_result=on_result
            )


    def start_button_mouse_enter(self, sender, event):
        self.start_button.style.color = BLACK
        self.start_button.style.background_color = GREENYELLOW

    def start_button_mouse_leave(self, sender, event):
        self.start_button.style.color = GRAY
        self.start_button.style.background_color = rgb(30,33,36)


    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)


    def close_host_window(self, button):
        self.close()



class Invoice(Box):
    def __init__(
        self, invoices:Window, app:App,
        payment_id, address, seller, currency,
        amount, expect, message, mail,
        success, error, created, expired, paid, status
    ):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 50,
                alignment = CENTER
            )
        )

        self.app = app
        self.invoices = invoices
        self.storage = StorageInvoices(self.app)
        self.clipboard = ClipBoard()

        self.payment_id = payment_id
        self.address = address
        self.seller = seller
        self.expect = expect
        self.message = message
        self.mail = mail
        self.success = success
        self.error = error
        self.created = created
        self.expired = expired
        self.paid = paid
        self.status = status

        self.invoice_icon = ImageView(
            image="images/invoice.png",
            style=Pack(
                background_color = rgb(40,43,48),
                padding = 8
            )
        )

        self.invoice_id = Label(
            text=self.payment_id,
            style=Pack(
                color = WHITE,
                font_weight = BOLD,
                background_color = rgb(40,43,48),
                flex = 2
            )
        )

        self.invoice_paid = Label(
            text=f"{int(self.paid)}",
            style=Pack(
                color = WHITE,
                font_weight = BOLD,
                background_color = rgb(40,43,48),
            )
        )

        self.invoice_expect = Label(
            text=f"| {int(self.expect)} BTCZ",
            style=Pack(
                color = WHITE,
                font_weight = BOLD,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )

        self.invoice_expired = Label(
            text="Pending",
            style=Pack(
                color = WHITE,
                font_weight = BOLD,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )

        self.view_button = Button(
            text="View",
            style=Pack(
                color = GRAY,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                width = 100,
                padding = (2,10,0,0)
            ),
            on_press=self.view_invoice
        )
        self.view_button._impl.native.FlatStyle = FlatStyle.FLAT

        self.add(
            self.invoice_icon,
            self.invoice_id,
            self.invoice_paid,
            self.invoice_expect,
            self.invoice_expired,
            self.view_button
        )
        self.insert_invoice_menustrip()
        self.app.add_background_task(self.updating_invoice)


    def insert_invoice_menustrip(self):
        context_menu = Forms.ContextMenuStrip()
        self.copy_id_cmd = Command(
            title="Copy id",
            icon="images/copy_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.copy_id_cmd_mouse_enter,
            mouse_leave=self.copy_id_cmd_mouse_leave,
            action=self.copy_invoice_id
        )
        commands = [
            self.copy_id_cmd,
        ]
        for command in commands:
            context_menu.Items.Add(command)
        self._impl.native.ContextMenuStrip = context_menu
        self.invoice_icon._impl.native.ContextMenuStrip = context_menu
        self.invoice_id._impl.native.ContextMenuStrip = context_menu


    async def updating_invoice(self, widget):
        while True:
            invoice_data = self.storage.get_invoice(self.payment_id)
            if invoice_data:
                expect = invoice_data[5]
                paid = invoice_data[12]
                status = invoice_data[13]
                if status == 2:
                    self.invoice_expired.style.color = RED
                    self.invoice_expired.text = "Expired"
                    return
                elif status == 5:
                    self.invoice_expired.style.color = GREENYELLOW
                    self.invoice_expired.text = "Completed"
                    return
                if paid >= expect:
                    self.storage.update_status(self.payment_id, 5)
                    self.invoice_paid.text = f"{int(paid)}"
                    self.invoice_expired.style.color = GREENYELLOW
                    self.invoice_expired.text = "Completed"
                    return
                expired_in = self.get_expired_date()
                if expired_in <= 0:
                    self.storage.update_status(self.payment_id, 2)
                    self.invoice_expired.style.color = RED
                    self.invoice_expired.text = "Expired"
                    return
                if paid != self.paid:
                    self.invoice_paid.text = f"{int(paid)}"

            await asyncio.sleep(1)


    async def view_invoice(self, button):
        if not self.invoices.server.server_status:
            return
        host = self.invoices.server.host
        port = self.invoices.server.port
        url = f"http://{host}:{port}/invoice/{self.payment_id}"
        webbrowser.open(url)


    def copy_invoice_id(self):
        self.clipboard.copy(self.payment_id)
        self.invoices.info_dialog(
            title="Copied",
            message="The invoice id has copied to clipboard.",
        )


    def get_expired_date(self):
        current_time = int(datetime.now().timestamp())
        remaining_seconds = self.expired - current_time
        return remaining_seconds
    
    def copy_id_cmd_mouse_enter(self):
        self.copy_id_cmd.icon = "images/copy_a.ico"
        self.copy_id_cmd.color = Color.BLACK

    def copy_id_cmd_mouse_leave(self):
        self.copy_id_cmd.icon = "images/copy_i.ico"
        self.copy_id_cmd.color = Color.WHITE



class Invoices(Window):
    def __init__(self, main:Window, server):
        super().__init__()

        self.title = "Invoices"
        self.size = (900,607)
        self._impl.native.BackColor = Color.rgb(30,33,36)
        
        self.server = server
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.storage = StorageInvoices(self.app)

        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self.on_close = self.on_close_invoices
        self._impl.native.Resize += self._handle_on_resize

        self.main = main

        self.no_invoices_toggle = None
        self.invoices_data = []

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.no_invoices = Label(
            text="No invoices found !",
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 14,
                padding_top = 40,
                background_color = rgb(30,33,36)
            )
        )

        self.invoices_list = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.invoices_scroll = ScrollContainer(
            style=Pack(
                background_color = rgb(30,33,36),
                flex = 1
            ),
            content=self.invoices_list
        )

        self.create_invoice = Button(
            text="New Invoice",
            style=Pack(
                color = GRAY,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                width = 150,
                padding = (10,10,0,10)
            ),
            on_press=self.create_new_invoice
        )
        new_i_icon = self.invoices_icon("images/new_invoice_i.png")
        self.create_invoice._impl.native.Image = Drawing.Image.FromFile(new_i_icon)
        self.create_invoice._impl.native.FlatStyle = FlatStyle.FLAT
        self.create_invoice._impl.native.TextImageRelation = Relation.IMAGEBEFORETEXT
        self.create_invoice._impl.native.ImageAlign = AlignContent.RIGHT
        self.create_invoice._impl.native.MouseEnter += self.create_invoice_mouse_enter
        self.create_invoice._impl.native.MouseLeave += self.create_invoice_mouse_leave

        self.search_invoice = TextInput(
            placeholder=" Invoice ID",
            style=Pack(
                font_size = 12,
                font_weight = BOLD,
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 1,
                padding =(10,10,0,0)
            )
        )

        self.host_server = Button(
            text="",
            style=Pack(
                color = GRAY,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                width = 100,
                padding =(10,10,0,0)
            )
        )
        self.host_server._impl.native.FlatStyle = FlatStyle.FLAT

        self.help_button = Button(
            text="Help",
            style=Pack(
                color = GRAY,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                width = 100,
                padding =(10,10,0,0)
            ),
            on_press=self.open_help_page
        )
        self.help_button._impl.native.FlatStyle = FlatStyle.FLAT

        self.menu_box = Box(
            style=Pack(
                direction = ROW,
                height = 50,
                background_color = rgb(60,63,68),
                alignment = CENTER,
                padding_bottom = 10
            )
        )
        self.menu_box._impl.native.Dock = DockStyle.TOP

        self.content = self.main_box

        self.main_box.add(
            self.menu_box
        )
        self.menu_box.add(
            self.create_invoice,
            self.search_invoice,
            self.host_server
        )
        self.app.add_background_task(self.listen_to_invoices)


    def load_invoices(self):
        data = self.storage.is_exists()
        if data:
            self.load_invoices_list()
        else:
            self.no_invoices_found()
        if self.server.server_status:
            self.host_server.text = "Stop"
            self.host_server._impl.native.MouseEnter += self.stop_server_mouse_enter
            self.host_server._impl.native.MouseLeave += self.stop_server_mouse_leave
            self.host_server.on_press = self.stop_invoices_server
            self.menu_box.add(self.help_button)
        else:
            self.host_server.text = "Host"
            self.host_server._impl.native.MouseEnter += self.host_server_mouse_enter
            self.host_server._impl.native.MouseLeave += self.host_server_mouse_leave
            self.host_server.on_press = self.start_invoices_server


    def load_invoices_list(self):
        invoices = self.storage.get_invoices()
        if invoices:
            for invoice in invoices:
                (
                    id, address, seller, currency, amount, expect, message,
                    mail, success, error, created, expired, paid, status
                ) = invoice
                invoice_info = Invoice(
                    self, self.app, id, address, seller, currency, amount, expect,
                    message, mail, success, error, created, expired, paid, status
                )
                self.invoices_list.insert(0, invoice_info)
                self.invoices_data.append(id)
        self.main_box.add(self.invoices_scroll)
        self.app.add_background_task(self.updating_invoices_list)
        

    async def updating_invoices_list(self, widget):
        while True:
            invoices = self.storage.get_invoices()
            for invoice in invoices:
                (
                    id, address, seller, currency, amount, expect, message,
                    mail, success, error, created, expired, paid, status
                ) = invoice
                if id not in self.invoices_data:
                    if self.no_invoices_toggle:
                        self.main_box.remove(self.no_invoices)
                        self.main_box.add(self.invoices_scroll)
                        self.no_invoices_toggle = None
                    invoice_info = Invoice(
                        self, self.app, id, address, seller, currency, amount, expect,
                        message, mail, success, error, created, expired, paid, status
                    )
                    self.invoices_list.insert(0, invoice_info)
                    self.invoices_data.append(id)
            
            await asyncio.sleep(3)


    async def listen_to_invoices(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            invoices = self.storage.get_invoices()
            if invoices:
                for invoice in invoices:
                    id = invoice[0]
                    address = invoice[1]
                    paid = invoice[12]
                    status = invoice[13]
                    if status == 1:
                        balance, _= await self.commands.getReceivedByAddress(address, 1)
                        if balance:
                            if float(balance) > paid:
                                self.storage.update_paid(id, float(balance))

            await asyncio.sleep(3)


    async def create_new_invoice(self, button):
        self.new_invoice = NewInvoice()
        self.new_invoice._impl.native.ShowDialog()

    def no_invoices_found(self):
        self.main_box.add(self.no_invoices)
        self.app.add_background_task(self.updating_invoices_list)
        self.no_invoices_toggle = True


    def start_invoices_server(self, button):
        self.host_window = Host(self, self.server)
        self.host_window._impl.native.ShowDialog()


    def stop_invoices_server(self, button):
        self.server.stop()
        self.update_host_button("stop")
        self.server.host = None
        self.server.port = None


    def open_help_page(self, button):
        url = f"http://{self.server.host}:{self.server.port}/api/?method=help"
        webbrowser.open(url)


    def update_host_button(self, option):
        if option == "start":
            self.host_server.text = "Stop"
            self.host_server._impl.native.MouseEnter -= self.host_server_mouse_enter
            self.host_server._impl.native.MouseLeave -= self.host_server_mouse_leave
            self.host_server._impl.native.MouseEnter += self.stop_server_mouse_enter
            self.host_server._impl.native.MouseLeave += self.stop_server_mouse_leave
            self.host_server.on_press = self.stop_invoices_server
            self.menu_box.add(self.help_button)

        elif option == "stop":
            self.host_server.text = "Host"
            self.host_server._impl.native.MouseEnter -= self.stop_server_mouse_enter
            self.host_server._impl.native.MouseLeave -= self.stop_server_mouse_leave
            self.host_server._impl.native.MouseEnter += self.host_server_mouse_enter
            self.host_server._impl.native.MouseLeave += self.host_server_mouse_leave
            self.host_server.on_press = self.start_invoices_server
            self.menu_box.remove(self.help_button)


    def create_invoice_mouse_enter(self, sender, event):
        new_a_icon = self.invoices_icon("images/new_invoice_a.png")
        self.create_invoice._impl.native.Image = Drawing.Image.FromFile(new_a_icon)
        self.create_invoice.style.color = BLACK
        self.create_invoice.style.background_color = GREENYELLOW

    def create_invoice_mouse_leave(self, sender, event):
        new_i_icon = self.invoices_icon("images/new_invoice_i.png")
        self.create_invoice._impl.native.Image = Drawing.Image.FromFile(new_i_icon)
        self.create_invoice.style.color = GRAY
        self.create_invoice.style.background_color = rgb(30,33,36)

    def host_server_mouse_enter(self, sender, event):
        self.host_server.style.color = BLACK
        self.host_server.style.background_color = GREENYELLOW

    def host_server_mouse_leave(self, sender, event):
        self.host_server.style.color = GRAY
        self.host_server.style.background_color = rgb(30,33,36)

    def stop_server_mouse_enter(self, sender, event):
        self.host_server.style.color = BLACK
        self.host_server.style.background_color = RED

    def stop_server_mouse_leave(self, sender, event):
        self.host_server.style.color = GRAY
        self.host_server.style.background_color = rgb(30,33,36)

    def invoices_icon(self, path):
        return Os.Path.Combine(str(self.app.paths.app), path)
    
    def _handle_on_resize(self, sender, event:Sys.EventArgs):
        min_width = 916
        min_height = 646
        self._impl.native.MinimumSize = Drawing.Size(min_width, min_height)

    def on_close_invoices(self, widget):
        self.hide()
        self.main.show()