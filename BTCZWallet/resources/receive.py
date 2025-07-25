
import json
import webbrowser

from toga import (
    App, Box, Label, ImageView, Window
)
from ..framework import (
    Table, DockStyle, BorderStyle, AlignTable,
    Color, Command, ClipBoard, RichLabel,
    ScrollBars, AlignRichLabel
)
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, TOP
from toga.colors import (
    rgb, WHITE, GRAY, YELLOW
)

from .storage import StorageMessages, StorageMarket


class Receive(Box):
    def __init__(self, app:App, main:Window, settings, utils, units, commands, tr, font):
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
        self.private_toggle = None

        self.app = app
        self.main = main
        self.commands = commands
        self.utils = utils
        self.units = units
        self.settings = settings
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)
        self.storage_market = StorageMarket(self.app)
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
                direction = ROW,
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
                flex = 1
            )
        )
        self.transparent_label._impl.native.Font = self.font.get(11, True)
        self.transparent_button._impl.native.MouseEnter += self.transparent_button_mouse_enter
        self.transparent_label._impl.native.MouseEnter += self.transparent_button_mouse_enter
        self.transparent_button._impl.native.MouseLeave += self.transparent_button_mouse_leave
        self.transparent_label._impl.native.MouseLeave += self.transparent_button_mouse_leave
        self.transparent_button._impl.native.Click += self.transparent_button_click
        self.transparent_label._impl.native.Click += self.transparent_button_click
        self.private_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )
        self.private_label = Label(
            text=self.tr.text("private_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1
            )
        )
        self.private_label._impl.native.Font = self.font.get(11, True)
        self.private_button._impl.native.MouseEnter += self.private_button_mouse_enter
        self.private_label._impl.native.MouseEnter += self.private_button_mouse_enter
        self.private_button._impl.native.MouseLeave += self.private_button_mouse_leave
        self.private_label._impl.native.MouseLeave += self.private_button_mouse_leave
        self.private_button._impl.native.Click += self.private_button_click
        self.private_label._impl.native.Click += self.private_button_click

        self.addresses_list = Box(
            style=Pack(
                direction=COLUMN,
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
            column_count=1,
            row_visible=False,
            borderstyle=BorderStyle.NONE,
            align=AlignTable.MIDCENTER,
            readonly=True,
            column_widths={0:442},
            background_color=Color.rgb(30,33,36),
            text_color=Color.WHITE,
            selection_backcolors={
                0:Color.rgb(40,43,48)
            },
            cell_color=Color.rgb(30,33,36),
            gird_color=Color.rgb(30,33,36),
            row_heights=50,
            on_select=self._on_selected_address,
            commands=[
                self.copy_address_cmd,
                self.copy_key_cmd,
                self.explorer_cmd,
            ],
            font=self.font.get(7, True),
            cell_font=self.font.get(9, True),
            rtl=self.rtl
        )

        self.address_info = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                alignment = CENTER
            )
        )
        self.address_qr = ImageView(
            style=Pack(
                padding_top = 40,
                width = 217,
                height = 217,
                background_color = rgb(30,33,36),
                flex =1
            )
        )
        self.address_value = RichLabel(
            text="",
            borderstyle=BorderStyle.NONE,
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            wrap=True,
            readonly=True,
            urls=False,
            dockstyle=DockStyle.TOP,
            text_align=AlignRichLabel.CENTER,
            scrollbars=ScrollBars.NONE,
            maxsize=(0, 65),
            minsize=(0, 65),
            font=self.font.get(10)
        )
        self.address_value_box = Box(
            style=Pack(
                direction = COLUMN,
                height = 65,
                padding = (5,50,0,50),
                background_color=rgb(40,43,48)
            )
        )

        self.address_balance = Label(
            text="",
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                color = WHITE,
                text_align = CENTER,
                padding = (20,50,0,50) ,
                flex =1,
                alignment = TOP
            )
        )
        self.address_balance._impl.native.Font = self.font.get(12, True)

        self.address_panel = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48)
            )
        )

        
    async def insert_widgets(self, widget):
        if not self.receive_toggle:
            self.addresses_list._impl.native.Controls.Add(self.addresses_table)
            if self.rtl:
                self.addresses_box.add(
                    self.address_info,
                    self.addresses_list_box
                )
            else:
                self.addresses_box.add(
                    self.addresses_list_box,
                    self.address_info
                )
            self.addresses_list_box.add(
                self.switch_address_box,
                self.addresses_list
            )
            if self.rtl:
                self.switch_address_box.add(
                    self.private_button,
                    self.transparent_button
                )
            else:
                self.switch_address_box.add(
                    self.transparent_button,
                    self.private_button
                )
            self.transparent_button.add(
                self.transparent_label
            )
            self.private_button.add(
                self.private_label
            )
            self.address_info.add(
                self.address_qr,
                self.address_value_box,
                self.address_balance,
                self.address_panel
            )
            self.address_value_box._impl.native.Controls.Add(self.address_value)
            self.add(
                self.addresses_box
            )
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
        self.app.add_background_task(self.display_transparent_addresses)

    async def display_transparent_addresses(self, widget):
        addresses = []
        transparent_addresses = await self.get_transparent_addresses()
        for address in transparent_addresses:
            row = {
                self.tr.text("columnt_addresses"): address
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

    def private_button_click(self, sender, event):
        self.clear_buttons()
        self.private_toggle = True
        self.private_button._impl.native.Click -= self.private_button_click
        self.private_label._impl.native.Click -= self.private_button_click
        self.private_label.style.color = rgb(114,137,218)
        self.private_label.style.background_color = rgb(66,69,73)
        self.private_button.style.background_color = rgb(66,69,73)
        self.app.add_background_task(self.display_private_addresses)

    async def display_private_addresses(self, widget):
        addresses = []
        private_addresses = await self.get_private_addresses()
        if private_addresses:
            for address in private_addresses:
                row = {
                    self.tr.text("columnz_addresses"): address
                }
                addresses.append(row)
        else:
            addresses = [{
                self.tr.text("columnz_addresses"): ''
            }]
        self.addresses_table.data_source = addresses

    def private_button_mouse_enter(self, sender, event):
        if self.private_toggle:
            return
        self.private_label.style.color = WHITE
        self.private_label.style.background_color = rgb(66,69,73)
        self.private_button.style.background_color = rgb(66,69,73)

    def private_button_mouse_leave(self, sender, event):
        if self.private_toggle:
            return
        self.private_label.style.color = GRAY
        self.private_label.style.background_color = rgb(30,33,36)
        self.private_button.style.background_color = rgb(30,33,36)

    def clear_buttons(self):
        if self.transparent_toggle:
            self.transparent_label.style.color = GRAY
            self.transparent_label.style.background_color = rgb(30,33,36)
            self.transparent_button.style.background_color = rgb(30,33,36)
            self.transparent_button._impl.native.Click += self.transparent_button_click
            self.transparent_label._impl.native.Click += self.transparent_button_click
            self.transparent_toggle = None

        elif self.private_toggle:
            self.private_label.style.color = GRAY
            self.private_label.style.background_color = rgb(30,33,36)
            self.private_button.style.background_color = rgb(30,33,36)
            self.private_button._impl.native.Click += self.private_button_click
            self.private_label._impl.native.Click += self.private_button_click
            self.private_toggle = None

    def _on_selected_address(self, rows):
        for row in rows:
            self.selected_address = row.Value
            self.app.add_background_task(self.get_address_balance)


    async def get_address_balance(self, widget):
        balance, _ = await self.commands.z_getBalance(self.selected_address)
        if balance is None:
            self.address_qr.image = None
            self.address_value.text = None
            return
        qr_image = self.utils.qr_generate(self.selected_address)
        balance = self.units.format_balance(balance)
        if self.rtl:
            balance = self.units.arabic_digits(balance)
        self.address_qr.image = qr_image
        self.address_value.text = self.selected_address
        text = self.tr.text("address_balance")
        self.address_balance.text = f"{text} {balance}"

    
    def copy_address(self):
        selected_cells = self.addresses_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 0:
                address = cell.Value
                self.clipboard.copy(address)
                self.main.info_dialog(
                    title=self.tr.title("copyaddress_dialog"),
                    message=self.tr.message("copyaddress_dialog"),
                )

    def open_address_in_explorer(self):
        url = "https://explorer.btcz.rocks/address/"
        selected_cells = self.addresses_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 0:
                txid = cell.Value
                if txid.startswith("z"):
                    return
                transaction_url = url + txid
                webbrowser.open(transaction_url)


    def copy_key(self):
        selected_cells = self.addresses_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 0:
                self.address_key = cell.Value
        self.app.add_background_task(self.get_private_key)


    async def get_private_key(self, widget):
        if self.transparent_toggle:
            result, _= await self.commands.DumpPrivKey(self.address_key)
        elif self.private_toggle:
            result, _= await self.commands.z_ExportKey(self.address_key)
        if result is not None:
            self.clipboard.copy(result)
            self.main.info_dialog(
                title=self.tr.title("copykey_dialog"),
                message=self.tr.message("copykey_dialog"),
            )


    async def get_transparent_addresses(self):
        addresses_data,_ = await self.commands.ListAddresses()
        addresses_data = json.loads(addresses_data)
        if addresses_data is not None:
            orders_addresses = self.storage_market.get_orders_addresses()
            filtered_addresses = [addr for addr in addresses_data if addr not in orders_addresses]
            address_items = {address_info for address_info in filtered_addresses}
        else:
            address_items = []
        return address_items
    

    async def get_private_addresses(self):
        addresses_data,_ = await self.commands.z_listAddresses()
        addresses_data = json.loads(addresses_data)
        if addresses_data:
            message_address = self.storage.get_identity("address")
            if message_address:
                address_items = {address_info for address_info in addresses_data if address_info != message_address[0]}
            else:
                address_items = {address_info for address_info in addresses_data}
        else:
            address_items = []
        return address_items
    
    
    async def reload_addresses(self):
        if self.receive_toggle:
            self.addresses_table.data_source.clear()
            if self.transparent_toggle:
                addresses = []
                transparent_addresses = await self.get_transparent_addresses()
                for address in transparent_addresses:
                    row = {
                        self.tr.text("columnt_addresses"): address
                    }
                    addresses.append(row)
                self.addresses_table.data_source = addresses
            elif self.private_toggle:
                addresses = []
                private_addresses = await self.get_private_addresses()
                if private_addresses:
                    for address in private_addresses:
                        row = {
                            self.tr.text("columnz_addresses"): address
                        }
                        addresses.append(row)
                else:
                    addresses = [{
                        self.tr.text("columnz_addresses"): ''
                    }]
                self.addresses_table.data_source = addresses

    

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
