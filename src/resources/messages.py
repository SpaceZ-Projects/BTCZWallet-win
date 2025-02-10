
import asyncio
import string
import secrets

from toga import (
    App, Box, Label, Window, TextInput, ImageView,
)
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.colors import rgb, WHITE, GRAY

from .storage import Storage
from .utils import Utils
from .client import Client


class Indentifier(Window):
    def __init__(self, messages:Box, main:Window):
        super().__init__(
            size = (600, 150),
            resizable= False,
            minimizable = False,
            closable=False
        )

        self.main = main

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
    def __init__(self, messages, main:Window):
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
        self.indentity = Indentifier(self.messages_page, self.main)
        self.indentity._impl.native.ShowDialog()

    
    def create_button_mouse_enter(self, sender, event):
        self.create_label.style.color = WHITE
        self.create_label.style.background_color = rgb(114,137,218)
        self.create_button.style.background_color = rgb(114,137,218)

    def create_button_mouse_leave(self, sender, event):
        self.create_label.style.color = GRAY
        self.create_label.style.background_color = rgb(30,33,36)
        self.create_button.style.background_color = rgb(30,33,36)


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
        self.storage = Storage(self.app)

        self.messages_toggle = None

        
    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.messages_toggle:
            data = self.storage.is_exists()
            if data:
                pass
            else:
                self.create_new_messenger()
            self.messages_toggle = True
            

    def create_new_messenger(self):
        self.new_messenger = NewMessenger(self, self.main)
        self.add(self.new_messenger)