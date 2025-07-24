
import asyncio
import json
import binascii
from datetime import datetime
import webbrowser
from decimal import Decimal

from toga import (
    App, Box, Label, Window, TextInput, ImageView,
    ScrollContainer, Button
)
from ..framework import (
    BorderStyle, ToolTip, ClipBoard, RichLabel,
    Color, DockStyle, ScrollBars, Forms, Command,
    FlatStyle, Drawing, Relation, Os, AlignContent,
    MenuStrip, RightToLeft, AlignRichLabel
)
from toga.style.pack import Pack
from toga.constants import (
    COLUMN, ROW, CENTER, BOLD,
    BOTTOM, HIDDEN, VISIBLE
)
from toga.colors import (
    rgb, WHITE, GRAY, RED, YELLOW, ORANGE, BLACK,
    GREENYELLOW
)

from .marketplace import MarketView
from .storage import StorageMessages
from .notify import NotifyRequest, NotifyMessage     



class EditUser(Window):
    def __init__(self, main:Window, username, settings, utils, tr, font):
        super().__init__(
            size = (450, 120),
            resizable= False
        )

        self.main = main
        self.username = username

        self.settings = settings
        self.utils = utils
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)

        self.title = self.tr.title("edituser_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.username_label = Label(
            text=self.tr.text("username_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36)
            )
        )
        self.username_label._impl.native.Font = self.font.get(11, True)

        self.username_input = TextInput(
            value=self.username,
            placeholder=self.tr.text("username_input"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                width = 250
            )
        )
        self.username_input._impl.native.Font = self.font.get(11, True)

        self.username_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding_top = 20
            )
        )

        self.cancel_button = Button(
            text=self.tr.text("cancel_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_edit_window
        )
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.confirm_button = Button(
            text=self.tr.text("confirm_button"),
            style=Pack(
                color = GRAY,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (0,0,10,20),
                width = 100
            ),
            on_press=self.verify_username
        )
        self.confirm_button._impl.native.Font = self.font.get(self.tr.size("confirm_button"), True)
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
        self.content = self.main_box

        self.main_box.add(
            self.username_box,
            self.buttons_box
        )
        if self.rtl:
            self.username_box.add(
                self.username_input,
                self.username_label
            )
        else:
            self.username_box.add(
                self.username_label,
                self.username_input
            )
        self.buttons_box.add(
            self.cancel_button,
            self.confirm_button
        )

    def verify_username(self, button):
        if not self.username_input.value:
            self.error_dialog(
                title="Missing Username",
                message="The username is required for messages address."
            )
            self.username_input.focus()
            return
        if self.username_input.value == self.username:
            self.error_dialog(
                title="Duplicate Username",
                message="The username you entered is the same as your current username."
            )
            self.username_input.focus()
            return
        username = self.username_input.value
        self.storage.edit_username(self.username, username)
        self.info_dialog(
            title="Updated Successfully",
            message="Your username has been successfully updated."
        )
        self.close()


    def confirm_button_mouse_enter(self, sender, event):
        self.confirm_button.style.color = BLACK
        self.confirm_button.style.background_color = GREENYELLOW

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.style.color = GRAY
        self.confirm_button.style.background_color = rgb(30,33,36)

    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)
    
    def close_edit_window(self, button):
        self.close()
        self.app.current_window = self.main


class Indentifier(Window):
    def __init__(self, messages:Box, main:Window, chat, settings, utils, commands, tr, font):
        super().__init__(
            size = (450, 120),
            resizable= False
        )

        self.main = main
        self.chat = chat
        self.messages_page = messages

        self.settings = settings
        self.utils = utils
        self.commands = commands
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)

        self.title = self.tr.title("newmessenger_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.username_label = Label(
            text=self.tr.text("username_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_size = 12,
                font_weight = BOLD
            )
        )
        self.username_label._impl.native.Font = self.font.get(11, True)

        self.username_input = TextInput(
            placeholder=self.tr.text("username_input"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                width = 250
            )
        )
        self.username_input._impl.native.Font = self.font.get(11, True)

        self.username_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding_top = 20
            )
        )

        self.cancel_button = Button(
            text=self.tr.text("cancel_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_indentity_setup
        )
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.confirm_button = Button(
            text=self.tr.text("confirm_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (0,0,10,20),
                width = 100
            ),
            on_press=self.verify_identity
        )
        self.confirm_button._impl.native.Font = self.font.get(self.tr.size("confirm_button"), True)
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

        self.content = self.main_box

        self.main_box.add(
            self.username_box,
            self.buttons_box
        )
        if self.rtl:
            self.username_box.add(
                self.username_input,
                self.username_label
            )
        else:
            self.username_box.add(
                self.username_label,
                self.username_input
            )
        self.buttons_box.add(
            self.cancel_button,
            self.confirm_button
        )

    def verify_identity(self, button):
        if not self.username_input.value:
            self.error_dialog(
                title="Missing Username",
                message="The username is required for messages address"
            )
            self.username_input.focus()
            return
        self.app.add_background_task(self.setup_new_identity)


    async def setup_new_identity(self, widget):
        category = "individual"
        username = self.username_input.value
        messages_address, _ = await self.commands.z_getNewAddress()
        if messages_address:
            prv_key, _= await self.commands.z_ExportKey(messages_address)
            if prv_key:
                self.storage.key(prv_key)
            self.storage.identity(category, username, messages_address)
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

    def confirm_button_mouse_enter(self, sender, event):
        self.confirm_button.style.color = BLACK
        self.confirm_button.style.background_color = GREENYELLOW

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.style.color = GRAY
        self.confirm_button.style.background_color = rgb(30,33,36)

    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)
    
    def close_indentity_setup(self, button):
        self.close()
        self.app.current_window = self.main



class NewMessenger(Box):
    def __init__(self, app:App, messages, main:Window, chat, settings, utils, commands, tr, font):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )

        self.app = app
        self.messages_page = messages
        self.main = main
        self.chat = chat

        self.settings = settings
        self.utils = utils
        self.commands = commands
        self.tr = tr
        self.font = font

        self.newmessenger_label = Label(
            text=self.tr.text("newmessenger_label"),
            style=Pack(
                text_align = CENTER,
                color = GRAY,
                background_color = rgb(40,43,48)
            )
        )
        self.newmessenger_label._impl.native.Font = self.font.get(11, True)

        self.create_button = Button(
            text=self.tr.text("create_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 200,
                padding_top = 8
            ),
            on_press=self.create_button_click
        )
        self.create_button._impl.native.Font = self.font.get(11, True)
        new_i_id = self.messages_icon("images/new_id_i.png")
        self.create_button._impl.native.Image = Drawing.Image.FromFile(new_i_id)
        self.create_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.create_button._impl.native.TextImageRelation = Relation.IMAGEBEFORETEXT
        self.create_button._impl.native.ImageAlign = AlignContent.RIGHT
        self.create_button._impl.native.MouseEnter += self.create_button_mouse_enter
        self.create_button._impl.native.MouseLeave += self.create_button_mouse_leave

        self.add(
            self.newmessenger_label,
            self.create_button
        )

    
    def create_button_click(self, button):
        self.indentity = Indentifier(
            self.messages_page, self.main, self.chat, self.settings, self.utils, self.commands, self.tr, self.font
        )
        self.indentity._impl.native.ShowDialog(self.main._impl.native)

    
    def create_button_mouse_enter(self, sender, event):
        new_a_id = self.messages_icon("images/new_id_a.png")
        self.create_button._impl.native.Image = Drawing.Image.FromFile(new_a_id)
        self.create_button.style.color = BLACK
        self.create_button.style.background_color = rgb(114,137,218)

    def create_button_mouse_leave(self, sender, event):
        new_i_id = self.messages_icon("images/new_id_i.png")
        self.create_button._impl.native.Image = Drawing.Image.FromFile(new_i_id)
        self.create_button.style.color = GRAY
        self.create_button.style.background_color = rgb(30,33,36)

    def messages_icon(self, path):
        return Os.Path.Combine(str(self.app.paths.app), path)


class Contact(Box):
    def __init__(self, data, app:App, chat, main:Window, utils, units, commands, settings, tr, font):
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

        self.category = data[0]
        self.contact_id = data[2]
        self.username = data[3]
        self.address = data[4]
        self.unread_count = 0

        self.app = app
        self.chat = chat
        self.main = main
        self.utils = utils
        self.units = units
        self.commands = commands
        self.settings = settings
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)
        self.clipboard = ClipBoard()

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        if self.category == "individual":
            image_path = "images/individual.png"
        elif self.category == "group":
            image_path = "images/group.png"

        self.category_icon = ImageView(
            image=image_path,
            style=Pack(
                background_color = rgb(40,43,48),
                padding = self.tr.padding("category_icon")
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
                padding_top = 11
            )
        )
        self.username_label._impl.native.Font = self.font.get(11, True)
        self.username_label._impl.native.MouseEnter += self.contact_mouse_enter
        self.username_label._impl.native.MouseLeave += self.contact_mouse_leave

        self.unread_messages = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = RED,
                text_align = CENTER,
                padding = self.tr.padding("unread_messages")
            )
        )
        self.unread_messages._impl.native.Font = self.font.get(9)
        self.unread_messages._impl.native.MouseEnter += self.contact_mouse_enter
        self.unread_messages._impl.native.MouseLeave += self.contact_mouse_leave

        if self.rtl:
            self.add(
                self.unread_messages,
                self.username_label,
                self.category_icon
            )
        else:
            self.add(
                self.category_icon,
                self.username_label,
                self.unread_messages
            )
        self.insert_contact_menustrip()
        self.app.add_background_task(self.update_contact)


    def insert_contact_menustrip(self):
        context_menu = MenuStrip(rtl=self.rtl)
        self.copy_address_cmd = Command(
            title=self.tr.text("copy_address_cmd"),
            icon="images/copy_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.copy_address_cmd_mouse_enter,
            mouse_leave=self.copy_address_cmd_mouse_leave,
            action=self.copy_contact_address,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.ban_contact_cmd = Command(
            title=self.tr.text("ban_contact_cmd"),
            icon="images/ban_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.ban_contact_cmd_mouse_enter,
            mouse_leave=self.ban_contact_cmd_mouse_leave,
            action=self.ban_contact,
            font=self.font.get(9),
            rtl=self.rtl
        )
        commands = [
            self.copy_address_cmd,
            self.ban_contact_cmd
        ]
        self.market = self.storage.get_hostname(self.contact_id)
        if self.market:
            self.marketplace_cmd = Command(
                title="Visit marketplace",
                icon="images/marketplace_i.ico",
                color=Color.WHITE,
                background_color=Color.rgb(30,33,36),
                mouse_enter=self.marketplace_cmd_mouse_enter,
                mouse_leave=self.marketplace_cmd_mouse_leave,
                action=self.show_contact_market,
                font=self.font.get(9),
                rtl=self.rtl
            )
            commands.append(self.marketplace_cmd)
        for command in commands:
            context_menu.Items.Add(command)
        self._impl.native.ContextMenuStrip = context_menu
        self.category_icon._impl.native.ContextMenuStrip = context_menu
        self.username_label._impl.native.ContextMenuStrip = context_menu


    def reload_contact_menustrip(self):
        self._impl.native.ContextMenuStrip = None
        self.category_icon._impl.native.ContextMenuStrip = None
        self.username_label._impl.native.ContextMenuStrip = None
        self.insert_contact_menustrip()


    async def update_contact(self, widget):
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue
            username = self.storage.get_contact_username(self.contact_id)
            if username:
                if username[0] != self.username:
                    self.username_label.text = username[0]
                    self.username = username[0]
            unread_messages = self.storage.get_unread_messages(self.contact_id)
            if unread_messages:
                unread_count = len(unread_messages)
                if unread_count > self.unread_count:
                    self.unread_messages.text = unread_count
                    self.unread_messages.style.visibility = VISIBLE
                    self.unread_count = unread_count
            else:
                self.unread_messages.text = ""
                self.unread_messages.style.visibility = HIDDEN
                self.unread_count = 0
            if not self.market:
                self.market = self.storage.get_hostname(self.contact_id)
                if self.market:
                    self.reload_contact_menustrip()
            await asyncio.sleep(3)


    def copy_contact_address(self):
        self.clipboard.copy(self.address)
        self.main.info_dialog(
            title=self.tr.title("copyaddress_dialog"),
            message=self.tr.message("copyaddress_dialog"),
        )


    def ban_contact(self):
        def on_result(widget, result):
            def on_second_result(widget, result):
                if result is None:
                    if self.chat.selected_contact_toggle:
                        self.chat.contact_info_box.clear()
                        self.chat.messages_box.clear()
                        self.chat.last_message_timestamp = None
                        self.chat.last_unread_timestamp = None
                        self.chat.selected_contact_toggle = None
            if result is True:
                self.storage.ban(self.address)
                self.storage.delete_contact(self.address)
                self.chat.contacts_box.remove(self)
                self.main.info_dialog(
                    title="Contact Banned",
                    message=f"The contact has been successfully banned and deleted:\n\n"
                            f"- Username: {self.username}\n"
                            f"- User ID: {self.contact_id}\n"
                            f"- Address: {self.address}",
                    on_result=on_second_result
                )

        self.main.question_dialog(
            title="Ban Contact",
            message=f"Are you sure you want to ban and delete this contact?\n\n"
                    f"- Username: {self.username}\n"
                    f"- User ID: {self.contact_id}\n"
                    f"- Address: {self.address}",
            on_result=on_result
        )


    def show_contact_market(self):
        if not self.chat.marketplace_toggle:
            self.market_window = MarketView(
                self.chat, self.main, self.utils, self.units, self.commands, self.tr, self.font, self.username, self.contact_id
            )
            self.market_window.show()
            self.chat.marketplace_toggle = True


    def contact_mouse_enter(self, sender, event):
        self.category_icon.style.background_color = rgb(66,69,73)
        self.username_label.style.background_color = rgb(66,69,73)
        self.style.background_color = rgb(66,69,73)

    def contact_mouse_leave(self, sender, event):
        self.category_icon.style.background_color = rgb(40,43,48)
        self.username_label.style.background_color = rgb(40,43,48)
        self.style.background_color = rgb(40,43,48)


    def copy_address_cmd_mouse_enter(self):
        self.copy_address_cmd.icon = "images/copy_a.ico"
        self.copy_address_cmd.color = Color.BLACK

    def copy_address_cmd_mouse_leave(self):
        self.copy_address_cmd.icon = "images/copy_i.ico"
        self.copy_address_cmd.color = Color.WHITE

    def ban_contact_cmd_mouse_enter(self):
        self.ban_contact_cmd.icon = "images/ban_a.ico"
        self.ban_contact_cmd.color = Color.BLACK

    def ban_contact_cmd_mouse_leave(self):
        self.ban_contact_cmd.icon = "images/ban_i.ico"
        self.ban_contact_cmd.color = Color.WHITE

    def marketplace_cmd_mouse_enter(self):
        self.marketplace_cmd.icon = "images/marketplace_a.ico"
        self.marketplace_cmd.color = Color.BLACK

    def marketplace_cmd_mouse_leave(self):
        self.marketplace_cmd.icon = "images/marketplace_i.ico"
        self.marketplace_cmd.color = Color.WHITE


class Pending(Box):
    def __init__(self, category, contact_id, username, address, app:App, window:Window, chat:Box, utils, units, commands, font):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 50
            )
        )
        self._impl.native.DoubleClick += self.show_pending_info

        self.pending_window = window
        self.chat = chat
        self.category = category
        self.contact_id = contact_id
        self.username = username
        self.address = address

        self.app = app
        self.commands = commands
        self.utils = utils
        self.units = units
        self.font = font

        self.storage = StorageMessages(self.app)

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
                padding_top = 11
            )
        )
        self.username_label._impl.native.Font = self.font.get(11, True)
        self.username_label._impl.native.DoubleClick += self.show_pending_info

        self.confirm_button = Button(
            text="Confirm",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_top = 10,
                width = 100
            ),
            on_press=self.send_identity
        )
        self.confirm_button._impl.native.Font = self.font.get(9, True)
        self.confirm_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.confirm_button._impl.native.MouseEnter += self.confirm_button_mouse_enter
        self.confirm_button._impl.native.MouseLeave += self.confirm_button_mouse_leave

        self.reject_button = Button(
            text="Reject",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (10,10,0,10),
                width = 100
            ),
            on_press=self.reject_button_click
        )
        self.reject_button._impl.native.Font = self.font.get(9, True)
        self.reject_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.reject_button._impl.native.MouseEnter += self.reject_button_mouse_enter
        self.reject_button._impl.native.MouseLeave += self.reject_button_mouse_leave

        self.add(
            self.category_icon,
            self.username_label,
            self.confirm_button,
            self.reject_button
        )


    async def send_identity(self, button):
        destination_address = self.address
        amount = 0.0001
        txfee = 0.0001
        category, username, address = self.storage.get_identity()
        id = self.units.generate_id()
        memo = {"type":"identity","category":category,"id":id,"username":username,"address":address}
        memo_str = json.dumps(memo)
        self.pending_window._impl.native.Enabled = False
        await self.send_memo(
            address,
            destination_address,
            amount,
            txfee,
            memo_str,
            id
        )


    async def send_memo(self, address, toaddress, amount, txfee, memo, id):
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
                            self.storage.add_contact(self.category, id, self.contact_id, self.username, self.address)
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


    def reject_button_click(self, button):
        self.storage.ban(self.address)
        self.storage.delete_pending(self.address)
        self.pending_window.pending_list_box.remove(self)


    def show_pending_info(self, sender, event):
        self.pending_window.info_dialog(
            title = "Pending info",
            message = f"- Username : {self.username}\n- ID : {self.contact_id}\n- Address : {self.address}"
        )

    def confirm_button_mouse_enter(self, sender, event):
        self.confirm_button.style.color = BLACK
        self.confirm_button.style.background_color = GREENYELLOW

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.style.color = GRAY
        self.confirm_button.style.background_color = rgb(30,33,36)

    def reject_button_mouse_enter(self, sender, event):
        self.reject_button.style.color = BLACK
        self.reject_button.style.background_color = RED

    def reject_button_mouse_leave(self, sender, event):
        self.reject_button.style.color = GRAY
        self.reject_button.style.background_color = rgb(30,33,36)



class Message(Box):
    def __init__(self, author, message, amount, timestamp, app:App, output:ScrollContainer, settings, utils, units, tr, font):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                padding = (0,10,5,5),
                background_color=rgb(30,33,36)
            )
        )

        self.wheel = 0

        self.app = app
        self.output_box = output
        self.author = author
        self.message = message
        self.amount = amount
        self.timestamp = timestamp

        self.settings = settings
        self.utils = utils
        self.units = units
        self.font = font
        self.tr = tr

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True
                message_align = AlignRichLabel.RIGHT
            else:
                message_align = AlignRichLabel.LEFT
        else:
            message_align = AlignRichLabel.LEFT

        if self.author == "you":
            if self.rtl:
                self.author = "أنت :"
            color = GRAY
        else:
            color = rgb(114,137,218)

        message_time = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        if self.rtl:
            message_time = self.units.arabic_digits(message_time)

        self.author_value = Label(
            text=self.author,
            style=Pack(
                color = color,
                background_color = rgb(30,30,30),
                padding = self.tr.padding("author_value"),
                flex = 1
            )
        )
        self.author_value._impl.native.Font = self.font.get(11, True)

        self.gift_value = Label(
            text="",
            style=Pack(
                color = YELLOW,
                background_color = rgb(30,30,30),
                font_weight = BOLD
            )
        )
        self.gift_value._impl.native.Font = self.font.get(9)

        self.message_time = Label(
            text=message_time,
            style=Pack(
                color = GRAY,
                background_color = rgb(30,30,30)
            )
        )
        self.message_time._impl.native.Font = self.font.get(9)

        self.sender_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,30,30),
                height = 27
            )
        )

        self.message_value = RichLabel(
            text=f"{self.message}",
            borderstyle=BorderStyle.NONE,
            background_color=Color.rgb(30,33,36),
            color=Color.WHITE,
            font = self.font.get(10),
            wrap=True,
            readonly=True,
            urls=True,
            text_align=message_align,
            dockstyle=DockStyle.FILL,
            scrollbars=ScrollBars.NONE,
            urls_click=self.show_url_dialog,
            mouse_wheel=self.on_scroll
        )

        self.message_box = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(40,43,48),
                height = 90,
                padding = self.tr.padding("message_box")
            )
        )

        self.add(
            self.sender_box,
            self.message_box
        )
        if self.amount > 0.0001:
            gift = self.amount - 0.0001
            gift_format = self.units.format_balance(gift)
            text = self.tr.text("gift_value")
            self.gift_value.text = f"{text} {gift_format}"
            if self.rtl:
                self.sender_box.add(
                    self.message_time,
                    self.gift_value,
                    self.author_value
                )
            else:
                self.sender_box.add(
                    self.author_value,
                    self.gift_value,
                    self.message_time
                )
        else:
            if self.rtl:
                self.sender_box.add(
                    self.message_time,
                    self.author_value
                )
            else:
                self.sender_box.add(
                    self.author_value,
                    self.message_time
                )
        self.message_box._impl.native.Controls.Add(self.message_value)


    def show_url_dialog(self, url):
        self.url = url
        def on_result(widget, result):
            if result is True:
                webbrowser.open(self.url)
        self.app.main_window.question_dialog(
            title="Confirm URL Redirect",
            message=f"Are you sure you want to visit the following URL?\n\n{self.url}\n\nPlease confirm to proceed.",
            on_result=on_result
        )

    
    def on_scroll(self, value):
        self.wheel = self.output_box.vertical_position - value
        self.output_box.vertical_position = self.wheel



class NewContact(Window):
    def __init__(self, main:Window, settings, utils, units, commands, tr, font):
        super().__init__(
            size = (600, 120),
            resizable= False
        )

        self.main = main
        self.is_valid_toggle = None
        
        self.settings = settings
        self.utils = utils
        self.units = units
        self.commands = commands
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)

        self.title = self.tr.title("addcontact_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.address_input = TextInput(
            placeholder="Z Address",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                width = 450
            ),
            on_change=self.is_valid_address
        )
        self.address_input._impl.native.Font = self.font.get(11, True)

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
                padding = (0,0,10,0)
            )
        )

        self.cancel_button = Button(
            text=self.tr.text("cancel_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_indentity_setup
        )
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.confirm_button = Button(
            text=self.tr.text("confirm_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (0,0,10,20),
                width = 100
            ),
            on_press=self.verify_address
        )
        self.confirm_button._impl.native.Font = self.font.get(self.tr.size("confirm_button"), True)
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

        self.content = self.main_box

        self.main_box.add(
            self.input_box,
            self.buttons_box
        )
        self.input_box.add(
            self.address_input,
            self.is_valid
        )
        self.buttons_box.add(
            self.cancel_button,
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

    
    def verify_address(self, button):
        address = self.address_input.value
        if not address:
            return
        if not self.is_valid_toggle:
            self.error_dialog(
                title=self.tr.title("invalidaddress_dialog"),
                message=self.tr.message("invalidaddress_dialog")
            )
            return
        contacts = self.storage.get_contacts("address")
        if address in contacts:
            self.error_dialog(
                title=self.tr.title("addressexists_dialog"),
                message=self.tr.message("addressexists_dialog")
            )
            return
        pending = self.storage.get_pending()
        if address in pending:
            self.error_dialog(
                title=self.tr.title("addressinpending_dialog"),
                message=self.tr.message("addressinpending_dialog")
            )
            return
        requests = self.storage.get_requests()
        if address in requests:
            self.error_dialog(
                title=self.tr.title("addressinrequest_dialog"),
                message=self.tr.message("addressinrequest_dialog")
            )
            return
        banned = self.storage.get_banned()
        if address in banned:
            self.error_dialog(
                title=self.tr.title("addressisbanned_dialog"),
                message=self.tr.message("addressisbanned_dialog")
            )
            return
        self.app.add_background_task(self.send_request)


    async def send_request(self, widget):
        destination_address = self.address_input.value
        amount = 0.0001
        txfee = 0.0001
        id = self.units.generate_id()
        category, username, address = self.storage.get_identity()
        memo = {"type":"request","category":category,"id":id,"username":username,"address":address}
        memo_str = json.dumps(memo)
        self._impl.native.Enabled = False
        await self.send_memo(
            address,
            destination_address,
            amount,
            txfee,
            memo_str,
            id
        )


    async def send_memo(self, address, toaddress, amount, txfee, memo, id):
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
                            self.storage.add_request(id, toaddress)
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
        self.confirm_button.style.color = BLACK
        self.confirm_button.style.background_color = GREENYELLOW

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.style.color = GRAY
        self.confirm_button.style.background_color = rgb(30,33,36)

    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)
    
    def close_indentity_setup(self, button):
        self.close()
        self.app.current_window = self.main


class PendingList(Window):
    def __init__(self, chat:Box, utils, units, commands, tr, font):
        super().__init__(
            size = (500, 400),
            resizable= False
        )

        self.chat = chat

        self.utils = utils
        self.units = units
        self.commands = commands
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)

        self.title = self.tr.title("pendinglist_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.no_pending_label = Label(
            text=self.tr.text("no_pending_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                flex = 1,
                text_align = CENTER
            )
        )
        self.no_pending_label._impl.native.Font = self.font.get(10, True)

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

        self.close_button = Button(
            text=self.tr.text("close_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            )
        )
        self.close_button._impl.native.Font = self.font.get(self.tr.size("close_button"), True)
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
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
                    contact_id=id,
                    username=username,
                    address=address,
                    app = self.app,
                    window = self,
                    chat = self.chat,
                    utils=self.utils, units=self.units, commands=self.commands, font=self.font
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
            contact_id=id,
            username=username,
            address=address,
            window = self,
            chat=self.chat,
            utils=self.utils, units=self.units, commands=self.commands, font=self.font
        )
        self.pending_list_box.add(pending_contact)

    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)


class Chat(Box):
    def __init__(self, app:App, main:Window, settings, utils, units, commands, tr, font):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                flex = 1
            )
        )

        self.send_toggle = None
        self.contact_id = None
        self.user_address = None
        self.selected_contact_toggle = None
        self.pending_toggle = None
        self.new_pending_toggle = None
        self.scroll_toggle = None
        self.unread_messages_toggle = None
        self.last_message_timestamp = None
        self.last_unread_timestamp = None
        self.marketplace_toggle = None
        self.fee_input = None
        self.messages = []
        self.unread_messages = []
        self.processed_timestamps = set()

        self.app = app
        self.main = main

        self.utils = utils
        self.units = units
        self.commands = commands
        self.settings = settings
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)
        self.tooltip = ToolTip()
        self.clipboard = ClipBoard()

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True


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
        self.tooltip.insert(self.add_contact._impl.native, "Add new contact")

        self.pending_contacts = ImageView(
            image="images/pending_i.png",
            style=Pack(
                background_color = rgb(40,43,48),
                alignment = CENTER
            )
        )
        self.pending_contacts._impl.native.Click += self.pending_contacts_click
        self.tooltip.insert(self.pending_contacts._impl.native, "Show pending contacts")

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
        self.tooltip.insert(self.copy_address._impl.native, "Copy your messages address")

        self.buttons_box = Box(
            style=Pack(
                alignment = CENTER,
                direction = ROW,
                background_color= rgb(40,43,48),
                height = 32
            )
        )

        self.address_balance = Label(
            text = self.tr.text("address_balance"),
            style=Pack(
                color = rgb(114,137,218),
                background_color = rgb(66,69,73),
                text_align = self.tr.align("address_balance"),
                flex = 1
            )
        )
        self.address_balance._impl.native.Font = self.font.get(9, True)

        self.list_unspent_utxos = Label(
            "",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                padding = self.tr.padding("list_unspent_utxos")
            )
        )
        self.list_unspent_utxos._impl.native.Font = self.font.get(9, True)
        self.tooltip.insert(self.list_unspent_utxos._impl.native, "Number of unspent shielded notes")

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
        self.messages_box._impl.native.Resize += self.messages_box_on_resize

        self.output_box = ScrollContainer(
            horizontal=False,
            style=Pack(
                background_color = rgb(40,43,48),
                flex = 1,
                padding = (0,5,5,0)
            )
        )
        if self.rtl:
            self.output_box._impl.native.RightToLeft = RightToLeft.YES

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 100,
                alignment = BOTTOM,
                padding = self.tr.padding("input_box")
            )
        )

        self.message_input = TextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,30,30),
                flex = 1,
                padding = self.tr.padding("message_input")
            ),
            on_change=self.update_character_count,
            on_confirm=self.verify_message
        )
        self.message_input._impl.native.Font = self.font.get(self.tr.size("message_input"), True)
        if self.rtl:
            self.message_input._impl.native.RightToLeft = RightToLeft.YES
        self.message_input.placeholder = self.tr.text("message_input")

        text = self.tr.text("character_count")
        value = "0 / 325"
        if self.rtl:
            value = self.units.arabic_digits(value)

        self.character_count = Label(
            text=f"{text} {value}",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = GRAY,
                flex = 1
            )
        )
        self.character_count._impl.native.Font = self.font.get(10)

        self.fee_input = TextInput(
            value="0.00020000",
            style=Pack(
                background_color = rgb(30,33,36),
                color = rgb(114,137,218),
                padding_bottom = 5,
                text_align = CENTER
            ),
            validators=[
                self.is_digit
            ]
        )
        self.fee_input._impl.native.Font = self.font.get(10, True)

        self.options_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment = CENTER
            )
        )

        self.send_button = Button(
            text=self.tr.text("sendmessage_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                flex = 1
            ),
            on_press=self.verify_message
        )
        self.send_button._impl.native.Font = self.font.get(self.tr.size("sendmessage_button"), True)
        send_i_icon = self.messages_icon("images/send_message_i.png")
        self.send_button._impl.native.Image = Drawing.Image.FromFile(send_i_icon)
        self.send_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.send_button._impl.native.TextImageRelation = Relation.IMAGEBEFORETEXT
        self.send_button._impl.native.ImageAlign = AlignContent.RIGHT
        self.send_button._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_button._impl.native.MouseLeave += self.send_button_mouse_leave

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
                background_color = rgb(40,43,48),
                width = 150,
                padding = 5
            )
        )

        self.chat_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 7,
                padding_left = 5
            )
        )

        if self.rtl:
            self.add(
                self.chat_box,
                self.panel_box
            )
        else:
            self.add(
                self.panel_box,
                self.chat_box
            )
        self.panel_box.add(
            self.buttons_box,
            self.contacts_scroll
        )
        if self.rtl:
            self.buttons_box.add(
                self.info_box,
                self.copy_address,
                self.pending_contacts,
                self.add_contact
            )
            self.info_box.add(
                self.address_balance,
                self.list_unspent_utxos
            )
        else:
            self.buttons_box.add(
                self.add_contact,
                self.pending_contacts,
                self.copy_address,
                self.info_box
            )
            self.info_box.add(
                self.list_unspent_utxos,
                self.address_balance
            )
        self.contacts_scroll.content = self.contacts_box

        self.chat_box.add(
            self.contact_info_box,
            self.output_box,
            self.input_box
        )
        self.output_box.content = self.messages_box
        if self.rtl:
            self.input_box.add(
                self.chat_buttons,
                self.message_input
            )
        else:
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

        self.insert_context_menu()


    def insert_context_menu(self):
        fee_context_menu = MenuStrip(rtl=self.rtl)
        self.fee_clear_cmd = Command(
            title="Clear",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            font=self.font.get(9),
            mouse_enter=self.fee_clear_cmd_mouse_enter,
            mouse_leave=self.fee_clear_cmd_mouse_leave,
            action=self.clear_fee_input,
            rtl=self.rtl
        )
        fee_context_menu.Items.Add(self.fee_clear_cmd)
        self.fee_input._impl.native.ContextMenuStrip = fee_context_menu

        message_context_menu = MenuStrip(rtl=self.rtl)
        self.message_copy_cmd = Command(
            title="Copy",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            font=self.font.get(9),
            mouse_enter=self.message_cmds_mouse_enter,
            mouse_leave=self.message_cmds_mouse_leave,
            action=self.copy_message_input,
            rtl=self.rtl
        )
        self.message_paste_cmd = Command(
            title="Paste",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            font=self.font.get(9),
            mouse_enter=self.message_cmds_mouse_enter,
            mouse_leave=self.message_cmds_mouse_leave,
            action=self.paste_message_input,
            rtl=self.rtl
        )
        self.message_clear_cmd = Command(
            title="Clear",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            font=self.font.get(9),
            mouse_enter=self.message_cmds_mouse_enter,
            mouse_leave=self.message_cmds_mouse_leave,
            action=self.clear_message_input,
            rtl=self.rtl
        )
        commands = [
            self.message_copy_cmd,
            self.message_paste_cmd,
            self.message_clear_cmd
        ]
        for command in commands:
            message_context_menu.Items.Add(command)
        self.message_input._impl.native.ContextMenuStrip = message_context_menu


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
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            address = self.storage.get_identity("address")
            if address:
                balance, _= await self.commands.z_getBalance(address[0])
                if balance:
                    text = self.tr.text("address_balance")
                    balance = self.units.format_balance(balance)
                    if self.rtl:
                        balance = self.units.arabic_digits(balance)
                    self.address_balance.text = f"{text} {balance}"
            
            await asyncio.sleep(5)
            

    async def waiting_new_memos(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            address = self.storage.get_identity("address")
            if address:
                listunspent, _= await self.commands.z_listUnspent(address[0], 0)
                if listunspent:
                    listunspent = json.loads(listunspent)
                    self.count_list_unspent(listunspent)
                    if len(listunspent) >= 54:
                        total_balance,_ = await self.commands.z_getBalance(address[0])
                        merge_fee = Decimal('0.0002')
                        txfee = Decimal('0.0001')
                        amount = Decimal(total_balance) - merge_fee
                        await self.merge_utxos(address[0], amount, txfee)
                    list_txs = self.storage.get_txs()
                    for data in listunspent:
                        txid = data['txid']
                        if txid not in list_txs:
                            await self.unhexlify_memo(data)

            await asyncio.sleep(5)


    def count_list_unspent(self, listunspent):
        count = len(listunspent)
        if count >= 50:
            self.list_unspent_utxos.style.color = RED
        elif count >= 20:
            self.list_unspent_utxos.style.color = ORANGE
        else:
            self.list_unspent_utxos.style.color = WHITE
        self.list_unspent_utxos.text = count


    async def merge_utxos(self, address, amount, txfee):
        memo = "merge"
        operation, _= await self.commands.SendMemo(address, address, amount, txfee, memo)
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
                            status = transaction_result[0].get('status')
                            result = transaction_result[0].get('result', {})
                            if status == "failed":
                                    return
                            txid = result.get('txid')
                            self.storage.tx(txid)
                            return
                        await asyncio.sleep(3)


    async def unhexlify_memo(self, data):
        memo = data['memo']
        amount = data['amount']
        txid = data['txid']
        try:
            decoded_memo = binascii.unhexlify(memo)
            form = decoded_memo.decode('utf-8')
            clean_form = form.rstrip('\x00')
            form_dict = json.loads(clean_form)
            form_type = form_dict.get('type')

            if form_type == "identity":
                await self.get_identity(form_dict)

            elif form_type == "message":
                await self.get_message(form_dict, amount)

            elif form_type == "request":
                await self.get_request(form_dict)

            elif form_type == "market":
                await self.get_marketplace(form_dict)

            self.storage.tx(txid)

        except (binascii.Error, json.decoder.JSONDecodeError) as e:
            self.storage.tx(txid)
        except Exception as e:
            self.storage.tx(txid)


    async def get_identity(self, form):
        category = form.get('category')
        contact_id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        if address in banned:
            return
        id = self.storage.get_request(address)
        if id:
            self.storage.add_contact(category, id[0], contact_id, username, address)
            self.storage.delete_request(address)
            if self.settings.notification_messages():
                notify = NotifyRequest()
                notify.show()
                notify.send_note(
                    title="Request Accepted",
                    text=f"By {username}"
                )
                await asyncio.sleep(5)
                notify.hide()
                notify.dispose()


    async def get_message(self, form, amount):
        contact_id = form.get('id')
        author = form.get('username')
        message = form.get('text')
        timestamp = form.get('timestamp')
        contact_username = self.storage.get_contact_username(contact_id)
        if not contact_username:
            return
        self.processed_timestamps.add(timestamp)
        if author != contact_username:
            self.storage.update_contact_username(author, contact_id)
        if self.contact_id == contact_id and self.main.message_button_toggle and not self.main._is_minimized and self.main._is_active:
            self.storage.message(contact_id, author, message, amount, timestamp)
            self.username_value.text = author
        else:
            await self.handler_unread_message(contact_id, author, message, amount, timestamp)


    async def handler_unread_message(self,contact_id, author, message, amount, timestamp):
        self.unread_messages_toggle = True
        self.storage.unread_message(contact_id, author, message, amount, timestamp)
        if self.settings.notification_messages():
            notify = NotifyMessage()
            notify.show()
            notify.send_note(
                title="New Message",
                text=f"{author} : {message[:100]}"
            )
            await asyncio.sleep(5)
            notify.hide()
            notify.dispose()


    async def get_request(self, form):
        category = form.get('category')
        contact_id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        if address in banned:
            return
        self.storage.add_pending(category, contact_id, username, address)
        if not self.pending_toggle:
            self.update_pending_list()
        else:
            self.pending_list.insert_pending(category, contact_id, username, address)
        if self.settings.notification_messages():
            notify = NotifyRequest()
            notify.show()
            notify.send_note(
                title="New Request",
                text=f"From : {username}"
            )
            await asyncio.sleep(5)
            notify.hide()
            notify.dispose()


    async def get_marketplace(self, form):
        contact_id = form.get('id')
        hostname = form.get('hostname')
        contact_username = self.storage.get_contact_username(contact_id)
        if not contact_username:
            return
        if not self.storage.get_hostname(contact_id):
            self.storage.insert_market(contact_id, hostname)
            return
        self.storage.update_market(contact_id, hostname)
            


    async def update_contacts_list(self, widget):
        self.contacts = []
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue
            contacts = self.storage.get_contacts()
            if contacts:
                for data in contacts:
                    try:
                        contact_id = data[2]
                        address = data[4]
                        if contact_id not in self.contacts:
                            contact = Contact(
                                data, self.app, self, self.main, self.utils, self.units, self.commands, self.settings, self.tr, self.font
                            )
                            contact._impl.native.Click += lambda sender, event, contact_id=contact_id, address=address:self.contact_click(
                                sender, event, contact_id, address)
                            contact.category_icon._impl.native.Click += lambda sender, event, contact_id=contact_id, address=address:self.contact_click(
                                sender, event, contact_id, address)
                            contact.username_label._impl.native.Click += lambda sender, event, contact_id=contact_id, address=address:self.contact_click(
                                sender, event, contact_id, address)
                            contact.unread_messages._impl.native.Click += lambda sender, event, contact_id=contact_id, address=address:self.contact_click(
                                sender, event, contact_id, address)
                            
                            self.contacts_box.add(
                                contact
                            )
                            self.contacts.append(contact_id)
                    except IndexError:
                        print(f"Skipping contact due to missing data: {data}")
                        continue
                    except Exception as e:
                        print(f"Unexpected error: {e}, data: {data}")
                        continue
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


    def contact_click(self, sender, event, contact_id, address):
        if self.send_toggle:
            return
        if event.Button == Forms.MouseButtons.Right:
            return
        if self.contact_id == contact_id:
            return
        username = self.storage.get_contact_username(contact_id)
        if self.selected_contact_toggle:
            self.contact_info_box.clear()
            self.messages_box.clear()
            self.last_message_timestamp = None
            self.last_unread_timestamp = None
        self.selected_contact_toggle = True
        self.processed_timestamps.clear()

        username_label = Label(
            text=self.tr.text("username_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,30,30),
                font_weight = BOLD,
                padding = self.tr.padding("username_label")
            )
        )
        self.username_value = Label(
            text=username[0],
            style=Pack(
                color = WHITE,
                background_color = rgb(30,30,30),
                font_weight = BOLD,
                padding = (9,0,0,0),
                text_align = self.tr.align("username_value")
            )
        )
        id_label = Label(
            text=self.tr.text("id_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,30,30),
                font_weight = BOLD,
                padding = self.tr.padding("id_label")
            )
        )
        id_value = Label(
            text=contact_id,
            style=Pack(
                color = WHITE,
                background_color = rgb(30,30,30),
                font_weight = BOLD,
                padding = (9,0,0,0),
                flex =1,
                text_align = self.tr.align("id_value")
            )
        )
        self.unread_label = Label(
            text=self.tr.text("unread_label"),
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
        if self.rtl:
            self.contact_info_box.add(
                id_value,
                id_label,
                self.username_value,
                username_label,
            )
        else:
            self.contact_info_box.add(
                username_label,
                self.username_value,
                id_label,
                id_value
            )
        self.contact_id = contact_id
        self.user_address = address

        self.messages = self.storage.get_messages(self.contact_id)
        if self.messages:
            messages = sorted(self.messages, key=lambda x: x[3], reverse=True)
            recent_messages = messages[:5]
            self.last_message_timestamp = recent_messages[-1][3]
            for data in recent_messages:
                message_username = data[0]
                message_text = data[1]
                message_amount = data[2]
                message_timestamp = data[3]
                self.processed_timestamps.add(message_timestamp)
                message = Message(
                    author=message_username,
                    message=message_text,
                    amount=message_amount,
                    timestamp=message_timestamp,
                    app= self.app,
                    output = self.output_box,
                    settings=self.settings, utils=self.utils, units=self.units, tr=self.tr, font=self.font
                )
                self.messages_box.insert(
                    0, message
                )
        self.unread_messages = self.storage.get_unread_messages(self.contact_id)
        if self.unread_messages:
            unread_messages = sorted(self.unread_messages, key=lambda x: x[3], reverse=False)
            recent_unread_messages = unread_messages[:5]
            self.last_unread_timestamp = recent_unread_messages[-1][3]
            self.messages_box.add(
                self.unread_label
            )
            for data in unread_messages:
                message_username = data[0]
                message_text = data[1]
                message_amount = data[2]
                message_timestamp = data[3]
                self.processed_timestamps.add(message_timestamp)
                message = Message(
                    author=message_username,
                    message=message_text,
                    amount=message_amount,
                    timestamp=message_timestamp,
                    app= self.app,
                    output = self.output_box,
                    settings=self.settings, utils=self.utils, units=self.units, tr=self.tr, font=self.font
                )
                self.messages_box.add(
                    message
                )
        self.output_box.on_scroll = self.update_messages_on_scroll
        self.app.add_background_task(self.update_current_messages)     


    async def update_current_messages(self, widget):
        self.messages = self.storage.get_messages(self.contact_id)
        self.unread_messages = self.storage.get_unread_messages(self.contact_id)
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue

            messages = self.storage.get_messages(self.contact_id)
            if messages:
                for data in messages:
                    if data not in self.messages:
                        author = data[0]
                        text = data[1]
                        amount = data[2]
                        timestamp = data[3]
                        await self.insert_message(author, text, amount, timestamp)
                        self.messages.append(data)

            unread_messages = self.storage.get_unread_messages(self.contact_id)
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

    
    async def update_messages_on_scroll(self, scroll):
        if self.output_box.vertical_position == self.output_box.max_vertical_position:
            self.messages_box.remove(self.unread_label)
            self.clean_unread_messages()

        if not self.scroll_toggle:
            if self.output_box.vertical_position == 0:
                self.scroll_toggle = True
                await self.load_old_messages()

            if self.output_box.vertical_position == self.output_box.max_vertical_position:
                self.scroll_toggle = True
                await self.load_unread_messages()


    def clean_unread_messages(self):
        unread_messages = self.storage.get_unread_messages(self.contact_id)
        if unread_messages:
            for data in unread_messages:
                author = data[0]
                text = data[1]
                amount = data[2]
                timestamp = data[3]
                self.storage.message(self.contact_id, author, text, amount, timestamp)
                self.messages.append(data)
            self.storage.delete_unread(self.contact_id)


    async def load_old_messages(self):
        messages = self.storage.get_messages(self.contact_id)
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
                    app=self.app,
                    output=self.output_box,
                    settings=self.settings, utils=self.utils, units=self.units, tr=self.tr, font=self.font
                )
                self.messages_box.insert(0, message)
            await asyncio.sleep(1)
        self.scroll_toggle = False


    async def load_unread_messages(self):
        unread_messages = self.storage.get_unread_messages(self.contact_id)
        if unread_messages:
            unread_messages = sorted(unread_messages, key=lambda x: x[3], reverse=False)
            more_unread_messages = [m for m in unread_messages if m[3] < self.last_unread_timestamp]
            more_unread_messages = more_unread_messages[:5]

            for data in more_unread_messages:
                message_username = data[0]
                message_text = data[1]
                message_amount = data[2]
                message_timestamp = data[3]
                self.processed_timestamps.add(message_timestamp)
                message = Message(
                    author=message_username,
                    message=message_text,
                    amount=message_amount,
                    timestamp=message_timestamp,
                    app=self.app,
                    output=self.output_box,
                    settings=self.settings, utils=self.utils, units=self.units, tr=self.tr, font=self.font
                )
                self.messages_box.add(message)

            if more_unread_messages:
                self.last_unread_timestamp = more_unread_messages[-1][3]
                await asyncio.sleep(1)
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
        self.new_contact = NewContact(
            self.main, self.settings, self.utils, self.units, self.commands, self.tr, self.font
        )
        self.new_contact._impl.native.ShowDialog(self.main._impl.native)
        
    
    def pending_contacts_click(self, sender, event):
        if self.new_pending_toggle:
            self.pending_contacts._impl.native.MouseEnter -= self.new_pending_contacts_mouse_enter
            self.pending_contacts._impl.native.MouseLeave -= self.new_pending_contacts_mouse_leave
            self.pending_contacts._impl.native.MouseEnter += self.pending_contacts_mouse_enter
            self.pending_contacts._impl.native.MouseLeave += self.pending_contacts_mouse_leave
            self.pending_contacts.image = "images/pending_i.png"
            self.new_pending_toggle = None
        self.pending_list = PendingList(self, self.utils, self.units, self.commands, self.tr, self.font)
        self.pending_list.close_button.on_press = self.close_pending_list
        self.pending_list._impl.native.ShowDialog(self.main._impl.native)
        self.pending_toggle = True


    def close_pending_list(self, button):
        self.pending_list.close()
        self.pending_toggle = False


    def copy_address_click(self, sender, event):
        address = self.storage.get_identity("address")
        self.clipboard.copy(address[0])
        self.main.info_dialog(
            title="Copied",
            message="The messages address has been copied to clipboard."
        )


    async def verify_message(self, widget):
        message = self.message_input.value.strip()
        character_count = len(message)
        fee = self.fee_input.value
        if not message:
            self.send_button._impl.native.Focus()
            self.message_input.value = ""
            self.main.error_dialog(
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
        elif character_count > 325:
            self.main.error_dialog(
                title="Message Too Long",
                message="Message exceeds the maximum length of 325 characters."
            )
            return
        elif float(fee) < 0.0002:
            self.main.error_dialog(
                title="Fee Too Low",
                message="The minimum fee per message is 0.0002."
            )
            self.fee_input.value = "0.00020000"
            return
        if message.lower() == "/market":
            self.app.add_background_task(self.handle_market_command)
            return
        self.app.add_background_task(self.send_message)


    async def handle_market_command(self, widget):
        if not self.settings.market_service():
            self.main.error_dialog(
                title="Disbaled",
                message="Your marketplace service is disabled"
            )
            return
        hostname = self.utils.get_onion_hostname("market")
        _, _, address = self.storage.get_identity()
        id = self.storage.get_id_contact(self.contact_id)
        fee = self.fee_input.value
        amount = float(fee) - 0.0001
        txfee = 0.0001
        memo = {"type":"market","id":id[0],"hostname":hostname}
        memo_str = json.dumps(memo)
        self.disable_send_button()
        await self.send_command(address, amount, txfee, memo_str)


    async def send_command(self, address, amount, txfee, memo):
        async def on_result(widget, result):
            if result is None:
                self.send_button._impl.native.Focus()
                self.fee_input.value = "0.00020000"
                self.character_count.style.color = GRAY
                await asyncio.sleep(0.2)
                self.message_input.focus()

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
                            self.main.info_dialog(
                                title="Market Sent",
                                message="Your market command was successfully sent",
                                on_result=on_result
                            )
                            return
                        await asyncio.sleep(3)
                else:
                    self.enable_send_button()
        else:
            self.enable_send_button()

    
    async def send_message(self, widget):
        author = "you"
        _, username, address = self.storage.get_identity()
        id = self.storage.get_id_contact(self.contact_id)
        message = self.message_input.value.replace('\n', '')
        fee = self.fee_input.value
        amount = float(fee) - 0.0001
        txfee = 0.0001
        timestamp = await self.get_message_timestamp()
        if timestamp is not None:
            memo = {"type":"message","id":id[0],"username":username,"text":message, "timestamp":timestamp}
            memo_str = json.dumps(memo)
            self.disable_send_button()
            await self.send_memo(
                address,
                amount,
                txfee,
                memo_str,
                author,
                message,
                timestamp
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
                            self.storage.message(self.contact_id, author, text, amount, timestamp)
                            self.send_button._impl.native.Focus()
                            self.fee_input.value = "0.00020000"
                            self.character_count.style.color = GRAY
                            await asyncio.sleep(0.2)
                            self.message_input.focus()
                            return
                        await asyncio.sleep(3)
                else:
                    self.enable_send_button()
        else:
            self.enable_send_button()
    

    def enable_send_button(self):
        self.send_button.text = "Send"
        send_i_icon = self.messages_icon("images/send_message_i.png")
        self.send_button._impl.native.Image = Drawing.Image.FromFile(send_i_icon)
        self.send_button.on_press = self.verify_message
        self.message_input.readonly = False
        self.send_toggle = False

    
    def disable_send_button(self):
        self.send_toggle = True
        self.send_button.text = "Sending..."
        self.send_button.on_press = None
        self.message_input.readonly = True


    async def insert_message(self, author, text, amount, timestamp):
        message = Message(
            author=author,
            message=text,
            amount=amount,
            timestamp=timestamp,
            app=self.app,
            output=self.output_box,
            settings=self.settings, utils=self.utils, units=self.units, tr=self.tr, font=self.font
        )
        self.messages_box.add(
            message
        )
        await asyncio.sleep(0.1)
        self.output_box.vertical_position = self.output_box.max_vertical_position
        self.enable_send_button()

    
    def insert_unread_message(self, author, text, amount, timestamp):
        message = Message(
            author=author,
            message=text,
            amount=amount,
            timestamp=timestamp,
            app=self.app,
            output=self.output_box,
            settings=self.settings, utils=self.utils, units=self.units, tr=self.tr, font=self.font
        )
        self.messages_box.add(
            message
        )

    def messages_box_on_resize(self, sender, event):
        if self.output_box.vertical_position == self.output_box.max_vertical_position or self.scroll_toggle:
            return
        self.output_box.vertical_position = self.output_box.max_vertical_position


    def update_character_count(self, input):
        message = self.message_input.value
        text = self.tr.text("character_count")
        value = "0 / 325"
        if self.rtl:
            value = self.units.arabic_digits(value)
        if not message:
            self.character_count.text = f"{text} {value}"
            return
        character_count = len(message)
        if character_count > 325:
            self.character_count.style.color = RED
        elif character_count < 325:
            self.character_count.style.color = GRAY
        elif character_count == 325:
            self.character_count.style.color = YELLOW
        if self.rtl:
            value = self.units.arabic_digits(f"{character_count} / 325")
        else:
            value = f"{character_count} / 325"
        self.character_count.text = f"{text} {value}"
        

    def send_button_mouse_enter(self, sender, event):
        if not self.send_toggle:
            send_a_icon = self.messages_icon("images/send_message_a.png")
            self.send_button._impl.native.Image = Drawing.Image.FromFile(send_a_icon)
            self.send_button.style.color = BLACK
            self.send_button.style.background_color = rgb(114,137,218)

    def send_button_mouse_leave(self, sender, event):
        if not self.send_toggle:
            send_i_icon = self.messages_icon("images/send_message_i.png")
            self.send_button._impl.native.Image = Drawing.Image.FromFile(send_i_icon)
            self.send_button.style.color = GRAY
            self.send_button.style.background_color = rgb(30,33,36)

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


    async def get_message_timestamp(self):
        blockchaininfo, _ = await self.commands.getBlockchainInfo()
        if blockchaininfo is not None:
            if isinstance(blockchaininfo, str):
                info = json.loads(blockchaininfo)
                if info is not None:
                    timestamp = info.get('mediantime')
                    if timestamp in self.processed_timestamps:
                        highest_timestamp = max(self.processed_timestamps)
                        timestamp = highest_timestamp + 1
                    self.processed_timestamps.add(timestamp)
                    return timestamp
                

    def messages_icon(self, path):
        return Os.Path.Combine(str(self.app.paths.app), path)
    
    def is_digit(self, input):
        if self.fee_input:
            if not self.fee_input.value.replace('.', '', 1).isdigit():
                self.fee_input.value = "0.00020000"

    def clear_fee_input(self):
        self.fee_input.value = "0.00020000"

    def clear_message_input(self):
        self.character_count.style.color = GRAY
        self.message_input.value = ""

    def copy_message_input(self):
        value = self.message_input.value
        self.clipboard.copy(value)

    def paste_message_input(self):
        value = self.clipboard.paste()
        self.message_input.value = value

    def fee_clear_cmd_mouse_enter(self):
        self.fee_clear_cmd.color = Color.BLACK

    def fee_clear_cmd_mouse_leave(self):
        self.fee_clear_cmd.color = Color.WHITE

    def message_cmds_mouse_enter(self, sender):
        sender.ForeColor = Color.BLACK

    def message_cmds_mouse_leave(self, sender):
        sender.ForeColor = Color.WHITE
                


class Messages(Box):
    def __init__(self, app:App, main:Window, settings, utils, units, commands, tr, font):
        super().__init__(
            style=Pack(
                direction = ROW,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )

        self.messages_toggle = None
        self.request_count = 0
        self.message_count = 0

        self.app = app
        self.main = main
        self.commands = commands
        self.settings = settings
        self.utils = utils
        self.units = units
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)
        self.chat = Chat(self.app, self.main, settings, utils, units, commands, tr, font)

        
    async def insert_widgets(self, widget):
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
        self.new_messenger = NewMessenger(
            self.app, self, self.main, self.chat, self.settings, self.utils, self.commands, self.tr, self.font
        )
        self.add(self.new_messenger)


    async def gather_unread_memos(self):
        data = self.storage.is_exists()
        if data:
            address = self.storage.get_identity("address")
            if address:
                listunspent, _= await self.commands.z_listUnspent(address[0], 0)
                if listunspent:
                    listunspent = json.loads(listunspent)
                    list_txs = self.storage.get_txs()
                    for data in listunspent:
                        txid = data['txid']
                        if txid not in list_txs:
                            await self.unhexlify_memo(data)

                    if self.request_count > 0:
                        if self.settings.notification_messages():
                            notify = NotifyRequest()
                            notify.show()
                            notify.send_note(
                                title="New Request(s)",
                                text=f"{self.request_count} New Request(s)"
                            )
                            await asyncio.sleep(5)
                            notify.hide()
                            notify.dispose()
                    if self.message_count > 0:
                        if self.settings.notification_messages():
                            notify = NotifyMessage()
                            notify.show()
                            notify.send_note(
                                title="New Message(s)",
                                text=f"{self.message_count} New Message(s)"
                            )
                            await asyncio.sleep(5)
                            notify.hide()
                            notify.dispose()
                        
                    self.chat.run_tasks()


    async def unhexlify_memo(self, data):
        memo = data['memo']
        amount = data['amount']
        txid = data['txid']
        try:
            decoded_memo = binascii.unhexlify(memo)
            form = decoded_memo.decode('utf-8')
            clean_form = form.rstrip('\x00')
            form_dict = json.loads(clean_form)
            form_type = form_dict.get('type')

            if form_type == "message":
                await self.get_message(form_dict, amount)
                self.storage.tx(txid)
                self.message_count += 1
            elif form_type == "request":
                await self.get_request(form_dict)
                self.storage.tx(txid)
                self.request_count += 1

        except (binascii.Error, json.decoder.JSONDecodeError) as e:
            self.storage.tx(txid)
        except Exception as e:
            self.storage.tx(txid)


    async def get_message(self, form, amount):
        id = form.get('id')
        author = form.get('username')
        message = form.get('text')
        timestamp = form.get('timestamp')
        contacts_ids = self.storage.get_contacts("contact_id")
        if id not in contacts_ids:
            return
        self.storage.unread_message(id, author, message, amount, timestamp)
        self.chat.processed_timestamps.add(timestamp)


    async def get_request(self, form):
        category = form.get('category')
        id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        if address in banned:
            return
        self.storage.add_pending(category, id, username, address)