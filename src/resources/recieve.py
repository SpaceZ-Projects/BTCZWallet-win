
import asyncio
import json
import webbrowser

from toga import (
    App, Box, Label, ImageView, Window, TextInput
)
from ..framework import (
    Table, DockStyle, BorderStyle, AlignTable,
    FontStyle, Font, Color, Command, ClipBoard,
    RichLabel, ScrollBars, AlignRichLabel, Cursors
)
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD, TOP
from toga.colors import rgb, WHITE, GRAY, YELLOW

from .utils import Utils
from .client import Client
from .storage import Storage


class ImportKey(Window):
    def __init__(self):
        super().__init__(
            size = (600, 150),
            resizable= False,
            minimizable = False,
            closable=False
        )
        
        self.utils = Utils(self.app)
        self.commands = Client(self.app)

        self.title = "Import Key"
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
            text="Please enter your private key for transparent or private addresses.\n(This operation may take up to 10 minutes to complete.)",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 11,
                padding_top = 5
            )
        )
        self.key_input = TextInput(
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 3,
                padding_left = 10
            )
        )
        
        self.import_label = Label(
            text="Import",
            style=Pack(
                color= GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size=12,
                flex = 1
            )
        )
        self.import_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                flex = 1,
                padding = 10
            )
        )
        self.import_button._impl.native.MouseEnter += self.import_button_mouse_enter
        self.import_button._impl.native.MouseLeave += self.import_button_mouse_leave
        self.import_label._impl.native.MouseEnter += self.import_button_mouse_enter
        self.import_label._impl.native.MouseLeave += self.import_button_mouse_leave
        self.import_button._impl.native.Click += self.import_button_click
        self.import_label._impl.native.Click += self.import_button_click

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
                padding_bottom = 10
            )
        )
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave
        self.close_button._impl.native.Click += self.close_import_key

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.input_box,
            self.close_button
        )
        self.input_box.add(
            self.key_input,
            self.import_button
        )
        self.import_button.add(
            self.import_label
        )

    def import_button_click(self, sender, event):
        if not self.key_input.value:
            self.error_dialog(
                "Missing Private Key",
                "Please enter a private key to proceed."
            )
            self.key_input.focus()
            return
        self.key_input.readonly = True
        self.import_button._impl.native.Click -= self.import_button_click
        self.import_label._impl.native.Click -= self.import_button_click
        self.import_button._impl.native.Cursor = Cursors.WAIT
        self.import_label._impl.native.Cursor = Cursors.WAIT
        self.close_button.enabled = False
        self.app.add_background_task(self.import_private_key)


    async def import_private_key(self, widget):
        key = self.key_input.value
        result, _= await self.commands.ImportPrivKey(key)
        if result is not None:
            pass
        else:
            result, _= await self.commands.z_ImportKey(key)
            if result is not None:
                pass
            else:
                self.error_dialog(
                    "Invalid Private Key",
                    "The private key you entered is not valid. Please check the format and try again."
                )
        self.update_import_window()


    def update_import_window(self):
        self.key_input.readonly = False
        self.key_input.value = ""
        self.import_button._impl.native.Click += self.import_button_click
        self.import_label._impl.native.Click += self.import_button_click
        self.import_button._impl.native.Cursor = Cursors.DEFAULT
        self.import_label._impl.native.Cursor = Cursors.DEFAULT
        self.close_button.enabled = True


    def import_button_mouse_enter(self, sender, event):
        self.import_label.style.color = WHITE
        self.import_label.style.background_color = rgb(40,43,48)
        self.import_button.style.background_color = rgb(40,43,48)

    def import_button_mouse_leave(self, sender, event):
        self.import_label.style.color = GRAY
        self.import_label.style.background_color = rgb(30,33,36)
        self.import_button.style.background_color = rgb(30,33,36)

    def close_button_mouse_enter(self, sender, event):
        self.close_button.image = "images/close_a.png"

    def close_button_mouse_leave(self, sender, event):
        self.close_button.image = "images/close_i.png"

    def close_import_key(self, sender, event):
        self.close()


class Recieve(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5)
            )
        )

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.storage = Storage(self.app)
        self.clipboard = ClipBoard()

        self.recieve_toggle = None
        self.transparent_toggle = None
        self.private_toggle = None

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
                flex = 1,
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
            text="Transparent",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
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
            text="Private",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
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
            title="Copy address",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_address,
            icon="images/copy_i.ico",
            mouse_enter=self.copy_address_cmd_mouse_enter,
            mouse_leave=self.copy_address_cmd_mouse_leave
        )
        self.copy_key_cmd = Command(
            title="Copy private key",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_key,
            icon="images/copy_i.ico",
            mouse_enter=self.copy_key_cmd_mouse_enter,
            mouse_leave=self.copy_key_cmd_mouse_leave
        )
        self.explorer_cmd = Command(
            title="View address in explorer",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.open_address_in_explorer,
            icon="images/explorer_i.ico",
            mouse_enter=self.explorer_cmd_mouse_enter,
            mouse_leave=self.explorer_cmd_mouse_leave
        )

        self.addresses_table = Table(
            dockstyle=DockStyle.FILL,
            column_count=1,
            row_visible=False,
            borderstyle=BorderStyle.NONE,
            text_style=FontStyle.BOLD,
            align=AlignTable.MIDCENTER,
            font=Font.SANSSERIF,
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
            ]
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
            text_size=10,
            borderstyle=BorderStyle.NONE,
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            style=FontStyle.BOLD,
            wrap=True,
            readonly=True,
            urls=False,
            dockstyle=DockStyle.TOP,
            text_align=AlignRichLabel.CENTER,
            scrollbars=ScrollBars.NONE,
            maxsize=(0, 35),
            minsize=(0, 35)
        )
        self.address_value_box = Box(
            style=Pack(
                direction = COLUMN,
                height=35,
                padding = (10,50,0,50),
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
                font_weight = BOLD,
                font_size = 14,
                padding = (20,50,0,50) ,
                flex =1,
                alignment = TOP
            )
        )
        self.address_panel = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48)
            )
        )

        
    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.recieve_toggle:
            self.addresses_list._impl.native.Controls.Add(self.addresses_table)
            self.addresses_box.add(
                self.addresses_list_box,
                self.address_info
            )
            self.addresses_list_box.add(
                self.switch_address_box,
                self.addresses_list
            )
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
            self.recieve_toggle = True
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
                'Transparent Addresses': address
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
                    'Private Addresses': address
                }
                addresses.append(row)
        else:
            addresses = [{
                'Private Addresses': ''
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
        balance = self.utils.format_balance(balance)
        self.address_qr.image = qr_image
        self.address_value.text = self.selected_address
        self.address_balance.text = f"Balance : {balance}"

    
    def copy_address(self):
        selected_cells = self.addresses_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 0:
                address = cell.Value
                self.clipboard.copy(address)
                self.main.info_dialog(
                    title="Copied",
                    message="The address has been copied to clipboard.",
                )

    def open_address_in_explorer(self):
        url = "https://explorer.btcz.rocks/address/"
        selected_cells = self.addresses_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 0:
                txid = cell.Value
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
                title="Copied",
                message="The private key has been copied to the clipboard.",
            )


    async def get_transparent_addresses(self):
        addresses_data,_ = await self.commands.ListAddresses()
        addresses_data = json.loads(addresses_data)
        if addresses_data is not None:
            address_items = {address_info for address_info in addresses_data}
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
