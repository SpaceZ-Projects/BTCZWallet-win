
import asyncio
import json
import webbrowser

from toga import App, Box, Label, ImageView, Window
from ..framework import (
    Table, DockStyle, BorderStyle, AlignTable,
    FontStyle, Font, Color, Command, ClipBoard
)
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.colors import rgb, WHITE

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

        self.addresses_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                background_color = rgb(30,33,36)
            )
        )

        self.addresses_list = Box(
            style=Pack(
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
            column_widths={0:427},
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
        self.address_qr = ImageView()
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
                self.addresses_list,
                self.address_info
            )
            self.address_info.add(
                self.address_qr,
                self.address_value
            )
            self.add(
                self.addresses_box
            )
            addresses = []
            transparent_addresses = await self.get_transparent_addresses()
            for address in transparent_addresses:
                row = {
                    'Transparent Address': address
                }
                addresses.append(row)
            self.addresses_table.data_source = addresses
            self.recieve_toggle = True

    
    async def get_transparent_addresses(self):
        addresses_data,_ = await self.commands.ListAddresses()
        addresses_data = json.loads(addresses_data)
        if addresses_data is not None:
            address_items = {address_info for address_info in addresses_data}
        else:
            address_items = []
        return address_items
    

    def _on_selected_address(self, rows):
        for row in rows:
            address = row.Value
            qr_image = self.utils.qr_generate(address)
            self.address_qr.image = qr_image
            self.address_value.text = address

    
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
