
import asyncio
import operator
import json
from datetime import datetime
import webbrowser

from toga import App, Box, Label, Window
from ..framework import (
    Table, Command, Color, DockStyle,
    Font, FontStyle, AlignTable, SelectMode,
    BorderStyle, ClipBoard
)
from toga.style.pack import Pack
from toga.colors import rgb, GRAY
from toga.constants import COLUMN, CENTER, BOLD

from .client import Client
from .utils import Utils

class Transactions(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (1,5,0,5)
            )
        )

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.clipboard = ClipBoard()

        self.transactions_toggle = None
        self.transactions_data = []

        self.transactions_count = 49
        self.transactions_from = 0

        self.copy_txid_cmd = Command(
            title="Copy txid",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_transaction_id,
            icon="images/copy.ico",
            mouse_enter=self.copy_txid_cmd_mouse_enter,
            mouse_leave=self.copy_txid_cmd_mouse_leave
        )
        self.copy_address_cmd = Command(
            title="Copy address",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_address,
            icon="images/copy.ico",
            mouse_enter=self.copy_address_cmd_mouse_enter,
            mouse_leave=self.copy_address_cmd_mouse_leave
        )

        self.explorer_cmd = Command(
            title="View txid in explorer",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.open_transaction_in_explorer,
            icon="images/explorer.ico",
            mouse_enter=self.explorer_cmd_mouse_enter,
            mouse_leave=self.explorer_cmd_mouse_leave
        )

        self.transactions_table = Table(
            dockstyle=DockStyle.FILL,
            background_color=Color.rgb(30,33,36),
            text_color=Color.GRAY,
            cell_color=Color.rgb(30,33,36),
            font=Font.SANSSERIF,
            text_style=FontStyle.BOLD,
            align=AlignTable.MIDCENTER,
            column_count=6,
            row_visible=False,
            gird_color=Color.rgb(30,33,36),
            row_heights=50,
            multiselect=False,
            select_mode=SelectMode.FULLROWSELECT,
            borderstyle=BorderStyle.NONE,
            readonly=True,
            selection_backcolors={
                0:Color.rgb(40,43,48),
                1:Color.rgb(40,43,48),
                2:Color.rgb(66,69,73),
                3:Color.rgb(40,43,48),
                4:Color.rgb(40,43,48),
                5:Color.rgb(40,43,48)
            },
            column_widths={0:75,1:300,2:120,3:150,4:50,5:300},
            commands=[
                self.copy_txid_cmd,
                self.copy_address_cmd,
                self.explorer_cmd
            ]
        )

        self.no_transaction = Label(
            text="No Transactions found.",
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 14,
                padding_top = 40,
                background_color = rgb(40,43,48)
            )
        )

    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.transactions_toggle:
            transactions, _ = await self.commands.listTransactions(
                self.transactions_count, self.transactions_from
            )
            if isinstance(transactions, str):
                transactions_data = json.loads(transactions)
            if transactions_data:
                sorted_transactions = sorted(
                    transactions_data,
                    key=operator.itemgetter('timereceived'),
                    reverse=True
                )
                self._impl.native.Controls.Add(self.transactions_table)
                await self.add_transactions_list(sorted_transactions)
            else:
                await self.no_transactions_found()
            self.transactions_toggle = True

    
    async def add_transactions_list(self, sorted_transactions):
        row_index = 0
        for data in sorted_transactions:
            address = data.get("address", "Shielded")
            category = data["category"]
            amount = self.utils.format_balance(data["amount"])
            confirmations = data["confirmations"]
            timereceived = data["timereceived"]
            formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
            txid = data["txid"]
            row = {
                'Category': category.upper(),
                'Address': address,
                'Amount': amount,
                'Time': formatted_timereceived,
                'Conf.': confirmations,
                'Txid': txid,
            }
            self.transactions_data.append(row)
            row_index += 1
        self.transactions_table.data_source = self.transactions_data
        self.set_categories_colors(row_index)

    def set_categories_colors(self, row_index):
        column_index = 0
        for row_index in range(len(self.transactions_table.rows)):
            cell = self.transactions_table.rows[row_index].Cells[column_index]
            category = self.transactions_data[row_index]["Category"].lower()
            if category == "send":
                category_color = Color.RED
            elif category == "receive":
                category_color = Color.GREEN
            else:
                category_color = Color.WHITE
            cell.Style.ForeColor = category_color
        
        self.transactions_data = []

    async def no_transactions_found(self):
        self.add(self.no_transaction)

    def copy_transaction_id(self):
        selected_cells = self.transactions_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 5:
                txid = cell.Value
                self.clipboard.copy(txid)
                self.main.info_dialog(
                    title="Copied",
                    message="The transaction ID has copied to clipboard.",
                )
                

    def copy_address(self):
        selected_cells = self.transactions_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 1:
                address = cell.Value
                self.clipboard.copy(address)
                self.main.info_dialog(
                    title="Copied",
                    message="The address has copied to clipboard.",
                )
                

    def open_transaction_in_explorer(self):
        url = "https://explorer.btcz.rocks/tx/"
        selected_cells = self.transactions_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 5:
                txid = cell.Value
                transaction_url = url + txid
                webbrowser.open(transaction_url)

    
    def copy_txid_cmd_mouse_enter(self):
        self.copy_txid_cmd.color = Color.BLACK

    def copy_txid_cmd_mouse_leave(self):
        self.copy_txid_cmd.color = Color.WHITE

    def copy_address_cmd_mouse_enter(self):
        self.copy_address_cmd.color = Color.BLACK

    def copy_address_cmd_mouse_leave(self):
        self.copy_address_cmd.color = Color.WHITE

    def explorer_cmd_mouse_enter(self):
        self.explorer_cmd.color = Color.BLACK

    def explorer_cmd_mouse_leave(self):
        self.explorer_cmd.color = Color.WHITE
