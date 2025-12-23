
import webbrowser

from toga import (
    App, Box, Label, ImageView, Window, Button
)
from ..framework import (
    Table, DockStyle, BorderStyle, AlignTable,
    Color, Command, ClipBoard, SelectMode, FlatStyle,
    Keys
)
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, TOP
from toga.colors import (
    rgb, WHITE, GRAY, YELLOW, RED, BLACK
)

from .storage import StorageAddresses, StorageMessages, StorageMobile


class QRView(Window):
    def __init__(self, main:Window, utils, font, address):
        super().__init__(
            resizable=False
        )

        self.main= main
        self.utils = utils
        self.font = font
        self.address = address
        
        self.title = "QRCode"
        self.size = (450,400)
        position_center = self.utils.window_center_to_parent(self.main, self)
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
                alignment = CENTER
            )
        )

        self.qr_view = ImageView(
            style=Pack(
                background_color = rgb(30,33,36),
                width = 275,
                height = 275,
                padding = (30,0,0,0)
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
            on_press=self.close_qr_view
        )
        self.close_button._impl.native.Font = self.font.get(9, True)
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.qr_box,
            self.close_button
        )
        self.qr_box.add(
            self.qr_view
        )
        
        qr_image = self.utils.qr_generate(self.address)
        if qr_image:
            self.qr_view.image = qr_image

    
    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)

    def close_qr_view(self, button):
        self.close()
        self.app.current_window = self.main



class Receive(Box):
    def __init__(self, app:App, main:Window, settings, utils, units, rpc, tr, font):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5)
            )
        )

        self.receive_toggle = None
        self.transparent_toggle = None
        self.shielded_toggle = None
        self.selected_address = None

        self.app = app
        self.main = main
        self.rpc = rpc
        self.utils = utils
        self.units = units
        self.settings = settings
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)
        self.addresses_storage = StorageAddresses(self.app)
        self.mobile_storage = StorageMobile(self.app)
        self.clipboard = ClipBoard()

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.addresses_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                background_color = rgb(40,43,48)
            )
        )

        self.addresses_list_box = Box(
            style=Pack(
                direction=COLUMN,
                flex = 1.5,
                background_color = rgb(30,33,36)
            )
        )

        self.switch_address_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = TOP,
                height = 35
            )
        )

        self.transparent_button = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )
        self.transparent_label = Label(
            text=self.tr.text("transparent_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding = (0,0,3,0)
            )
        )
        self.transparent_label._impl.native.Font = self.font.get(11, True)
        self.transparent_button._impl.native.MouseEnter += self.transparent_button_mouse_enter
        self.transparent_label._impl.native.MouseEnter += self.transparent_button_mouse_enter
        self.transparent_button._impl.native.MouseLeave += self.transparent_button_mouse_leave
        self.transparent_label._impl.native.MouseLeave += self.transparent_button_mouse_leave
        self.transparent_button._impl.native.Click += self.transparent_button_click
        self.transparent_label._impl.native.Click += self.transparent_button_click

        self.transparent_line = Box(
            style=Pack(
                background_color = rgb(30,33,36),
                height = 2
            )
        )

        self.shielded_button = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )
        self.shielded_label = Label(
            text=self.tr.text("shielded_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding = (0,0,3,0)
            )
        )
        self.shielded_label._impl.native.Font = self.font.get(11, True)
        self.shielded_button._impl.native.MouseEnter += self.shielded_button_mouse_enter
        self.shielded_label._impl.native.MouseEnter += self.shielded_button_mouse_enter
        self.shielded_button._impl.native.MouseLeave += self.shielded_button_mouse_leave
        self.shielded_label._impl.native.MouseLeave += self.shielded_button_mouse_leave
        self.shielded_button._impl.native.Click += self.shielded_button_click
        self.shielded_label._impl.native.Click += self.shielded_button_click

        self.shielded_line = Box(
            style=Pack(
                background_color = rgb(30,33,36),
                height = 2
            )
        )

        self.addresses_list = Box(
            style=Pack(
                direction=COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.copy_address_cmd = Command(
            title=self.tr.text("copy_address_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_address,
            icon="images/copy_i.ico",
            mouse_enter=self.copy_address_cmd_mouse_enter,
            mouse_leave=self.copy_address_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.send_from_cmd = Command(
            title="Send from address",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.send_from_address,
            icon="images/send_i.ico",
            mouse_enter=self.send_from_cmd_mouse_enter,
            mouse_leave=self.send_from_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.copy_key_cmd = Command(
            title=self.tr.text("copy_key_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_key,
            icon="images/copy_i.ico",
            mouse_enter=self.copy_key_cmd_mouse_enter,
            mouse_leave=self.copy_key_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.explorer_cmd = Command(
            title=self.tr.text("exploreraddress_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.open_address_in_explorer,
            icon="images/explorer_i.ico",
            mouse_enter=self.explorer_cmd_mouse_enter,
            mouse_leave=self.explorer_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )

        self.addresses_table = Table(
            dockstyle=DockStyle.FILL,
            select_mode=SelectMode.FULLROWSELECT,
            column_count=4,
            row_visible=False,
            borderstyle=BorderStyle.NONE,
            align=AlignTable.MIDCENTER,
            readonly=True,
            column_widths={0:400,1:150},
            background_color=Color.rgb(30,33,36),
            text_color=Color.WHITE,
            selection_backcolors={
                0:Color.rgb(40,43,48),
                1:Color.rgb(66,69,73),
                2:Color.rgb(40,43,48),
                3:Color.rgb(40,43,48)
            },
            cell_color=Color.rgb(30,33,36),
            gird_color=Color.rgb(30,33,36),
            row_heights=50,
            on_select=self._on_selected_address,
            on_double_click=self.show_qr_code,
            commands=[
                self.copy_address_cmd,
                self.send_from_cmd,
                self.copy_key_cmd,
                self.explorer_cmd,
            ],
            font=self.font.get(7, True),
            cell_font=self.font.get(9, True),
            rtl=self.rtl
        )
        self.addresses_table.KeyDown += self.table_keydown

        self.addresses_list._impl.native.Controls.Add(self.addresses_table)
        self.addresses_box.add(
            self.addresses_list_box
        )
        self.addresses_list_box.add(
            self.switch_address_box,
            self.addresses_list
        )
        if self.rtl:
            self.switch_address_box.add(
                self.shielded_button,
                self.transparent_button
            )
        else:
            self.switch_address_box.add(
                self.transparent_button,
                self.shielded_button
            )
        self.transparent_button.add(
            self.transparent_label,
            self.transparent_line
        )
        self.shielded_button.add(
            self.shielded_label,
            self.shielded_line
        )
        self.add(
            self.addresses_box
        )

        
    def insert_widgets(self):
        if not self.receive_toggle:
            self.receive_toggle = True
            self.transparent_button_click(None, None)
    

    def transparent_button_click(self, sender, event):
        self.clear_buttons()
        self.transparent_toggle = True
        self.transparent_button._impl.native.Click -= self.transparent_button_click
        self.transparent_label._impl.native.Click -= self.transparent_button_click
        self.transparent_label.style.color = YELLOW
        self.transparent_label.style.background_color = rgb(66,69,73)
        self.transparent_button.style.background_color = rgb(66,69,73)
        self.transparent_line.style.background_color = YELLOW
        self.display_transparent_addresses()

    def display_transparent_addresses(self):
        addresses = []
        devices_addresses = self.mobile_storage.get_addresses_list("taddress")
        transparent_addresses = self.addresses_storage.get_addresses(address_type="transparent")
        transparent_addresses.sort(key=lambda x: (x[3] is None, x[3] or 0), reverse=True)
        for data in transparent_addresses:
            address = data[2]
            balance = data[3]
            change = data[1]
            mobile = ""
            if address in devices_addresses:
                mobile = "✔"
            if change:
                change = "✔"
            row = {
                self.tr.text("columnt_addresses"): address,
                "Balances": self.units.format_balance(balance),
                "Change": change,
                "Mobile": mobile
            }
            addresses.append(row)
        self.addresses_table.data_source = addresses

    def transparent_button_mouse_enter(self, sender, event):
        if self.transparent_toggle:
            return
        self.transparent_label.style.color = WHITE
        self.transparent_label.style.background_color = rgb(66,69,73)
        self.transparent_button.style.background_color = rgb(66,69,73)

    def transparent_button_mouse_leave(self, sender, event):
        if self.transparent_toggle:
            return
        self.transparent_label.style.color = GRAY
        self.transparent_label.style.background_color = rgb(30,33,36)
        self.transparent_button.style.background_color = rgb(30,33,36)

    def shielded_button_click(self, sender, event):
        self.clear_buttons()
        self.shielded_toggle = True
        self.shielded_button._impl.native.Click -= self.shielded_button_click
        self.shielded_label._impl.native.Click -= self.shielded_button_click
        self.shielded_label.style.color = rgb(114,137,218)
        self.shielded_label.style.background_color = rgb(66,69,73)
        self.shielded_button.style.background_color = rgb(66,69,73)
        self.shielded_line.style.background_color = rgb(114,137,218)
        self.display_shielded_addresses()

    def display_shielded_addresses(self):
        addresses = []
        devices_addresses = self.mobile_storage.get_addresses_list("zaddress")
        transparent_addresses = self.addresses_storage.get_addresses(address_type="shielded")
        transparent_addresses.sort(key=lambda x: (x[3] is None, x[3] or 0), reverse=True)
        for data in transparent_addresses:
            address = data[2]
            balance = data[3]
            mobile = ""
            if address in devices_addresses:
                mobile = "✔"
            row = {
                self.tr.text("columnz_addresses"): address,
                "Balances": self.units.format_balance(balance),
                "Mobile": mobile
            }
            addresses.append(row)
        self.addresses_table.data_source = addresses

    def shielded_button_mouse_enter(self, sender, event):
        if self.shielded_toggle:
            return
        self.shielded_label.style.color = WHITE
        self.shielded_label.style.background_color = rgb(66,69,73)
        self.shielded_button.style.background_color = rgb(66,69,73)

    def shielded_button_mouse_leave(self, sender, event):
        if self.shielded_toggle:
            return
        self.shielded_label.style.color = GRAY
        self.shielded_label.style.background_color = rgb(30,33,36)
        self.shielded_button.style.background_color = rgb(30,33,36)

    def clear_buttons(self):
        if self.transparent_toggle:
            self.transparent_label.style.color = GRAY
            self.transparent_label.style.background_color = rgb(30,33,36)
            self.transparent_button.style.background_color = rgb(30,33,36)
            self.transparent_line.style.background_color = rgb(30,33,36)
            self.transparent_button._impl.native.Click += self.transparent_button_click
            self.transparent_label._impl.native.Click += self.transparent_button_click
            self.transparent_toggle = None

        elif self.shielded_toggle:
            self.shielded_label.style.color = GRAY
            self.shielded_label.style.background_color = rgb(30,33,36)
            self.shielded_button.style.background_color = rgb(30,33,36)
            self.shielded_line.style.background_color = rgb(30,33,36)
            self.shielded_button._impl.native.Click += self.shielded_button_click
            self.shielded_label._impl.native.Click += self.shielded_button_click
            self.shielded_toggle = None


    def _on_selected_address(self, rows):
        for cell in rows:
            row = cell.OwningRow
            self.selected_address = row.Cells[0].Value


    def show_qr_code(self, sender, event):
        qr_view = QRView(self.main, self.utils, self.font, self.selected_address)
        qr_view._impl.native.ShowDialog(self.main._impl.native)

    
    def copy_address(self):
        if self.selected_address:
            self.clipboard.copy(self.selected_address)
            self.main.info_dialog(
                title=self.tr.title("copyaddress_dialog"),
                message=self.tr.message("copyaddress_dialog"),
            )

    def send_from_address(self):
        if self.selected_address and not self.main.send_page.operation_toggle:
            address_selection = self.main.send_page.address_selection
            self.main.send_button_click(None)
            if self.selected_address.startswith("t"):
                self.main.send_page.transparent_button_click(None, None)
            elif self.selected_address.startswith("z"):
                self.main.send_page.shielded_button_click(None, None)
            address_selection.value = address_selection.items.find(self.selected_address)

    def open_address_in_explorer(self):
        if self.selected_address:
            if self.selected_address.startswith("z"):
                return
        url = "https://explorer.btcz.rocks/address/"
        transaction_url = url + self.selected_address
        webbrowser.open(transaction_url)


    def copy_key(self):
        if self.selected_address:
            self.app.loop.create_task(self.get_private_key())


    async def get_private_key(self):
        if self.transparent_toggle:
            result, _= await self.rpc.DumpPrivKey(self.selected_address)
        elif self.shielded_toggle:
            result, _= await self.rpc.z_ExportKey(self.selected_address)
        if result is not None:
            self.clipboard.copy(result)
            self.main.info_dialog(
                title=self.tr.title("copykey_dialog"),
                message=self.tr.message("copykey_dialog"),
            )

    def table_keydown(self, sender, e):
        if e.KeyCode == Keys.F5:
            self.reload_addresses()
    
    
    def reload_addresses(self):
        if self.receive_toggle:
            self.addresses_table.data_source.clear()
            if self.transparent_toggle:
                self.display_transparent_addresses()
            elif self.shielded_toggle:
                self.display_shielded_addresses()


    def send_from_cmd_mouse_enter(self):
        self.send_from_cmd.icon = "images/send_a.ico"
        self.send_from_cmd.color = Color.BLACK

    def send_from_cmd_mouse_leave(self):
        self.send_from_cmd.icon = "images/send_i.ico"
        self.send_from_cmd.color = Color.WHITE

    def copy_address_cmd_mouse_enter(self):
        self.copy_address_cmd.icon = "images/copy_a.ico"
        self.copy_address_cmd.color = Color.BLACK

    def copy_address_cmd_mouse_leave(self):
        self.copy_address_cmd.icon = "images/copy_i.ico"
        self.copy_address_cmd.color = Color.WHITE

    def explorer_cmd_mouse_enter(self):
        self.explorer_cmd.icon = "images/explorer_a.ico"
        self.explorer_cmd.color = Color.BLACK

    def explorer_cmd_mouse_leave(self):
        self.explorer_cmd.icon = "images/explorer_i.ico"
        self.explorer_cmd.color = Color.WHITE

    def copy_key_cmd_mouse_enter(self):
        self.copy_key_cmd.icon = "images/copy_a.ico"
        self.copy_key_cmd.color = Color.BLACK

    def copy_key_cmd_mouse_leave(self):
        self.copy_key_cmd.icon = "images/copy_i.ico"
        self.copy_key_cmd.color = Color.WHITE
