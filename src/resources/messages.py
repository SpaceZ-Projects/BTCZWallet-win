
import asyncio
import string
import secrets
import json
import binascii
from datetime import datetime
import webbrowser

from toga import (
    App, Box, Label, Window, TextInput, ImageView,
    ScrollContainer, MultilineTextInput
)
from ..framework import (
    BorderStyle, ToolTip, ClipBoard, Keys,
    RichLabel,FontStyle, Color, DockStyle,
    ScrollBars
)
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD, RIGHT, LEFT, BOTTOM
from toga.colors import rgb, WHITE, GRAY, RED, YELLOW

from .storage import Storage
from .utils import Utils
from .client import Client
from .notify import NotifyRequest, NotifyMessage


class Indentifier(Window):
    def __init__(self, messages:Box, main:Window, chat):
        super().__init__(
            size = (600, 150),
            resizable= False,
            minimizable = False,
            closable=False
        )

        self.main = main
        self.chat = chat

        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.messages_page = messages

        self.title = "Setup Indentity"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )
        self.info_label = Label(
            text="For fist time a username is required for address indentity, you can edit it later",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 11,
                padding_top = 5
            )
        )
        self.username_label = Label(
            text="Username :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_size = 12,
                font_weight = BOLD
            )
        )
        self.username_input = TextInput(
            placeholder="required",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                width = 250
            )
        )
        self.username_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding_top = 15
            )
        )

        self.close_button = ImageView(
            image="images/close_i.png",
            style=Pack(
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                padding_right = 10
            )
        )
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave
        self.close_button._impl.native.Click += self.close_indentity_setup

        self.confirm_button = ImageView(
            image="images/confirm_i.png",
            style=Pack(
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                padding_left = 10
            )
        )
        self.confirm_button._impl.native.MouseEnter += self.confirm_button_mouse_enter
        self.confirm_button._impl.native.MouseLeave += self.confirm_button_mouse_leave
        self.confirm_button._impl.native.Click += self.verify_identity

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER,
                background_color = rgb(30,33,36)
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.username_box,
            self.buttons_box
        )
        self.username_box.add(
            self.username_label,
            self.username_input
        )
        self.buttons_box.add(
            self.close_button,
            self.confirm_button
        )

    def verify_identity(self, sender, event):
        if not self.username_input.value:
            self.error_dialog(
                title="Error",
                message="The username is required for messages address"
            )
            self.username_input.focus()
            return
        self.app.add_background_task(self.setup_new_identity)


    async def setup_new_identity(self, widget):
        category = "individual"
        username = self.username_input.value
        messages_address, _ = await self.commands.z_getNewAddress()
        id = self.generate_id()
        if messages_address:
            prv_key, _= await self.commands.z_ExportKey(messages_address)
            if prv_key:
                self.storage.key(prv_key)
            self.storage.identity(category, id, username, messages_address)
            self.info_dialog(
                title="Identity Setup Complete!",
                message=f"Success! Your new identity has been securely set up with the username:\n\n"
                        f"Username: {username}\nAddress: {messages_address}\n\n"
                        "Your messages address and private key have been stored."
            )
            self.close()
            self.messages_page.clear()
            self.messages_page.add(
                self.chat
            )
            self.chat.run_tasks()

    def generate_id(self, length=32):
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        random_bytes = secrets.token_bytes(length)
        address_id = ''.join(alphabet[b % 62] for b in random_bytes)
        return address_id

    def confirm_button_mouse_enter(self, sender, event):
        self.confirm_button.image = "images/confirm_a.png"

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.image = "images/confirm_i.png"

    def close_button_mouse_enter(self, sender, event):
        self.close_button.image = "images/close_a.png"

    def close_button_mouse_leave(self, sender, event):
        self.close_button.image = "images/close_i.png"
    
    def close_indentity_setup(self, sender, event):
        self.close()



class NewMessenger(Box):
    def __init__(self, messages, main:Window, chat):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )

        self.messages_page = messages
        self.main = main
        self.chat = chat

        self.new_label = Label(
            text="There no messages address for this wallet, click the button to create new messages address",
            style=Pack(
                text_align = CENTER,
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight = BOLD,
                font_size = 12
            )
        )
        self.create_label = Label(
            text="New Messenger",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1,
                padding_top = 7
            )
        )
        self.create_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_top = 10,
                width = 200,
                height = 40
            )
        )
        self.create_button._impl.native.MouseEnter += self.create_button_mouse_enter
        self.create_button._impl.native.MouseLeave += self.create_button_mouse_leave
        self.create_label._impl.native.MouseEnter += self.create_button_mouse_enter
        self.create_label._impl.native.MouseLeave += self.create_button_mouse_leave
        self.create_button._impl.native.Click += self.create_button_click
        self.create_label._impl.native.Click += self.create_button_click

        self.add(
            self.new_label,
            self.create_button
        )
        self.create_button.add(
            self.create_label
        )

    
    def create_button_click(self, sender, event):
        self.indentity = Indentifier(self.messages_page, self.main, self.chat)
        self.indentity._impl.native.ShowDialog()

    
    def create_button_mouse_enter(self, sender, event):
        self.create_label.style.color = WHITE
        self.create_label.style.background_color = rgb(114,137,218)
        self.create_button.style.background_color = rgb(114,137,218)

    def create_button_mouse_leave(self, sender, event):
        self.create_label.style.color = GRAY
        self.create_label.style.background_color = rgb(30,33,36)
        self.create_button.style.background_color = rgb(30,33,36)


class Contact(Box):
    def __init__(self, category, user_id, username, address, app:App, main):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 50
            )
        )
        self._impl.native.MouseEnter += self.contact_mouse_enter
        self._impl.native.MouseLeave += self.contact_mouse_leave

        self.app =app
        self.main = main
        self.storage = Storage(self.app)

        self.category = category
        self.user_id = user_id
        self.username = username
        self.address = address

        if self.category == "individual":
            image_path = "images/individual.png"
        elif self.category == "group":
            image_path = "images/group.png"

        self.category_icon = ImageView(
            image=image_path,
            style=Pack(
                background_color = rgb(40,43,48),
                padding_left = 10
            )
        )
        self.category_icon._impl.native.MouseEnter += self.contact_mouse_enter
        self.category_icon._impl.native.MouseLeave += self.contact_mouse_leave

        self.username_label = Label(
            text=self.username,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                flex = 1,
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                padding_top = 11
            )
        )
        self.username_label._impl.native.MouseEnter += self.contact_mouse_enter
        self.username_label._impl.native.MouseLeave += self.contact_mouse_leave

        self.unread_messages = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = RED,
                text_align = CENTER,
                font_size = 9,
                font_weight = BOLD,
                padding =(15,20,0,0)
            )
        )
        self.unread_messages._impl.native.MouseEnter += self.contact_mouse_enter
        self.unread_messages._impl.native.MouseLeave += self.contact_mouse_leave

        self.add(
            self.category_icon,
            self.username_label,
            self.unread_messages
        )

        self.app.add_background_task(self.update_unread_count)


    async def update_unread_count(self, widget):
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue
            unread_messages = self.storage.get_unread_messages(self.user_id)
            if unread_messages:
                unread_count = len(unread_messages)
                self.unread_messages.text = unread_count
            else:
                self.unread_messages.text = ""
            await asyncio.sleep(3)


    def contact_mouse_enter(self, sender, event):
        self.category_icon.style.background_color = rgb(66,69,73)
        self.username_label.style.background_color = rgb(66,69,73)
        self.style.background_color = rgb(66,69,73)

    def contact_mouse_leave(self, sender, event):
        self.category_icon.style.background_color = rgb(40,43,48)
        self.username_label.style.background_color = rgb(40,43,48)
        self.style.background_color = rgb(40,43,48)


class Pending(Box):
    def __init__(self, category, user_id, username, address, app:App, window:Window, chat:Box):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 50
            )
        )
        self._impl.native.DoubleClick += self.show_pending_info

        self.app = app
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.pending_window = window
        self.chat = chat

        self.category = category
        self.user_id = user_id
        self.username = username
        self.address = address

        if self.category == "individual":
            image_path = "images/individual.png"
        elif self.category == "group":
            image_path = "images/group.png"

        self.category_icon = ImageView(
            image=image_path,
            style=Pack(
                background_color = rgb(40,43,48),
                padding_left = 10
            )
        )
        self.category_icon._impl.native.DoubleClick += self.show_pending_info

        self.username_label = Label(
            text=self.username,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                flex = 1,
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                padding_top = 11
            )
        )
        self.username_label._impl.native.DoubleClick += self.show_pending_info

        self.confirm_button = ImageView(
            image="images/confirm_i.png",
            style=Pack(
                background_color = rgb(40,43,48),
                padding_top = 14
            )
        )
        self.confirm_button._impl.native.MouseEnter += self.confirm_button_mouse_enter
        self.confirm_button._impl.native.MouseLeave += self.confirm_button_mouse_leave
        self.confirm_button._impl.native.Click += self.confirm_button_click

        self.reject_button = ImageView(
            image="images/reject_i.png",
            style=Pack(
                background_color = rgb(40,43,48),
                padding = (14,10,0,10)
            )
        )
        self.reject_button._impl.native.MouseEnter += self.reject_button_mouse_enter
        self.reject_button._impl.native.MouseLeave += self.reject_button_mouse_leave
        self.reject_button._impl.native.Click += self.reject_button_click

        self.add(
            self.category_icon,
            self.username_label,
            self.confirm_button,
            self.reject_button
        )


    def confirm_button_click(self, sender, event):
        self.app.add_background_task(self.send_identity)


    async def send_identity(self, widget):
        destination_address = self.address
        amount = 0.0001
        txfee = 0.0001
        category, id, username, address = self.storage.get_identity()
        memo = {"type":"identity","category":category,"id":id,"username":username,"address":address}
        memo_str = json.dumps(memo)
        self.pending_window._impl.native.Enabled = False
        await self.send_memo(
            address,
            destination_address,
            amount,
            txfee,
            memo_str
        )


    async def send_memo(self, address, toaddress, amount, txfee, memo):
        operation, _= await self.commands.SendMemo(address, toaddress, amount, txfee, memo)
        if operation:
            transaction_status, _= await self.commands.z_getOperationStatus(operation)
            transaction_status = json.loads(transaction_status)
            if isinstance(transaction_status, list) and transaction_status:
                status = transaction_status[0].get('status')
                if status == "executing" or status =="success":
                    await asyncio.sleep(1)
                    while True:
                        transaction_result, _= await self.commands.z_getOperationResult(operation)
                        transaction_result = json.loads(transaction_result)
                        if isinstance(transaction_result, list) and transaction_result:
                            result = transaction_result[0].get('result', {})
                            txid = result.get('txid')
                            self.storage.tx(txid)
                            self.storage.delete_pending(self.address)
                            self.storage.add_contact(self.category, self.user_id, self.username, self.address)
                            self.pending_window.pending_list_box.remove(self)
                            self.pending_window.info_dialog(
                                title="New Contact Added",
                                message="The contact has been successfully stored in the list."
                            )
                            self.pending_window._impl.native.Enabled = True
                            return
                        await asyncio.sleep(3)
                else:
                    self.pending_window._impl.native.Enabled = True
        else:
            self.pending_window._impl.native.Enabled = True


    def reject_button_click(self, sender, event):
        self.storage.ban(self.address)
        self.storage.delete_pending(self.address)
        self.pending_window.pending_list_box.remove(self)


    def show_pending_info(self, sender, event):
        self.pending_window.info_dialog(
            title = "Pending info",
            message = f"- Username : {self.username}\n- ID : {self.user_id}\n- Address : {self.address}"
        )

    def confirm_button_mouse_enter(self, sender, event):
        self.confirm_button.image = "images/confirm_a.png"

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.image = "images/confirm_i.png"

    def reject_button_mouse_enter(self, sender, event):
        self.reject_button.image = "images/reject_a.png"

    def reject_button_mouse_leave(self, sender, event):
        self.reject_button.image = "images/reject_i.png"



class Message(Box):
    def __init__(self, author, message, amount, timestamp, app:App):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                padding = (0,30,5,5),
                background_color=rgb(40,43,48)
            )
        )

        self.app = app
        self.utils = Utils(self.app)
        
        self.author = author
        self.message = message
        self.amount = amount
        self.timestamp = timestamp

        if self.author == "you":
            color = GRAY
        else:
            color = rgb(114,137,218)

        message_time = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

        self.author_value = Label(
            text=f"{self.author} :",
            style=Pack(
                color = color,
                font_size = 13,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                padding = (0,0,8,5),
                flex = 1
            )
        )

        self.gift_value = Label(
            text="",
            style=Pack(
                color = YELLOW,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                padding = (8,5,0,0)
            )
        )

        self.message_time = Label(
            text=message_time,
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                padding = (8,5,0,0)
            )
        )

        self.sender_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36)
            )
        )

        self.message_value = RichLabel(
            text=f"  {self.message}",
            text_size=10,
            borderstyle=BorderStyle.NONE,
            background_color=Color.rgb(30,33,36),
            color=Color.WHITE,
            style=FontStyle.BOLD,
            wrap=True,
            readonly=True,
            urls=True,
            dockstyle=DockStyle.FILL,
            scrollbars=ScrollBars.NONE
        )

        self.message_box = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(40,43,48),
                height = 80,
                padding_top = 1
            )
        )
        self.add(
            self.sender_box,
            self.message_box
        )
        if self.amount > 0.0001:
            gift = self.amount - 0.0001
            gift_format = self.utils.format_balance(gift)
            self.gift_value.text = f"Gift : {gift_format}"
            self.sender_box.add(
                self.author_value,
                self.gift_value,
                self.message_time
            )
        else:
            self.sender_box.add(
                self.author_value,
                self.message_time
            )
        self.message_box._impl.native.Controls.Add(self.message_value)



class NewContact(Window):
    def __init__(self):
        super().__init__(
            size = (600, 150),
            resizable= False,
            minimizable = False,
            closable=False
        )

        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.storage = Storage(self.app)

        self.is_valid_toggle = None

        self.title = "Add Contact"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.info_label = Label(
            text="Enter the message address",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 11,
                padding_top = 5
            )
        )

        self.address_input = TextInput(
            placeholder="Z Address",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                width = 450
            ),
            on_change=self.is_valid_address
        )

        self.is_valid = ImageView(
            style=Pack(
                background_color = rgb(30,33,36),
                width = 30,
                height = 30,
                padding= (2,0,0,10)
            )
        )

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (10,0,10,0)
            )
        )

        self.close_button = ImageView(
            image="images/close_i.png",
            style=Pack(
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                padding_right = 10
            )
        )
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave
        self.close_button._impl.native.Click += self.close_indentity_setup

        self.confirm_button = ImageView(
            image="images/confirm_i.png",
            style=Pack(
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                padding_left = 10
            )
        )
        self.confirm_button._impl.native.MouseEnter += self.confirm_button_mouse_enter
        self.confirm_button._impl.native.MouseLeave += self.confirm_button_mouse_leave
        self.confirm_button._impl.native.Click += self.verify_address

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER,
                background_color = rgb(30,33,36)
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.input_box,
            self.buttons_box
        )
        self.input_box.add(
            self.address_input,
            self.is_valid
        )
        self.buttons_box.add(
            self.close_button,
            self.confirm_button
        )


    async def is_valid_address(self, widget):
        address = self.address_input.value
        if not address:
            self.is_valid.image = None
            return
        if address.startswith("z"):
            result, _ = await self.commands.z_validateAddress(address)
        else:
            self.is_valid.image = "images/notvalid.png"
            return
        if result is not None:
            result = json.loads(result)
            is_valid = result.get('isvalid')
            if is_valid is True:
                self.is_valid.image = "images/valid.png"
                self.is_valid_toggle = True
            elif is_valid is False:
                self.is_valid.image = "images/notvalid.png"
                self.is_valid_toggle = False

    
    def verify_address(self, sender, event):
        address = self.address_input.value
        if not address:
            return
        if not self.is_valid_toggle:
            self.error_dialog(
                title="Invalid Address",
                message="The address entered is not valid. Please check and try again."
            )
            return
        contacts = self.storage.get_contacts("address")
        if address in contacts:
            self.error_dialog(
                title="Address Already in Contacts",
                message="This address is already in your contacts list."
            )
            return
        pending = self.storage.get_pending("address")
        if address in pending:
            self.error_dialog(
                title="Address in Pending List",
                message="This address is already in your pending list."
            )
            return
        requests = self.storage.get_requests()
        if address in requests:
            self.error_dialog(
                title="Address in Requests",
                message="This address is already in your requests list."
            )
            return
        self.app.add_background_task(self.send_request)


    async def send_request(self, widget):
        destination_address = self.address_input.value
        amount = 0.0001
        txfee = 0.0001
        category, id, username, address = self.storage.get_identity()
        memo = {"type":"request","category":category,"id":id,"username":username,"address":address}
        memo_str = json.dumps(memo)
        self._impl.native.Enabled = False
        await self.send_memo(
            address,
            destination_address,
            amount,
            txfee,
            memo_str
        )


    async def send_memo(self, address, toaddress, amount, txfee, memo):
        operation, _= await self.commands.SendMemo(address, toaddress, amount, txfee, memo)
        if operation:
            transaction_status, _= await self.commands.z_getOperationStatus(operation)
            transaction_status = json.loads(transaction_status)
            if isinstance(transaction_status, list) and transaction_status:
                status = transaction_status[0].get('status')
                if status == "executing" or status =="success":
                    await asyncio.sleep(1)
                    while True:
                        transaction_result, _= await self.commands.z_getOperationResult(operation)
                        transaction_result = json.loads(transaction_result)
                        if isinstance(transaction_result, list) and transaction_result:
                            result = transaction_result[0].get('result', {})
                            txid = result.get('txid')
                            self.storage.tx(txid)
                            self.storage.add_request(toaddress)
                            self.info_dialog(
                                title="Request sent",
                                message="The request has been sent successfully to the address."
                            )
                            self.close()
                            return
                        await asyncio.sleep(3)
                else:
                    self._impl.native.Enabled = True
        else:
            self._impl.native.Enabled = True

    def confirm_button_mouse_enter(self, sender, event):
        self.confirm_button.image = "images/confirm_a.png"

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.image = "images/confirm_i.png"

    def close_button_mouse_enter(self, sender, event):
        self.close_button.image = "images/close_a.png"

    def close_button_mouse_leave(self, sender, event):
        self.close_button.image = "images/close_i.png"
    
    def close_indentity_setup(self, sender, event):
        self.close()


class PendingList(Window):
    def __init__(self, chat:Box):
        super().__init__(
            size = (500, 400),
            resizable= False,
            minimizable = False,
            closable=False
        )

        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.chat = chat

        self.title = "Pending List"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.no_pending_label = Label(
            text="Empty list",
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                font_size = 10,
                background_color = rgb(30,33,36),
                flex = 1,
                text_align = CENTER
            )
        )

        self.no_pending_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.pending_list_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.pending_list = ScrollContainer(
            horizontal=None,
            style=Pack(
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.close_button = ImageView(
            image="images/close_i.png",
            style=Pack(
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10
            )
        )
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

        self.content = self.main_box

        self.get_pending_list()

    def get_pending_list(self):
        pending = self.storage.get_pending()
        if pending:
            for data in pending:
                category = data[0]
                id = data[1]
                username = data[2]
                address = data[3]
                pending_contact = Pending(
                    category=category,
                    user_id=id,
                    username=username,
                    address=address,
                    app = self.app,
                    window = self,
                    chat = self.chat
                )
                self.pending_list_box.add(
                    pending_contact
                )
            self.main_box.add(
                self.pending_list,
                self.close_button
            )
            self.pending_list.content = self.pending_list_box
        else:
            self.main_box.add(
                self.no_pending_box,
                self.close_button
            )
            self.no_pending_box.add(
                self.no_pending_label
            )

    def insert_pending(self, category, id, username, address):
        pending_contact = Pending(
            category=category,
            user_id=id,
            username=username,
            address=address,
            window = self
        )
        self.pending_list_box.add(pending_contact)

    def close_button_mouse_enter(self, sender, event):
        self.close_button.image = "images/close_a.png"

    def close_button_mouse_leave(self, sender, event):
        self.close_button.image = "images/close_i.png"


class Chat(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                flex = 1
            )
        )

        self.app = app
        self.main = main

        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.tootip = ToolTip()
        self.clipboard = ClipBoard()

        self.send_toggle = None
        self.user_id = None
        self.user_address = None
        self.selected_contact_toggle = None
        self.pending_toggle = None
        self.new_pending_toggle = None
        self.scroll_toggle = None
        self.unread_messages_toggle = None

        self.add_contact = ImageView(
            image="images/add_contact_i.png",
            style=Pack(
                background_color = rgb(40,43,48),
                alignment = CENTER
            )
        )
        self.add_contact._impl.native.MouseEnter += self.add_contact_mouse_enter
        self.add_contact._impl.native.MouseLeave += self.add_contact_mouse_leave
        self.add_contact._impl.native.Click += self.add_contact_click
        self.tootip.insert(self.add_contact._impl.native, "Add new contact")

        self.pending_contacts = ImageView(
            image="images/pending_i.png",
            style=Pack(
                background_color = rgb(40,43,48),
                alignment = CENTER
            )
        )
        self.pending_contacts._impl.native.Click += self.pending_contacts_click
        self.tootip.insert(self.pending_contacts._impl.native, "Show pending contacts")

        self.copy_address = ImageView(
            image="images/copy_i.png",
            style=Pack(
                background_color = rgb(40,43,48),
                alignment = CENTER
            )
        )
        self.copy_address._impl.native.MouseEnter += self.copy_address_mouse_enter
        self.copy_address._impl.native.MouseLeave += self.copy_address_mouse_leave
        self.copy_address._impl.native.Click += self.copy_address_click
        self.tootip.insert(self.copy_address._impl.native, "Copy your messages address")

        self.buttons_box = Box(
            style=Pack(
                alignment = CENTER,
                direction = ROW,
                background_color= rgb(40,43,48),
                height = 32
            )
        )

        self.address_balance = Label(
            text = "Balance : 0.00000000",
            style=Pack(
                color = rgb(114,137,218),
                background_color = rgb(66,69,73),
                text_align = RIGHT,
                font_weight = BOLD,
                font_size = 10,
                flex = 1
            )
        )

        self.info_box = Box(
            style=Pack(
                alignment = CENTER,
                direction = ROW,
                background_color= rgb(66,69,73),
                height = 32,
                flex = 1
            )
        )

        self.contacts_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )
        self.contacts_scroll = ScrollContainer(
            horizontal=False,
            style=Pack(
                background_color = rgb(30,33,36),
                padding_top = 5,
                flex = 1
            )
        )

        self.panel_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                width = 300
            )
        )

        self.contact_info_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,30,30),
                height = 32,
                alignment = CENTER
            )
        )

        self.messages_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )

        self.output_box = ScrollContainer(
            horizontal=False,
            style=Pack(
                background_color = rgb(40,43,48),
                flex = 1,
                padding_bottom = 5
            )
        )

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                height = 100
            )
        )

        self.message_input = MultilineTextInput(
            placeholder="Write message",
            style=Pack(
                color = WHITE,
                font_size = 11,
                font_weight = BOLD,
                background_color = rgb(30,30,30),
                height = 90,
                flex = 1,
                padding =(3,0,0,5)
            ),
            on_change=self.update_character_count
        )
        self.message_input._impl.native.BorderStyle = BorderStyle.NONE
        self.message_input._impl.native.KeyDown += self.message_input_key_enter

        self.character_count = Label(
            text="Limit : 0 / 250",
            style=Pack(
                background_color = rgb(30,33,36),
                text_align = CENTER,
                color = GRAY,
                font_size = 10,
                font_weight = BOLD,
                flex = 1
            )
        )

        self.fee_input = TextInput(
            value="0.00020000",
            style=Pack(
                font_size = 11,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                color = rgb(114,137,218),
                padding_bottom = 2,
                text_align = CENTER
            )
        )

        self.options_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                alignment = CENTER
            )
        )

        self.send_icon = ImageView(
            image="images/send_message_i.png",
            style=Pack(
                background_color = rgb(40,43,48),
                padding_left = 40
            )
        )

        self.send_label = Label(
            text="Send",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_size = 12,
                font_weight = BOLD,
                text_align = LEFT,
                flex = 1
            )
        )

        self.send_button = Box(
            style=Pack(
                direction = ROW,
                alignment = CENTER,
                background_color = rgb(40,43,48),
                width = 150,
                height = 40
            )
        )
        self.send_button._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_button._impl.native.MouseLeave += self.send_button_mouse_leave
        self.send_icon._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_icon._impl.native.MouseLeave += self.send_button_mouse_leave
        self.send_label._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_label._impl.native.MouseLeave += self.send_button_mouse_leave
        self.send_button._impl.native.Click += self.send_button_click
        self.send_icon._impl.native.Click += self.send_button_click
        self.send_label._impl.native.Click += self.send_button_click

        self.send_box = Box(
            style=Pack(
                direction = ROW,
                alignment = BOTTOM,
                background_color = rgb(40,43,48)
            )
        )

        self.chat_buttons = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                width = 150,
                padding = 5
            )
        )

        self.chat_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 7,
                padding_left = 5
            )
        )

        self.add(
            self.panel_box,
            self.chat_box
        )
        self.panel_box.add(
            self.buttons_box,
            self.contacts_scroll
        )
        self.buttons_box.add(
            self.add_contact,
            self.pending_contacts,
            self.copy_address,
            self.info_box
        )
        self.info_box.add(
            self.address_balance
        )
        self.contacts_scroll.content = self.contacts_box
        self.chat_box.add(
            self.contact_info_box,
            self.output_box,
            self.input_box
        )
        self.output_box.content = self.messages_box
        self.input_box.add(
            self.message_input,
            self.chat_buttons
        )
        self.chat_buttons.add(
            self.options_box,
            self.send_box
        )
        self.options_box.add(
            self.character_count,
            self.fee_input
        )
        self.send_box.add(
            self.send_button
        )
        self.send_button.add(
            self.send_icon,
            self.send_label
        )


    def run_tasks(self):
        self.app.add_background_task(self.update_messages_balance)
        self.app.add_background_task(self.waiting_new_memos)
        self.app.add_background_task(self.update_contacts_list)
        self.load_pending_list()


    async def update_messages_balance(self, widget):
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue
            address = self.storage.get_identity("address")
            if address:
                balance, _= await self.commands.z_getBalance(address[0])
                if balance:
                    balance = self.utils.format_balance(balance)
                    self.address_balance.text = f"Balance : {balance}"
            
            await asyncio.sleep(5)
            

    async def waiting_new_memos(self, widget):
        while True:
            address = self.storage.get_identity("address")
            if address:
                listunspent, _= await self.commands.z_listUnspent(address[0])
                if listunspent:
                    listunspent = json.loads(listunspent)
                    list_txs = self.storage.get_txs()

                    for data in listunspent:
                        txid = data['txid']
                        if txid not in list_txs:
                            self.storage.tx(txid)
                            await self.unhexlify_memo(data)

            await asyncio.sleep(5)


    async def unhexlify_memo(self, data):
        memo = data['memo']
        amount = data['amount']
        current_time = int(datetime.now().timestamp())
        try:
            decoded_memo = binascii.unhexlify(memo)
            form = decoded_memo.decode('utf-8')
            clean_form = form.rstrip('\x00')
            form_dict = json.loads(clean_form)
            form_type = form_dict.get('type')

            if form_type == "identity":
                await self.get_identity(form_dict)
            elif form_type == "message":
                await self.get_message(form_dict, amount, current_time)
            elif form_type == "request":
                await self.get_request(form_dict)

        except Exception as e:
            print(f"Received new transaction. Amount: {amount}")
        except binascii.Error as e:
            print(f"Received new transaction. Amount: {amount}")
        except json.decoder.JSONDecodeError as e:
            print(f"Received new transaction. Amount: {amount}")


    async def get_identity(self, form):
        category = form.get('category')
        id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        requests = self.storage.get_requests()
        if address in banned:
            return
        elif address in requests:
            self.storage.delete_request(address)
            self.storage.add_contact(category, id, username, address)
            notify = NotifyRequest()
            notify.show()
            notify.send_note(
                title="Request Accepted",
                text=f"By {username}"
            )
            await asyncio.sleep(5)
            notify.hide()


    async def get_message(self, form, amount, timestamp):
        id = form.get('id')
        author = form.get('username')
        message = form.get('text')
        contacts_ids = self.storage.get_contacts("id")
        if id not in contacts_ids:
            return
        if self.user_id == id and self.main.message_button_toggle:
            self.storage.message(id, author, message, amount, timestamp)
        else:
            self.unread_messages_toggle = True
            self.storage.unread_message(id, author, message, amount, timestamp)
            notify = NotifyMessage()
            notify.show()
            notify.send_note(
                title="New Message",
                text=f"From : {author}"
            )
            await asyncio.sleep(5)
            notify.hide()


    async def get_request(self, form):
        category = form.get('category')
        id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        if address in banned:
            return
        self.storage.add_pending(category, id, username, address)
        if not self.pending_toggle:
            self.update_pending_list()
        else:
            self.pending_list.insert_pending(category, id, username, address)
        notify = NotifyRequest()
        notify.show()
        notify.send_note(
            title="New Request",
            text=f"From : {username}"
        )
        await asyncio.sleep(5)
        notify.hide()


    async def update_contacts_list(self, widget):
        self.contacts = []
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue
            contacts = self.storage.get_contacts()
            if contacts:
                for data in contacts:
                    if data not in self.contacts:
                        category = data[0]
                        id = data[1]
                        username = data[2]
                        address = data[3]
                        contact = Contact(
                            category=category,
                            user_id=id,
                            username=username,
                            address=address,
                            app = self.app,
                            main = self.main
                        )
                        contact._impl.native.Click += lambda sender, event, user_id=id, username=username, address=address:self.contact_click(
                            sender, event, user_id, username, address)
                        contact.category_icon._impl.native.Click += lambda sender, event, user_id=id, username=username, address=address:self.contact_click(
                            sender, event, user_id, username, address)
                        contact.username_label._impl.native.Click += lambda sender, event, user_id=id, username=username, address=address:self.contact_click(
                            sender, event, user_id, username, address)
                        contact.unread_messages._impl.native.Click += lambda sender, event, user_id=id, username=username, address=address:self.contact_click(
                            sender, event, user_id, username, address)
                        
                        self.contacts_box.add(
                            contact
                        )
                        self.contacts.append(data)
            await asyncio.sleep(5)


    def load_pending_list(self):
        pending = self.storage.get_pending()
        if pending:
            self.pending_contacts.image = "images/new_pending_i.png"
            self.pending_contacts._impl.native.MouseEnter += self.new_pending_contacts_mouse_enter
            self.pending_contacts._impl.native.MouseLeave += self.new_pending_contacts_mouse_leave
            self.new_pending_toggle = True
        else:
            self.pending_contacts._impl.native.MouseEnter += self.pending_contacts_mouse_enter
            self.pending_contacts._impl.native.MouseLeave += self.pending_contacts_mouse_leave


    def contact_click(self, sender, event, user_id, username, address):
        if self.user_id == user_id:
            return
        if self.selected_contact_toggle:
            self.contact_info_box.clear()
            self.messages_box.clear()
        username_label = Label(
            text="Username :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,30,30),
                font_weight = BOLD,
                padding = (9,0,0,10)
            )
        )
        username_value = Label(
            text=username,
            style=Pack(
                color = WHITE,
                background_color = rgb(30,30,30),
                font_weight = BOLD,
                padding = (9,0,0,0)
            )
        )
        id_label = Label(
            text="ID :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,30,30),
                font_weight = BOLD,
                padding = (9,0,0,10)
            )
        )
        id_value = Label(
            text=user_id,
            style=Pack(
                color = WHITE,
                background_color = rgb(30,30,30),
                font_weight = BOLD,
                padding = (9,0,0,0),
                flex =1
            )
        )
        self.unread_label = Label(
            text="--Unread Messages--",
            style=Pack(
                color = YELLOW,
                background_color = rgb(30,30,30),
                font_weight = BOLD,
                font_size = 10,
                text_align = CENTER,
                flex =1,
                padding = (0,30,5,15)
            )
        )
        self.contact_info_box.add(
            username_label,
            username_value,
            id_label,
            id_value
        )
        self.user_id = user_id
        self.user_address = address

        self.selected_contact_toggle = True
        self.last_message_timestamp = None

        messages = self.storage.get_messages(self.user_id)
        unread_messages = self.storage.get_unread_messages(self.user_id)
        if messages:
            messages = sorted(messages, key=lambda x: x[3], reverse=True)
            recent_messages = messages[:5]
            self.last_message_timestamp = recent_messages[-1][3]
            for data in recent_messages:
                message_username = data[0]
                message_text = data[1]
                message_amount = data[2]
                message_timestamp = data[3]
                message = Message(
                    author=message_username,
                    message=message_text,
                    amount=message_amount,
                    timestamp=message_timestamp,
                    app= self.app
                )
                self.messages_box.insert(
                    0, message
                )
            self.output_box.vertical_position = self.output_box.max_vertical_position
        if unread_messages:
            unread_messages = sorted(unread_messages, key=lambda x: x[3], reverse=True)
            self.messages_box.add(
                self.unread_label
            )
            self.output_box.vertical_position = self.output_box.max_vertical_position
            for data in unread_messages:
                message_username = data[0]
                message_text = data[1]
                message_amount = data[2]
                message_timestamp = data[3]
                message = Message(
                    author=message_username,
                    message=message_text,
                    amount=message_amount,
                    timestamp=message_timestamp,
                    app= self.app
                )
                self.messages_box.insert(
                    6, message
                )
        self.output_box.on_scroll = self.update_messages_on_scroll
        self.app.add_background_task(self.update_current_messages)      


    async def update_current_messages(self, widget):
        self.messages = self.storage.get_messages(self.user_id)
        self.unread_messages = self.storage.get_unread_messages(self.user_id)
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue

            messages = self.storage.get_messages(self.user_id)
            if messages:
                for data in messages:
                    if data not in self.messages:
                        author = data[0]
                        text = data[1]
                        amount = data[2]
                        timestamp = data[3]
                        self.insert_message(author, text, amount, timestamp)
                        self.messages.append(data)

            unread_messages = self.storage.get_unread_messages(self.user_id)
            if unread_messages:
                for data in unread_messages:
                    if data not in self.unread_messages:
                        author = data[0]
                        text = data[1]
                        amount = data[2]
                        timestamp = data[3]
                        self.insert_unread_message(author, text, amount, timestamp)
                        self.unread_messages.append(data)
                
            await asyncio.sleep(3)

    
    def update_messages_on_scroll(self, scroll):
        if self.output_box.vertical_position == self.output_box.max_vertical_position:
            self.messages_box.remove(self.unread_label)
            self.clean_unread_messages()
        if not self.scroll_toggle:
            if self.output_box.vertical_position == 0:
                self.scroll_toggle = True
                self.load_old_messages()


    def clean_unread_messages(self):
        unread_messages = self.storage.get_unread_messages(self.user_id)
        if unread_messages:
            for data in unread_messages:
                author = data[0]
                text = data[1]
                amount = data[2]
                timestamp = data[3]
                self.storage.message(self.user_id, author, text, amount, timestamp)
                self.messages.append(data)
            self.storage.delete_unread(self.user_id)


    def load_old_messages(self):
        messages = self.storage.get_messages(self.user_id)
        messages = sorted(messages, key=lambda x: x[3], reverse=True)
        last_loaded_message_timestamp = self.last_message_timestamp
        try:
            last_loaded_index = next(i for i, m in enumerate(messages) if m[3] == last_loaded_message_timestamp)
        except StopIteration:
            return
        older_messages = messages[last_loaded_index + 1 : last_loaded_index + 6]
        if older_messages:
            self.last_message_timestamp = older_messages[-1][3]
            for data in older_messages:
                message = Message(
                    author=data[0],
                    message=data[1],
                    amount=data[2],
                    timestamp=data[3],
                    app=self.app
                )
                self.messages_box.insert(0, message)
            self.scroll_toggle = False


    def update_pending_list(self):
        pending = self.storage.get_pending()
        if pending:
            if not self.new_pending_toggle:
                self.pending_contacts._impl.native.MouseEnter -= self.pending_contacts_mouse_enter
                self.pending_contacts._impl.native.MouseLeave -= self.pending_contacts_mouse_leave
                self.pending_contacts._impl.native.MouseEnter += self.new_pending_contacts_mouse_enter
                self.pending_contacts._impl.native.MouseLeave += self.new_pending_contacts_mouse_leave
                self.pending_contacts.image = "images/new_pending_i.png"
                self.new_pending_toggle = True



    def add_contact_click(self, sender, event):
        self.new_contact = NewContact()
        self.new_contact._impl.native.ShowDialog()
        
    
    def pending_contacts_click(self, sender, event):
        if self.new_pending_toggle:
            self.pending_contacts._impl.native.MouseEnter -= self.new_pending_contacts_mouse_enter
            self.pending_contacts._impl.native.MouseLeave -= self.new_pending_contacts_mouse_leave
            self.pending_contacts._impl.native.MouseEnter += self.pending_contacts_mouse_enter
            self.pending_contacts._impl.native.MouseLeave += self.pending_contacts_mouse_leave
            self.pending_contacts.image = "images/pending_i.png"
            self.new_pending_toggle = None
        self.pending_list = PendingList(self)
        self.pending_list.close_button._impl.native.Click += self.close_pending_list
        self.pending_list._impl.native.ShowDialog()
        self.pending_toggle = True


    def close_pending_list(self, sender, event):
        self.pending_list.close()
        self.pending_toggle = False


    def copy_address_click(self, sender, event):
        address = self.storage.get_identity("address")
        self.clipboard.copy(address[0])
        self.main.info_dialog(
            title="Copied",
            message="The messages address has been copied to clipboard."
        )


    def message_input_key_enter(self, sender, event):
        if event.KeyCode == Keys.Enter:
            self.app.add_background_task(self.verify_message)


    def send_button_click(self, sender, event):
        self.app.add_background_task(self.verify_message)


    async def verify_message(self, widget):
        message = self.message_input.value.strip()
        character_count = len(message)
        fee = self.fee_input.value
        if not message:
            self.send_button._impl.native.Focus()
            self.message_input.value = ""
            self.main.info_dialog(
                title="Message Required",
                message="Enter a message before sending."
            )
            self.message_input.focus()
            return
        elif not self.selected_contact_toggle:
            self.main.error_dialog(
                title="No Contact Selected",
                message="Select a contact from the list before sending a message."
            )
            return
        elif character_count > 250:
            self.main.error_dialog(
                title="Message Too Long",
                message="Message exceeds the maximum length of 250 characters."
            )
            return
        elif float(fee) < 0.0002:
            self.main.error_dialog(
                title="Fee Too Low",
                message="The minimum fee per message is 0.0002."
            )
            self.fee_input.value = "0.00020000"
            return
        self.app.add_background_task(self.send_message)

    
    async def send_message(self, widget):
        author = "you"
        current_time = int(datetime.now().timestamp())
        _, id, username, address = self.storage.get_identity()
        message = self.message_input.value.replace('\n', '')
        fee = self.fee_input.value
        amount = float(fee) - 0.0001
        txfee = 0.0001
        memo = {"type":"message","id":id,"username":username,"text":message}
        memo_str = json.dumps(memo)
        self.message_input.readonly = True
        self.send_button._impl.native.Enabled = False
        self.send_label._impl.native.Enabled = False
        self.send_icon._impl.native.Enabled = False
        await self.send_memo(
            address,
            amount,
            txfee,
            memo_str,
            author,
            message,
            current_time
        )


    async def send_memo(self, address, amount, txfee, memo, author, text, timestamp):
        operation, _= await self.commands.SendMemo(address, self.user_address, amount, txfee, memo)
        if operation:
            transaction_status, _= await self.commands.z_getOperationStatus(operation)
            transaction_status = json.loads(transaction_status)
            if isinstance(transaction_status, list) and transaction_status:
                status = transaction_status[0].get('status')
                if status == "executing" or status =="success":
                    await asyncio.sleep(1)
                    while True:
                        transaction_result, _= await self.commands.z_getOperationResult(operation)
                        transaction_result = json.loads(transaction_result)
                        if isinstance(transaction_result, list) and transaction_result:
                            self.message_input.value = ""
                            result = transaction_result[0].get('result', {})
                            txid = result.get('txid')
                            self.storage.tx(txid)
                            self.storage.message(self.user_id, "you", text, amount, timestamp)
                            self.message_input.readonly = False
                            self.send_button._impl.native.Enabled = True
                            self.send_label._impl.native.Enabled = True
                            self.send_icon._impl.native.Enabled = True
                            self.send_button._impl.native.Focus()
                            self.fee_input.value = "0.00020000"
                            self.character_count.style.color = GRAY
                            await asyncio.sleep(0.2)
                            self.message_input.focus()
                            return
                        await asyncio.sleep(3)
                else:
                    self.message_input.readonly = False
                    self.send_button._impl.native.Enabled = True
                    self.send_label._impl.native.Enabled = True
                    self.send_icon._impl.native.Enabled = True
        else:
            self.message_input.readonly = False
            self.send_button._impl.native.Enabled = True
            self.send_label._impl.native.Enabled = True
            self.send_icon._impl.native.Enabled = True


    def insert_message(self, author, text, amount, timestamp):
        message = Message(
            author=author,
            message=text,
            amount=amount,
            timestamp=timestamp,
            app=self.app
        )
        self.messages_box.add(
            message
        )
        self.output_box.vertical_position = self.output_box.max_vertical_position

    
    def insert_unread_message(self, author, text, amount, timestamp):
        message = Message(
            author=author,
            message=text,
            amount=amount,
            timestamp=timestamp,
            app=self.app
        )
        self.messages_box.add(
            message
        )


    def update_character_count(self, input):
        message = self.message_input.value
        if not message:
            self.character_count.text = f"Limit : 0 / 250"
            return
        character_count = len(message)
        if character_count > 250:
            self.character_count.style.color = RED
        elif character_count < 250:
            self.character_count.style.color = GRAY
        elif character_count == 250:
            self.character_count.style.color = YELLOW
        self.character_count.text = f"Limit : {character_count} / 250"
        

    def send_button_mouse_enter(self, sender, event):
        self.send_icon.image = "images/send_message_a.png"
        self.send_label.style.color = WHITE
        self.send_icon.style.background_color = rgb(114,137,218)
        self.send_label.style.background_color = rgb(114,137,218)
        self.send_button.style.background_color = rgb(114,137,218)

    def send_button_mouse_leave(self, sender, event):
        self.send_icon.image = "images/send_message_i.png"
        self.send_label.style.color = GRAY
        self.send_icon.style.background_color = rgb(40,43,48)
        self.send_label.style.background_color = rgb(40,43,48)
        self.send_button.style.background_color = rgb(40,43,48)


    def add_contact_mouse_enter(self, sender, event):
        self.add_contact.image = "images/add_contact_a.png"

    def add_contact_mouse_leave(self, sender, event):
        self.add_contact.image = "images/add_contact_i.png"

    def pending_contacts_mouse_enter(self, sender, event):
        self.pending_contacts.image = "images/pending_a.png"

    def pending_contacts_mouse_leave(self, sender, event):
        self.pending_contacts.image = "images/pending_i.png"

    def new_pending_contacts_mouse_enter(self, sender, event):
        self.pending_contacts.image = "images/new_pending_a.png"

    def new_pending_contacts_mouse_leave(self, sender, event):
        self.pending_contacts.image = "images/new_pending_i.png"

    def copy_address_mouse_enter(self, sender, event):
        self.copy_address.image = "images/copy_a.png"

    def copy_address_mouse_leave(self, sender, event):
        self.copy_address.image = "images/copy_i.png"


class Messages(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.chat = Chat(self.app, self.main)

        self.messages_toggle = None

        
    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.messages_toggle:
            data = self.storage.is_exists()
            if data:
                identity = self.storage.get_identity()
                if identity:
                    self.add(
                        self.chat
                    )
                else:
                    self.create_new_messenger()
            else:
                self.create_new_messenger()
            self.messages_toggle = True


    def create_new_messenger(self):
        self.new_messenger = NewMessenger(self, self.main, self.chat)
        self.add(self.new_messenger)


    async def gather_unread_memos(self):
        self.request_count = 0
        self.message_count = 0
        data = self.storage.is_exists()
        if data:
            address = self.storage.get_identity("address")
            if address:
                listunspent, _= await self.commands.z_listUnspent(address[0])
                if listunspent:
                    listunspent = json.loads(listunspent)
                    list_txs = self.storage.get_txs()
                    for data in listunspent:
                        txid = data['txid']
                        if txid not in list_txs:
                            await self.unhexlify_memo(data)

                    if self.request_count > 0:
                        notify = NotifyRequest()
                        notify.show()
                        notify.send_note(
                            title="New Request(s)",
                            text=f"{self.request_count} New Request(s)"
                        )
                        await asyncio.sleep(5)
                        notify.hide()
                    if self.message_count > 0:
                        notify = NotifyMessage()
                        notify.show()
                        notify.send_note(
                            title="New Message(s)",
                            text=f"{self.message_count} New Message(s)"
                        )
                        await asyncio.sleep(5)
                        notify.hide()

                    self.chat.run_tasks()


    async def unhexlify_memo(self, data):
        memo = data['memo']
        amount = data['amount']
        txid = data['txid']
        current_time = int(datetime.now().timestamp())
        try:
            decoded_memo = binascii.unhexlify(memo)
            form = decoded_memo.decode('utf-8')
            clean_form = form.rstrip('\x00')
            form_dict = json.loads(clean_form)
            form_type = form_dict.get('type')

            if form_type == "message":
                self.storage.tx(txid)
                await self.get_message(form_dict, amount, current_time)
                self.message_count += 1
            elif form_type == "request":
                self.storage.tx(txid)
                await self.get_request(form_dict)
                self.request_count += 1

        except Exception as e:
            pass
        except binascii.Error as e:
            pass
        except json.decoder.JSONDecodeError as e:
            pass


    async def get_message(self, form, amount, timestamp):
        id = form.get('id')
        author = form.get('username')
        message = form.get('text')
        contacts_ids = self.storage.get_contacts("id")
        if id not in contacts_ids:
            return
        self.storage.unread_message(id, author, message, amount, timestamp)


    async def get_request(self, form):
        category = form.get('category')
        id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        if address in banned:
            return
        self.storage.add_pending(category, id, username, address)
