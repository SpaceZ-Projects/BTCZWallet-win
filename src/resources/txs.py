
import asyncio
import operator
import json
from datetime import datetime
import webbrowser

from toga import App, Box, Label, Window, ImageView
from ..framework import (
    Table, Command, Color, DockStyle,
    Font, FontStyle, AlignTable, SelectMode,
    BorderStyle, ClipBoard
)
from toga.style.pack import Pack
from toga.colors import rgb, GRAY, WHITE, GREEN, RED, ORANGE
from toga.constants import COLUMN, CENTER, BOLD, ROW, LEFT

from .client import Client
from .utils import Utils
from .notify import NotifyTx



class Txid(Window):
    def __init__(self, txid):
        super().__init__(
            size =(600, 150),
            resizable= False,
            minimizable = False,
            closable=False
        )

        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.txid = txid

        self.updating_txid = None

        self.title = "Transaction Info"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self.main_box = Box(
            style=Pack(
                alignment = CENTER,
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.txid_label = Label(
            text="Transaction ID : ",
            style=Pack(
                font_weight = BOLD,
                text_align = CENTER,
                color = GRAY,
                background_color = rgb(30,33,36),
                padding_left = 20
            )
        )
        self.txid_value = Label(
            text=self.txid,
            style=Pack(
                font_weight = BOLD,
                text_align = CENTER,
                color = WHITE,
                background_color = rgb(30,33,36)
            )
        )
        self.txid_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 2,
                alignment = CENTER
            )
        )

        self.confirmations_label = Label(
            text="Confirmations : ",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                color = GRAY,
                background_color = rgb(30,33,36),
                padding_left = 50
            )
        )
        self.confirmations_value = Label(
            text="",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )
        self.confirmations_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = LEFT
            )
        )

        self.category_label = Label(
            text="Category : ",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                color = GRAY,
                background_color = rgb(30,33,36),
                padding_left = 50
            )
        )
        self.category_value = Label(
            text="",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )
        self.category_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = LEFT
            )
        )

        self.amount_label = Label(
            text="Amount : ",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                color = GRAY,
                background_color = rgb(30,33,36),
                padding_left = 50
            )
        )
        self.amount_value = Label(
            text="",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )
        self.amount_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = LEFT
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
        self.close_button._impl.native.Click += self.close_transaction_info

        self.content = self.main_box

        self.main_box.add(
            self.txid_box,
            self.confirmations_box,
            self.category_box,
            self.amount_box,
            self.close_button
        )
        self.txid_box.add(
            self.txid_label,
            self.txid_value
        )
        self.confirmations_box.add(
            self.confirmations_label,
            self.confirmations_value
        )
        self.category_box.add(
            self.category_label,
            self.category_value
        )
        self.amount_box.add(
            self.amount_label,
            self.amount_value
        )

        self.app.add_background_task(self.update_transaction_info)


    async def update_transaction_info(self, widget):
        if not self.updating_txid:
            self.updating_txid = True
            while True:
                if not self.updating_txid:
                    return
                transaction_info, _= await self.commands.getTransaction(self.txid)
                if isinstance(transaction_info, str):
                    transaction_info = json.loads(transaction_info)
                if transaction_info:
                    category = transaction_info['details'][0]['category']
                    amount = self.utils.format_balance(float(transaction_info['amount']))
                    confirmations = transaction_info['confirmations']
                    if confirmations <= 0:
                        color = RED
                    elif 1 <= confirmations < 6:
                        color = ORANGE
                    else:
                        color = GREEN
                    self.confirmations_value.style.color = color
                    self.confirmations_value.text = confirmations
                    self.category_value.text = category
                    self.amount_value.text = amount
                
                await asyncio.sleep(5)

    def close_button_mouse_enter(self, sender, event):
        self.close_button.image = "images/close_a.png"

    def close_button_mouse_leave(self, sender, event):
        self.close_button.image = "images/close_i.png"

    def close_transaction_info(self, sender, event):
        self.updating_txid = None
        self.close()



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
        self.notify = NotifyTx()
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
            on_scroll=self.on_scroll_table,
            on_double_click=self.transactions_table_double_click
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


    async def update_transactions(self, widget):
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
                            'Txid': txid
                        }
                        self.transactions_data.insert(0, row)
                        self.add_transaction(0, row)
                        notify = NotifyTx()
                        notify.show()
                        notify.send_note(
                            title=f"[{category}] : {amount} BTCZ",
                            text=f"Txid : {txid}",
                            on_click=lambda sender, event:self.on_notification_click(txid)
                        )
                        await asyncio.sleep(5)
                        notify.hide()
            await asyncio.sleep(5)


    def on_notification_click(self, txid):
        self.transactions_info = Txid(txid)
        self.transactions_info._impl.native.ShowDialog()


    def add_transaction(self, index, row):
        if self.no_transaction_toggle:
            self.remove(self.no_transaction)
            self._impl.native.Controls.Add(self.transactions_table)
            self.transactions_table.data_source = self.transactions_data
            self.no_transaction_toggle = None
        else:
            if self.transactions_toggle and not self.no_transaction_toggle:
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


    def transactions_table_double_click(self, sender, event):
        row_index = event.RowIndex
        txid = sender.Rows[row_index].Cells[4].Value
        self.transactions_info = Txid(txid)
        self.transactions_info._impl.native.ShowDialog()

    
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
