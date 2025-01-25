
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
    def __init__(self, app:App, main:Window, notify):
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
        self.notify = notify
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.clipboard = ClipBoard()

        self.transactions_toggle = None
        self.no_transaction_toggle = None
        self.transactions_data = []

        self.transactions_count = 49
        self.transactions_from = 0

        self.copy_txid_cmd = Command(
            title="Copy txid",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_transaction_id,
            icon="images/copy_i.ico",
            mouse_enter=self.copy_txid_cmd_mouse_enter,
            mouse_leave=self.copy_txid_cmd_mouse_leave
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
            title="View txid in explorer",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.open_transaction_in_explorer,
            icon="images/explorer_i.ico",
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
            column_count=5,
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
                4:Color.rgb(40,43,48)
            },
            column_widths={0:75,1:300,2:120,3:150,4:300},
            commands=[
                self.copy_txid_cmd,
                self.copy_address_cmd,
                self.explorer_cmd
            ],
            on_scroll=self.on_scroll_table
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
            if self.transactions_data:
                self._impl.native.Controls.Add(self.transactions_table)
                self.transactions_table.data_source = self.transactions_data
            else:
                await self.no_transactions_found()
            self.transactions_toggle = True


    def create_rows(self, sorted_transactions):
        for data in sorted_transactions:
            address = data.get("address", "Shielded")
            category = data["category"]
            amount = self.utils.format_balance(data["amount"])
            timereceived = data["timereceived"]
            formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
            txid = data["txid"]
            row = {
                'Category': category.upper(),
                'Address': address,
                'Amount': amount,
                'Time': formatted_timereceived,
                'Txid': txid,
            }
            self.transactions_data.append(row)


    async def no_transactions_found(self):
        self.add(self.no_transaction)
        self.no_transaction_toggle = True


    async def update_transactions(self):
        sorted_transactions = await self.get_transactions(
            self.transactions_count,0
        )
        if sorted_transactions:
            self.create_rows(sorted_transactions)
        while True:
            new_transactions = await self.get_transactions(self.transactions_count,0)
            if new_transactions:
                for data in new_transactions:
                    txid = data["txid"]
                    if not any(tx["Txid"] == txid for tx in self.transactions_data):
                        address = data.get("address", "Shielded")
                        category = data["category"]
                        amount = self.utils.format_balance(data["amount"])
                        timereceived = data["timereceived"]
                        formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                        row = {
                            'Category': category.upper(),
                            'Address': address,
                            'Amount': amount,
                            'Time': formatted_timereceived,
                            'Txid': txid,
                        }
                        self.transactions_data.append(row)
                        self.add_transaction(0, row)
                        self.notify.send_note(
                            title=f"[{category}] : {amount} BTCZ",
                            text=f"Txid : {txid}"
                        )
            await asyncio.sleep(5)


    def add_transaction(self, index, row):
        if self.no_transaction_toggle:
            self.remove(self.no_transaction)
            self._impl.native.Controls.Add(self.transactions_table)
            self.no_transaction_toggle = None
        if self.transactions_toggle:
            self.transactions_table.add_row(index=index, row_data=row)
                

    async def get_transactions(self, count, tx_from):
        transactions, _ = await self.commands.listTransactions(
            count, tx_from
        )
        if isinstance(transactions, str):
            transactions_data = json.loads(transactions)
        if transactions_data:
            sorted_transactions = sorted(
                transactions_data,
                key=operator.itemgetter('timereceived'),
                reverse=True
            )
            return sorted_transactions
        return None


    def copy_transaction_id(self):
        selected_cells = self.transactions_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 4:
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
            if cell.ColumnIndex == 4:
                txid = cell.Value
                transaction_url = url + txid
                webbrowser.open(transaction_url)


    def on_scroll_table(self, event):
        rows_visible = self.transactions_table.Size.Height // self.transactions_table.RowTemplate.Height
        last_visible_row = self.transactions_table.FirstDisplayedScrollingRowIndex + rows_visible - 2
        if last_visible_row >= self.transactions_table.RowCount - 1:
            self.transactions_from += 50
            self.app.add_background_task(self.get_transactions_archive)


    async def get_transactions_archive(self, widget):
        sorted_transactions = await self.get_transactions(
            self.transactions_count, self.transactions_from
        )
        if sorted_transactions:
            for data in sorted_transactions:
                address = data.get("address", "Shielded")
                category = data["category"]
                amount = self.utils.format_balance(data["amount"])
                timereceived = data["timereceived"]
                formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                txid = data["txid"]
                row = {
                    'Category': category.upper(),
                    'Address': address,
                    'Amount': amount,
                    'Time': formatted_timereceived,
                    'Txid': txid,
                }
                last_index = self.transactions_table.RowCount
                self.add_transaction(last_index, row)

    
    def copy_txid_cmd_mouse_enter(self):
        self.copy_txid_cmd.icon = "images/copy_a.ico"
        self.copy_txid_cmd.color = Color.BLACK

    def copy_txid_cmd_mouse_leave(self):
        self.copy_txid_cmd.icon = "images/copy_i.ico"
        self.copy_txid_cmd.color = Color.WHITE

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
