
import asyncio
import json
import webbrowser

from toga import App, Box, Label, ImageView, Window
from ..framework import (
    Table, DockStyle, BorderStyle, AlignTable,
    FontStyle, Font, Color, Command, ClipBoard
)
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD, TOP
from toga.colors import rgb, WHITE, GRAY, YELLOW

from .utils import Utils
from .client import Client


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
        self.clipboard = ClipBoard()

        self.recieve_toggle = None
        self.transparent_toggle = None
        self.private_toggle = None

        self.addresses_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                background_color = rgb(30,33,36)
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
                self.explorer_cmd
            ]
        )

        self.address_info = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(30,33,36),
                alignment = CENTER
            )
        )
        self.address_qr = ImageView(
            style=Pack(
                padding_top = 35,
                width = 217,
                height = 217,
                background_color = rgb(30,33,36)
            )
        )
        self.address_value = Label(
            text="",
            style=Pack(
                background_color = rgb(30,33,36),
                color = WHITE,
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                padding_top = 20
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
                self.address_value
            )
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
                'Transparent Address': address
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
                    'Private Address': address
                }
                addresses.append(row)
        else:
            self.address_qr.image = None
            self.address_value.text = None
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
            address = row.Value
            qr_image = self.utils.qr_generate(address)
            address_lines = []
            while len(address) > 35:
                address_lines.append(address[:35])
                address = address[35:]
            if address:
                address_lines.append(address)
            formatted_address = '\n'.join(address_lines)
            self.address_qr.image = qr_image
            self.address_value.text = formatted_address

    
    def copy_address(self):
        selected_cells = self.addresses_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 0:
                address = cell.Value
                self.clipboard.copy(address)
                self.main.info_dialog(
                    title="Copied",
                    message="The address has copied to clipboard.",
                )

    def open_address_in_explorer(self):
        url = "https://explorer.btcz.rocks/address/"
        selected_cells = self.addresses_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 0:
                txid = cell.Value
                transaction_url = url + txid
                webbrowser.open(transaction_url)


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
