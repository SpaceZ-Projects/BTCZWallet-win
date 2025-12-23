
import asyncio
from datetime import datetime, timezone

from toga import App, Window, Box, ImageView, Button, Label, TextInput
from ..framework import FlatStyle, Drawing, Os, Sys
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.colors import rgb, GRAY, GREENYELLOW, BLACK, WHITE, RED, YELLOW

from .storage import StorageMobile, StorageTxs, StorageAddresses, StorageMessages



class AuthQR(Window):
    def __init__(self, mobile_window:Window, utils, font, device_id, device_name, device_secret):
        super().__init__(
            resizable=False,
            closable=False
        )

        self.mobile_window = mobile_window
        self.utils = utils
        self.font = font

        self.device_id = device_id
        self.device_secret = device_secret
        self.hostname_toggle = None
        self.auth_toggle = None
        self.secretkey_toggle = None

        self.title = f"Device : {device_name}"
        self.size = (450,450)
        position_center = self.utils.window_center_to_parent(self.mobile_window, self)
        self.position = position_center
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.hostname_button = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,30,30),
                flex = 1,
                alignment = CENTER,
                padding = 2
            )
        )
        self.hostname_label = Label(
            text="Hostname",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,30,30),
                text_align = CENTER,
                padding = (10,0,10,0)
            )
        )
        self.hostname_label._impl.native.Font = self.font.get(11, True)
        self.hostname_button._impl.native.MouseEnter += self.hostname_button_mouse_enter
        self.hostname_label._impl.native.MouseEnter += self.hostname_button_mouse_enter
        self.hostname_button._impl.native.MouseLeave += self.hostname_button_mouse_leave
        self.hostname_label._impl.native.MouseLeave += self.hostname_button_mouse_leave
        self.hostname_button._impl.native.Click += self.hostname_button_click
        self.hostname_label._impl.native.Click += self.hostname_button_click

        self.auth_button = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,30,30),
                flex = 1,
                alignment = CENTER,
                padding = 2
            )
        )
        self.auth_label = Label(
            text="Authorization",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,30,30),
                text_align = CENTER,
                padding = (10,0,10,0)
            )
        )
        self.auth_label._impl.native.Font = self.font.get(11, True)
        self.auth_button._impl.native.MouseEnter += self.auth_button_mouse_enter
        self.auth_label._impl.native.MouseEnter += self.auth_button_mouse_enter
        self.auth_button._impl.native.MouseLeave += self.auth_button_mouse_leave
        self.auth_label._impl.native.MouseLeave += self.auth_button_mouse_leave
        self.auth_button._impl.native.Click += self.auth_button_click
        self.auth_label._impl.native.Click += self.auth_button_click

        self.secretkey_button = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,30,30),
                flex = 1,
                alignment = CENTER,
                padding = 2
            )
        )
        self.secretkey_label = Label(
            text="Secret Key",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,30,30),
                text_align = CENTER,
                padding = (10,0,10,0)
            )
        )
        self.secretkey_label._impl.native.Font = self.font.get(11, True)
        self.secretkey_button._impl.native.MouseEnter += self.secretkey_button_mouse_enter
        self.secretkey_label._impl.native.MouseEnter += self.secretkey_button_mouse_enter
        self.secretkey_button._impl.native.MouseLeave += self.secretkey_button_mouse_leave
        self.secretkey_label._impl.native.MouseLeave += self.secretkey_button_mouse_leave
        self.secretkey_button._impl.native.Click += self.secretkey_button_click
        self.secretkey_label._impl.native.Click += self.secretkey_button_click

        self.switch_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                height = 80
            )
        )

        self.qr_view = ImageView(
            style=Pack(
                background_color = rgb(30,33,36),
                width = 275,
                height = 275
            )
        )

        self.qr_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.close_button = Button(
            text="Close",
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_auth_qr
        )
        self.close_button._impl.native.Font = self.font.get(9, True)
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.switch_box,
            self.qr_box,
            self.close_button
        )
        self.switch_box.add(
            self.hostname_button,
            self.auth_button,
            self.secretkey_button
        )
        self.hostname_button.add(
            self.hostname_label
        )
        self.auth_button.add(
            self.auth_label
        )
        self.secretkey_button.add(
            self.secretkey_label
        )
        self.qr_box.add(
            self.qr_view
        )

        self.hostname_button_click(None, None)


    def hostname_button_click(self, sender, event):
        self.clear_buttons()
        self.hostname_toggle = True
        self.hostname_button._impl.native.Click -= self.hostname_button_click
        self.hostname_label._impl.native.Click -= self.hostname_button_click
        self.hostname_label.style.color = WHITE
        self.hostname_label.style.background_color = rgb(66,69,73)
        self.hostname_button.style.background_color = rgb(66,69,73)
        self.show_hostname_qr()


    def show_hostname_qr(self):
        hostname = self.utils.get_onion_hostname("mobile")
        if hostname:
            qr_image = self.utils.qr_generate(hostname)
            if qr_image:
                self.qr_view.image = qr_image


    def auth_button_click(self, sender, event):
        self.clear_buttons()
        self.auth_toggle = True
        self.auth_button._impl.native.Click -= self.auth_button_click
        self.auth_label._impl.native.Click -= self.auth_button_click
        self.auth_label.style.color = WHITE
        self.auth_label.style.background_color = rgb(66,69,73)
        self.auth_button.style.background_color = rgb(66,69,73)
        self.show_auth_qr()


    def show_auth_qr(self):
        qr_image = self.utils.qr_generate(self.device_id)
        if qr_image:
            self.qr_view.image = qr_image


    def secretkey_button_click(self, sender, event):
        self.clear_buttons()
        self.secretkey_toggle = True
        self.secretkey_button._impl.native.Click -= self.secretkey_button_click
        self.secretkey_label._impl.native.Click -= self.secretkey_button_click
        self.secretkey_label.style.color = WHITE
        self.secretkey_label.style.background_color = rgb(66,69,73)
        self.secretkey_button.style.background_color = rgb(66,69,73)
        self.show_secretkey_qr()


    def show_secretkey_qr(self):
        qr_image = self.utils.qr_generate(self.device_secret, True)
        if qr_image:
            self.qr_view.image = qr_image


    def clear_buttons(self):
        if self.hostname_toggle:
            self.hostname_label.style.color = GRAY
            self.hostname_label.style.background_color = rgb(30,30,30)
            self.hostname_button.style.background_color = rgb(30,30,30)
            self.hostname_button._impl.native.Click += self.hostname_button_click
            self.hostname_label._impl.native.Click += self.hostname_button_click
            self.hostname_toggle = None

        elif self.auth_toggle:
            self.auth_label.style.color = GRAY
            self.auth_label.style.background_color = rgb(30,30,30)
            self.auth_button.style.background_color = rgb(30,30,30)
            self.auth_button._impl.native.Click += self.auth_button_click
            self.auth_label._impl.native.Click += self.auth_button_click
            self.auth_toggle = None

        elif self.secretkey_toggle:
            self.secretkey_label.style.color = GRAY
            self.secretkey_label.style.background_color = rgb(30,30,30)
            self.secretkey_button.style.background_color = rgb(30,30,30)
            self.secretkey_button._impl.native.Click += self.secretkey_button_click
            self.secretkey_label._impl.native.Click += self.secretkey_button_click
            self.secretkey_toggle = None


    def hostname_button_mouse_enter(self, sender, event):
        if self.hostname_toggle:
            return
        self.hostname_label.style.color = WHITE
        self.hostname_label.style.background_color = rgb(66,69,73)
        self.hostname_button.style.background_color = rgb(66,69,73)

    def hostname_button_mouse_leave(self, sender, event):
        if self.hostname_toggle:
            return
        self.hostname_label.style.color = GRAY
        self.hostname_label.style.background_color = rgb(30,30,30)
        self.hostname_button.style.background_color = rgb(30,30,30)


    def auth_button_mouse_enter(self, sender, event):
        if self.auth_toggle:
            return
        self.auth_label.style.color = WHITE
        self.auth_label.style.background_color = rgb(66,69,73)
        self.auth_button.style.background_color = rgb(66,69,73)

    def auth_button_mouse_leave(self, sender, event):
        if self.auth_toggle:
            return
        self.auth_label.style.color = GRAY
        self.auth_label.style.background_color = rgb(30,30,30)
        self.auth_button.style.background_color = rgb(30,30,30)

    def secretkey_button_mouse_enter(self, sender, event):
        if self.secretkey_toggle:
            return
        self.secretkey_label.style.color = WHITE
        self.secretkey_label.style.background_color = rgb(66,69,73)
        self.secretkey_button.style.background_color = rgb(66,69,73)

    def secretkey_button_mouse_leave(self, sender, event):
        if self.secretkey_toggle:
            return
        self.secretkey_label.style.color = GRAY
        self.secretkey_label.style.background_color = rgb(30,30,30)
        self.secretkey_button.style.background_color = rgb(30,30,30)


    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)

    def close_auth_qr(self, button):
        self.close()
        self.app.current_window = self.mobile_window




class AddDevice(Window):
    def __init__(self, mobile_window:Window, utils, units, rpc, tr, font):
        super().__init__(
            resizable=False,
            closable=False
        )

        self.mobile_window = mobile_window
        self.utils = utils
        self.units = units
        self.rpc = rpc
        self.tr = tr
        self.font = font

        self.mobile_storage = StorageMobile(self.app)

        self.title = "Add Device"
        self.size = (450,120)
        position_center = self.utils.window_center_to_parent(self.mobile_window, self)
        self.position = position_center
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.device_name_label = Label(
            text="Device Name :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER
            )
        )
        self.device_name_label._impl.native.Font = self.font.get(11, True)

        self.device_name_input = TextInput(
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                width = 250
            )
        )
        self.device_name_input._impl.native.Font = self.font.get(11, True)

        self.device_name_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.cancel_button = Button(
            text=self.tr.text("cancel_button"),
            style=Pack(
                color = RED,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_add_window
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
            on_press=self.save_device
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
            self.device_name_box,
            self.buttons_box
        )
        self.device_name_box.add(
            self.device_name_label,
            self.device_name_input
        )
        self.buttons_box.add(
            self.cancel_button,
            self.confirm_button
        )


    async def save_device(self, button):
        def on_result(widget, result):
            if result is None:
                self.close()
                self.app.current_window = self.mobile_window
        device_name = self.device_name_input.value
        if not device_name:
            self.error_dialog(
                title="Missing Name",
                message="The device name is reaquired"
            )
            return
        mobile_auth = self.units.generate_id()
        mobile_secret = self.units.generate_secret_key()
        taddress,_ = await self.rpc.getNewAddress()
        zaddress,_ = await self.rpc.z_getNewAddress()
        if not taddress:
            self.error_dialog(
                title="Generate Addresses",
                message="Failed to generate new addresses"
            )
            return
        self.mobile_storage.insert_device(mobile_auth, device_name, taddress, zaddress)
        self.mobile_storage.insert_secret(mobile_auth, mobile_secret)
        self.info_dialog(
            title="Device Added",
            message=f"The device name {device_name} has been successfully added",
            on_result=on_result
        )


    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)

    def confirm_button_mouse_enter(self, sender, event):
        self.confirm_button.style.color = BLACK
        self.confirm_button.style.background_color = GREENYELLOW

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.style.color = GRAY
        self.confirm_button.style.background_color = rgb(30,33,36)

    def close_add_window(self, button):
        self.close()
        self.app.current_window = self.mobile_window



class Device(Box):
    def __init__(self, app:App, mobile_window:Window, utils, font, device, secret):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (5,2,5,5),
                height = 100,
                alignment = CENTER
            )
        )

        self.app = app
        self.mobile_window = mobile_window
        self.utils = utils
        self.font = font
        self.storage = StorageMobile(self.app)

        self.device_secret = secret
        self.device_id = device[0]
        self.device_name = device[1]
        device_status = device[4]
        self.status = device_status
        device_timestamp = device[5]
        if device_timestamp:
            device_timestamp = datetime.fromtimestamp(device_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            device_timestamp = "Not yet"

        if device_status == "on":
            device_icon = "images/device_on.png"
        else:
            device_icon = "images/device_off.png"

        self.device_icon = ImageView(
            image=device_icon,
            style=Pack(
                background_color = rgb(40,43,48),
                padding = (3,0,0,0)
            )
        )

        self.device_name_label = Label(
            text=f"Name : {self.device_name}",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48)
            )
        )
        self.device_name_label._impl.native.Font = self.font.get(11, True)

        self.device_last_connected = Label(
            text=f"Recent Request : {device_timestamp}",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48)
            )
        )
        self.device_last_connected._impl.native.Font = self.font.get(9, True)

        self.transparent_balance = Label(
            text="T :",
            style=Pack(
                color = YELLOW,
                background_color = rgb(40,43,48)
            )
        )
        self.transparent_balance._impl.native.Font = self.font.get(9, True)

        self.shielded_balance = Label(
            text="Z :",
            style=Pack(
                color = rgb(114,137,218),
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.shielded_balance._impl.native.Font = self.font.get(9, True)

        self.device_balances_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48)
            )
        )

        self.device_info_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment=CENTER,
                flex = 2
            )
        )

        self.connect_button = Button(
            text="Connect",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                width = 100,
                padding = (10,0,0,0)
            ),
            on_press=self.show_auth_qr
        )
        self.connect_button._impl.native.Font = self.font.get(9, True)
        self.connect_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.connect_button._impl.native.MouseEnter += self.connect_button_mouse_enter
        self.connect_button._impl.native.MouseLeave += self.connect_button_mouse_leave

        self.remove_button = Button(
            text="Remove",
            style=Pack(
                color = RED,
                background_color = rgb(40,43,48),
                width = 100,
                padding = (12,0,0,0)
            ),
            on_press=self.remove_device
        )
        self.remove_button._impl.native.Font = self.font.get(9, True)
        self.remove_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.remove_button._impl.native.MouseEnter += self.remove_button_mouse_enter
        self.remove_button._impl.native.MouseLeave += self.remove_button_mouse_leave
        
        self.device_buttons_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment=CENTER,
                flex = 1
            )
        )

        self.add(
            self.device_icon,
            self.device_info_box,
            self.device_buttons_box
        )
        self.device_info_box.add(
            self.device_name_label,
            self.device_last_connected,
            self.device_balances_box
        )
        self.device_balances_box.add(
            self.transparent_balance,
            self.shielded_balance
        )
        self.device_buttons_box.add(
            self.connect_button,
            self.remove_button,
        )


    def show_auth_qr(self, button):
        auth_window = AuthQR(self.mobile_window, self.utils, self.font, self.device_id, self.device_name, self.device_secret)
        auth_window._impl.native.ShowDialog(self.mobile_window._impl.native)


    def remove_device(self, button):
        def on_result(widget, result):
            if result is False:
                return
            if result is True:
                self.storage.delete_device(self.device_id)
                self.storage.delete_secret(self.device_id)
                self.mobile_window.devices_list.remove(self)
        self.mobile_window.question_dialog(
            title="Removing Device",
            message=f"Are you sure you want to remove this device {self.device_name} ?",
            on_result=on_result
        )

    def connect_button_mouse_enter(self, sender, event):
        self.connect_button.style.color = WHITE

    def connect_button_mouse_leave(self, sender, event):
        self.connect_button.style.color = GRAY

    def remove_button_mouse_enter(self, sender, event):
        self.remove_button.style.color = BLACK
        self.remove_button.style.background_color = RED

    def remove_button_mouse_leave(self, sender, event):
        self.remove_button.style.color = RED
        self.remove_button.style.background_color = rgb(40,43,48)



class Mobile(Window):
    def __init__(self, main:Window, notify, utils, units, rpc, tr, font, server):
        super().__init__(
            resizable = False
        )

        self.main = main
        self.notify = notify

        self.utils = utils
        self.units = units
        self.rpc = rpc
        self.tr = tr
        self.font = font

        self.server = server
        self.mobile_storage = StorageMobile(self.app)
        self.txs_storage = StorageTxs(self.app)
        self.addresses_storage = StorageAddresses(self.app)
        self.messages_storage = StorageMessages(self.app)

        self.title = "Mobile Server"
        self._impl.native.Icon = self.window_icon("images/Mobile.ico")
        self._impl.native.Size = Drawing.Size(500,600)
        position_center = self.utils.window_center_to_parent(self.main, self)
        self.position = position_center
        self.on_close = self.close_mobile_window
        self._impl.native.Resize += self._handle_on_resize
        self._impl.native.MinimumSize = Drawing.Size(500,600)

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.devices_data = {}

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.add_button = Button(
            text="Add Device",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 100,
                padding =(5,10,0,10)
            ),
            on_press=self.add_new_device
        )
        self.add_button._impl.native.Font = self.font.get(9, True)
        self.add_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.add_button._impl.native.MouseEnter += self.add_button_mouse_enter
        self.add_button._impl.native.MouseLeave += self.add_button_mouse_leave

        self.devices_label = Label(
            text="Devices :",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.devices_label._impl.native.Font = self.font.get(10, True)
        
        self.connected_label = Label(
            text="Connected :",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.connected_label._impl.native.Font = self.font.get(10, True)

        self.start_server = Button(
            text="",
            enabled=False,
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 100,
                padding =(5,10,0,0)
            )
        )
        self.start_server._impl.native.FlatStyle = FlatStyle.FLAT
        self.start_server._impl.native.Font = self.font.get(9, True)

        self.menu_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 40,
                alignment = CENTER,
                padding = (0,0,10,0)
            )
        )

        self.devices_list = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.menu_box
        )
        self.menu_box.add(
            self.add_button,
            self.devices_label,
            self.connected_label,
            self.start_server
        )

        self.load_mobile_config()


    def load_mobile_config(self):
        if self.server.server_status:
            self.start_server.text = "Stop"
            self.start_server._impl.native.MouseEnter += self.stop_server_mouse_enter
            self.start_server._impl.native.MouseLeave += self.stop_server_mouse_leave
            self.start_server.on_press = self.stop_mobile_server
        else:
            self.start_server.text = "Host"
            self.start_server._impl.native.MouseEnter += self.start_server_mouse_enter
            self.start_server._impl.native.MouseLeave += self.start_server_mouse_leave
            self.start_server.on_press = self.start_mobile_server

        torrc = self.utils.read_torrc()
        if torrc:
            hs_dirs = torrc.get("HiddenServiceDir", [])
            hs_ports = torrc.get("HiddenServicePort", [])
            if not isinstance(hs_dirs, list):
                hs_dirs = [hs_dirs]
            if not isinstance(hs_ports, list):
                hs_ports = [hs_ports]
            for dir_path, port_line in zip(hs_dirs, hs_ports):
                if dir_path.endswith("mobile_service"):
                    self.mobile_port = port_line.split()[1].split(":")[1] if port_line else ""
                    self.start_server.enabled = True
                    
        self.app.loop.create_task(self.updating_devices_status())
        self.app.loop.create_task(self.load_devices_list())
        self.app.loop.create_task(self.updating_devices_list())


    async def load_devices_list(self):
        devices_list = self.mobile_storage.get_devices()
        if devices_list:
            for device in devices_list:
                device_id = device[0]
                device_secret = self.mobile_storage.get_secret(device_id)
                device_info = Device(self.app, self, self.utils, self.font, device, device_secret[0])
                self.devices_data[device_id] = device_info
                self.devices_list.add(device_info)
        await asyncio.sleep(0.5)
        self.main_box.add(self.devices_list)


    async def updating_devices_list(self):
        while True:
            if not self.main.mobile_toggle:
                return
            devices_list = self.mobile_storage.get_devices()
            connected_devices = self.server.broker.connected_count()
            self.devices_label.text = f"Devices : {len(devices_list)}"
            self.connected_label.text = f"Connected : {connected_devices}"
            if devices_list:
                for device in devices_list:
                    device_id = device[0]
                    device_name = device[1]
                    device_status = device[4]
                    device_timestamp = device[5]
                    taddress, zaddress = self.mobile_storage.get_device_addresses(device_id)
                    tbalance = self.addresses_storage.get_address_balance(taddress)
                    zbalance = self.addresses_storage.get_address_balance(zaddress)
                    if device_id not in self.devices_data:
                        device_secret = self.mobile_storage.get_secret(device_id)
                        device_info = Device(self.app, self, self.utils, self.font, device, device_secret[0])
                        self.devices_data[device_id] = device_info
                        self.devices_list.add(device_info)
                    else:
                        existing_device = self.devices_data[device_id]
                        if device_status and device_status == "on":
                            existing_device.device_icon.image = "images/device_on.png"
                            if existing_device.status != device_status:
                                self.notify.send_note(
                                    title="Device Connected",
                                    text=f"🟢 {device_name}"
                                )
                        else:
                            existing_device.device_icon.image = "images/device_off.png"
                            if existing_device.status != device_status:
                                self.notify.send_note(
                                    title="Device Disconncted",
                                    text=f"🔴 {device_name}"
                                )
                        existing_device.status = device_status
                        if device_timestamp:
                            device_timestamp = datetime.fromtimestamp(device_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            existing_device.device_last_connected._impl.native.Text = f"Recent Request : {device_timestamp}"
                        try:
                            existing_device.transparent_balance.text = f"T : {self.units.format_balance(tbalance)}"
                            existing_device.shielded_balance.text = f"Z : {self.units.format_balance(zbalance)}"
                        except Exception:
                            pass

            await asyncio.sleep(3)


    async def updating_devices_status(self):
        while True:
            if not self.main.mobile_toggle:
                return
            devices_list = self.mobile_storage.get_devices()
            if devices_list:
                now = int(datetime.now(timezone.utc).timestamp())
                for device in devices_list:
                    device_id = device[0]
                    device_status = device[4]
                    device_timestamp = device[5]
                    if device_status and device_status == "on":
                        if device_timestamp and now - device_timestamp > 60:
                            self.mobile_storage.update_device_status(device_id, "off")
            
            await asyncio.sleep(3)


    def add_new_device(self, button):
        devices_list = self.mobile_storage.get_devices()
        if len(devices_list) >= 5:
            return
        add_window = AddDevice(
            self, self.utils, self.units, self.rpc, self.tr, self.font
        )
        add_window._impl.native.ShowDialog(self._impl.native)


    def start_mobile_server(self, button):         
        self.start_server.enabled = False
        host = "127.0.0.1"
        port = self.mobile_port      
        self.server.host = host
        self.server.port = port
        self.server.mobile_storage = self.mobile_storage
        self.server.txs_storage = self.txs_storage
        self.server.addresses_storage = self.addresses_storage
        self.server.messages_storage = self.messages_storage

        result = self.server.start()
        if result is True:
            self.notify.show()
            self.notify.send_note(
                title="Mobile Server",
                text=f"Server started successfully, and listening to {host}:{port}"
            )
            self.update_host_button("start")
        else:
            self.error_dialog(
                title="Error",
                message="Failed to start server. Please check the configuration and try again."
            )
        self.start_server.enabled = True


    def stop_mobile_server(self, button):
        self.server.stop()
        self.notify.hide()
        self.update_host_button("stop")
        self.server.host = None
        self.server.port = None


    def update_host_button(self, option):
        if option == "start":
            self.start_server.text = "Stop"
            self.start_server._impl.native.MouseEnter -= self.start_server_mouse_enter
            self.start_server._impl.native.MouseLeave -= self.start_server_mouse_leave
            self.start_server._impl.native.MouseEnter += self.stop_server_mouse_enter
            self.start_server._impl.native.MouseLeave += self.stop_server_mouse_leave
            self.start_server.on_press = self.stop_mobile_server

        elif option == "stop":
            self.start_server.text = "Host"
            self.start_server._impl.native.MouseEnter -= self.stop_server_mouse_enter
            self.start_server._impl.native.MouseLeave -= self.stop_server_mouse_leave
            self.start_server._impl.native.MouseEnter += self.start_server_mouse_enter
            self.start_server._impl.native.MouseLeave += self.start_server_mouse_leave
            self.start_server.on_press = self.start_mobile_server

    
    def _handle_on_resize(self, sender, event: Sys.EventArgs):
        self._impl.native.MinimumSize = Drawing.Size(500,600)


    def add_button_mouse_enter(self, sender, event):
        self.add_button.style.color = BLACK
        self.add_button.style.background_color = GREENYELLOW

    def add_button_mouse_leave(self, sender, event):
        self.add_button.style.color = GRAY
        self.add_button.style.background_color = rgb(30,33,36)

    def start_server_mouse_enter(self, sender, event):
        self.start_server.style.color = BLACK
        self.start_server.style.background_color = GREENYELLOW

    def start_server_mouse_leave(self, sender, event):
        self.start_server.style.color = GRAY
        self.start_server.style.background_color = rgb(30,33,36)

    def stop_server_mouse_enter(self, sender, event):
        self.start_server.style.color = BLACK
        self.start_server.style.background_color = RED

    def stop_server_mouse_leave(self, sender, event):
        self.start_server.style.color = GRAY
        self.start_server.style.background_color = rgb(30,33,36)

    def window_icon(self, path):
        icon_path = Os.Path.Combine(str(self.app.paths.app), path)
        icon = Drawing.Icon(icon_path)
        return icon


    def close_mobile_window(self, widget):
        self.main.mobile_toggle = None
        self.close()
        self.app.current_window = self.main