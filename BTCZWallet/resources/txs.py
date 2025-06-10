
import asyncio
import operator
import json
from datetime import datetime
import webbrowser

from toga import App, Box, Label, Window, Button
from ..framework import (
    Table, Command, Color, DockStyle,
    AlignTable, SelectMode, BorderStyle,
    ClipBoard, FlatStyle, CustomFont
)
from toga.style.pack import Pack
from toga.colors import rgb, GRAY, WHITE, GREEN, RED, ORANGE, BLACK
from toga.constants import COLUMN, CENTER, BOLD, ROW

from .client import Client
from .utils import Utils
from .units import Units
from .notify import NotifyTx
from .settings import Settings
from .storage import StorageMessages, StorageTxs
from ..translations import Translations



class Txid(Window):
    def __init__(self, txid):
        super().__init__(
            size =(600, 180),
            resizable= False
        )

        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.commands = Client(self.app)
        self.settings = Settings(self.app)
        self.tr = Translations(self.settings)
        self.txid = txid

        self.updating_txid = None

        self.title = self.tr.title("txinfo_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        self.monda_font = CustomFont()

        self.main_box = Box(
            style=Pack(
                alignment = CENTER,
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.txid_label = Label(
            text=self.tr.text("txid_label"),
            style=Pack(
                text_align = CENTER,
                color = GRAY,
                background_color = rgb(30,33,36),
                padding_left = 20
            )
        )
        self.txid_label._impl.native.Font = self.monda_font.get(9)

        self.txid_value = Label(
            text=self.txid,
            style=Pack(
                text_align = CENTER,
                color = WHITE,
                background_color = rgb(30,33,36)
            )
        )
        self.txid_value._impl.native.Font = self.monda_font.get(9)

        self.txid_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 2,
                alignment = CENTER
            )
        )

        self.confirmations_label = Label(
            text=self.tr.text("confirmations_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48)
            )
        )
        self.confirmations_label._impl.native.Font = self.monda_font.get(9)

        self.confirmations_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.confirmations_value._impl.native.Font = self.monda_font.get(9)
        
        self.confirmations_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (0,50,0,50)
            )
        )

        self.category_label = Label(
            text=self.tr.text("category_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48)
            )
        )
        self.category_label._impl.native.Font = self.monda_font.get(9)

        self.category_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.category_value._impl.native.Font = self.monda_font.get(9)

        self.time_label = Label(
            text=self.tr.text("time_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48)
            )
        )
        self.time_label._impl.native.Font = self.monda_font.get(9)

        self.time_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48)
            )
        )
        self.time_value._impl.native.Font = self.monda_font.get(9)

        self.category_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (0,50,0,50)
            )
        )

        self.amount_label = Label(
            text=self.tr.text("amount_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48)
            )
        )
        self.amount_label._impl.native.Font = self.monda_font.get(9)

        self.amount_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.amount_value._impl.native.Font = self.monda_font.get(9)

        self.fee_label = Label(
            text=self.tr.text("fee_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48)
            )
        )
        self.fee_label._impl.native.Font = self.monda_font.get(9)

        self.fee_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48)
            )
        )
        self.fee_value._impl.native.Font = self.monda_font.get(9)

        self.amount_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (0,50,0,50)
            )
        )
        
        self.close_button = Button(
            text="Close",
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (10,0,10,0),
                width = 100
            ),
            on_press=self.close_transaction_info
        )
        self.close_button._impl.native.Font = self.monda_font.get(9, True)
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

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
            self.category_value,
            self.time_label,
            self.time_value
        )
        self.amount_box.add(
            self.amount_label,
            self.amount_value,
            self.fee_label,
            self.fee_value
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
                    if category == "send":
                        fee = self.units.format_balance(float(transaction_info['fee']))
                    else:
                        fee = "NaN"
                    amount = self.units.format_balance(float(transaction_info['amount']))
                    if self.settings.hidden_balances():
                        amount = "*.********"
                    confirmations = transaction_info['confirmations']
                    timereceived = transaction_info['timereceived']
                    formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                    if confirmations <= 0:
                        color = RED
                    elif 1 <= confirmations < 6:
                        color = ORANGE
                    else:
                        color = GREEN
                    self.confirmations_value.style.color = color
                    self.confirmations_value.text = confirmations
                    self.category_value.text = category
                    self.time_value.text = formatted_timereceived
                    self.amount_value.text = amount
                    self.fee_value.text = fee
                
                await asyncio.sleep(5)

    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)

    def close_transaction_info(self, button):
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
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.clipboard = ClipBoard()
        self.settings = Settings(self.app)
        self.tr = Translations(self.settings)
        self.storagemsgs = StorageMessages(self.app)
        self.storagetxs = StorageTxs(self.app)
        self.notify = NotifyTx()

        self.transactions_toggle = None
        self.no_transaction_toggle = None
        self.no_more_transactions = None
        self.scroll_toggle = None
        self.txid_toggle = None

        self.transactions_count = 50
        self.transactions_from = 0
        self.transactions_ids = []
        self.transactions_data = []

        self.copy_txid_cmd = Command(
            title=self.tr.text("copy_txid_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_transaction_id,
            icon="images/copy_i.ico",
            mouse_enter=self.copy_txid_cmd_mouse_enter,
            mouse_leave=self.copy_txid_cmd_mouse_leave
        )
        self.copy_address_cmd = Command(
            title=self.tr.text("copy_address_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_address,
            icon="images/copy_i.ico",
            mouse_enter=self.copy_address_cmd_mouse_enter,
            mouse_leave=self.copy_address_cmd_mouse_leave
        )

        self.explorer_cmd = Command(
            title=self.tr.text("explorer_cmd"),
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
                0:Color.rgb(15,15,15),
                1:Color.rgb(40,43,48),
                2:Color.rgb(66,69,73),
                3:Color.rgb(40,43,48),
                4:Color.rgb(40,43,48)
            },
            column_widths={0:75,1:330,2:120,3:150,4:300},
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


    async def run_tasks(self, wigdet):
        self.app.add_background_task(self.gather_transparent_transactions)
        await asyncio.sleep(0.5)
        self.app.add_background_task(self.gather_private_transactions)
        await asyncio.sleep(1)
        self.app.add_background_task(self.update_transactions_table)


    async def insert_widgets(self, widget):
        if not self.transactions_toggle:
            sorted_transactions = self.get_transactions(self.transactions_count, self.transactions_from)
            if sorted_transactions:
                self._impl.native.Controls.Add(self.transactions_table)
                self.create_rows(sorted_transactions)
            else:
                self.no_transactions_found()
            self.transactions_toggle = True


    def get_transactions(self, limit, offset):
        transparent_transactions = self.storagetxs.get_transparent_transactions()
        private_transactions = self.storagetxs.get_private_transactions()
        all_transactions = transparent_transactions + private_transactions

        if not all_transactions:
            return []
        sorted_transactions = sorted(
            all_transactions,
            key=operator.itemgetter(5),
            reverse=True
        )
        transactions = sorted_transactions[offset:offset + limit]
        return transactions

    
    def no_transactions_found(self):
        self.add(self.no_transaction)
        self.no_transaction_toggle = True


    def create_rows(self, sorted_transactions):
        
        for data in sorted_transactions:
            tx_type = data[0]
            category = data[1]
            address = data[2]
            if category == "send":
                if tx_type == "private":
                    icon = "images/tx_send_private.png"
                else:
                    icon = "images/tx_send_transparent.png"
            elif category == "receive":
                if tx_type == "private":
                    icon = "images/tx_receive_private.png"
                else:
                    icon = "images/tx_receive_transparent.png"
            elif category == "mining":
                icon = "images/tx_mining.png"
            txid = data[3]
            amount = data[4]
            if self.settings.hidden_balances():
                amount = "*.********"
            timereceived = data[5]
            formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
            row = {
                self.tr.text("column_category"): icon,
                self.tr.text("column_address"): address,
                self.tr.text("column_amount"): amount,
                self.tr.text("column_time"): formatted_timereceived,
                'TxID': txid,
            }
            self.transactions_data.append(row)
        
        self.transactions_table.data_source = self.transactions_data


    def reload_transactions(self):
        if self.transactions_toggle:
            self.transactions_from = 0
            self.no_more_transactions = None
            sorted_transactions = self.get_transactions(self.transactions_count, self.transactions_from)
            if sorted_transactions:
                if self.no_transaction_toggle:
                    self.remove(self.no_transaction)
                    self._impl.native.Controls.Add(self.transactions_table)

                self.transactions_table.data_source.clear()
                self.create_rows(sorted_transactions)


    async def gather_transparent_transactions(self, widget):
        tx_type = "transparent"
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            new_transactions = await self.get_transaparent_transactions(9999, 0)
            if new_transactions:
                stored_transactions = self.storagetxs.get_transparent_transactions("txid")
                mining_options = self.settings.load_mining_options()
                if mining_options:
                    mining_address = mining_options[1]
                for data in new_transactions:
                    txid = data["txid"]
                    if txid not in stored_transactions:
                        address = data.get("address", "Shielded")
                        category = data["category"]
                        amount = self.units.format_balance(data["amount"])
                        timereceived = data["timereceived"]
                        if mining_address and mining_address.startswith('t'):
                            if address == mining_address:
                                category = "mining"
                        self.storagetxs.transparent_transaction(tx_type, category, address, txid, amount, timereceived)

            await asyncio.sleep(10)


    async def get_transaparent_transactions(self, count, tx_from):
        transactions, _ = await self.commands.listTransactions(
            count, tx_from
        )
        if transactions is not None:
            if isinstance(transactions, str):
                transactions_data = json.loads(transactions)
                return transactions_data
        return None


    async def gather_private_transactions(self, widget):
        tx_type = "private"
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            new_transactions = await self.get_private_transactions()
            if new_transactions:
                stored_transactions = self.storagetxs.get_private_transactions("txid")
                mining_options = self.settings.load_mining_options()
                if mining_options:
                    mining_address = mining_options[1]
                for tx_list in new_transactions:
                    for data in tx_list:
                        txid = data['txid']
                        if txid not in stored_transactions:
                            address = data["address"]
                            category = "receive"
                            amount = data["amount"]
                            timereceived = int(datetime.now().timestamp())
                            if mining_address and mining_address.startswith('z'):
                                if address == mining_address:
                                    category = "mining"
                            self.storagetxs.private_transaction(tx_type, category, address, txid, amount, timereceived)

            await asyncio.sleep(10)


    async def get_private_transactions(self):
        transactions_data = []
        addresses_data,_ = await self.commands.z_listAddresses()
        addresses_data = json.loads(addresses_data)
        if addresses_data:
            message_address = self.storagemsgs.get_identity("address")
            if message_address:
                address_items = {address_info for address_info in addresses_data if address_info != message_address[0]}
            else:
                address_items = {address_info for address_info in addresses_data}
        else:
            address_items = []
        for address in address_items:
            listunspent, _= await self.commands.z_listUnspent(address, 0)
            if listunspent:
                listunspent = json.loads(listunspent)
                transactions_data.append(listunspent)

        return transactions_data
    
    

    async def update_transactions_table(self, widget):
        sorted_transactions = self.get_transactions(self.transactions_count, self.transactions_from)
        for data in sorted_transactions:
            txid = data[3]
            self.transactions_ids.append(txid)
        while True:
            sorted_transactions = self.get_transactions(50, 0)
            if sorted_transactions:
                for data in sorted_transactions:
                    txid = data[3]
                    if txid not in self.transactions_ids:
                        data = self.storagetxs.get_transparent_transaction(txid)
                        if data is None:
                            data = self.storagetxs.get_private_transaction(txid)
                        tx_type = data[0]
                        category = data[1]
                        if category == "send":
                            if tx_type == "private":
                                icon = "images/tx_send_private.png"
                            else:
                                icon = "images/tx_send_transparent.png"
                            notify_icon = "images/tx_send.ico"
                        elif category == "receive":
                            if tx_type == "private":
                                icon = "images/tx_receive_private.png"
                            else:
                                icon = "images/tx_receive_transparent.png"
                            notify_icon = "images/tx_receive.ico"
                        elif category == "mining":
                            icon = "images/tx_mining.png"
                            notify_icon = "images/mining_notify.ico"
                        address = data[2]
                        amount = data[4]
                        if self.settings.hidden_balances():
                            amount = "*.********"
                        timereceived = data[5]
                        formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                        row = {
                            self.tr.text("column_category"): icon,
                            self.tr.text("column_address"): address,
                            self.tr.text("column_amount"): amount,
                            self.tr.text("column_time"): formatted_timereceived,
                            'TxID': txid,
                        }
                        self.transactions_ids.append(txid)
                        self.add_transaction(0, row)
                        if self.settings.notification_txs():
                            if self.notify.Visible is False:
                                self.notify.icon = notify_icon
                                self.notify.show()
                                self.notify.send_note(
                                    title=f"[{category}] : {amount} BTCZ",
                                    text=f"TxID : {txid}",
                                    on_click=lambda sender, event:self.on_notification_click(txid)
                                )
                                await asyncio.sleep(5)
                                self.notify.hide()

            await asyncio.sleep(6)

                
    def on_notification_click(self, txid):
        self.transactions_info = Txid(txid)
        self.transactions_info._impl.native.ShowDialog(self.main._impl.native)


    def add_transaction(self, index, row):
        if self.no_transaction_toggle:
            self.remove(self.no_transaction)
            self._impl.native.Controls.Add(self.transactions_table)
            self.transactions_table.data_source = self.transactions_data
            self.no_transaction_toggle = None
        else:
            if self.transactions_toggle and not self.no_transaction_toggle:
                self.transactions_table.add_row(index=index, row_data=row)


    def copy_transaction_id(self):
        selected_cells = self.transactions_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 4:
                txid = cell.Value
                self.clipboard.copy(txid)
                self.main.info_dialog(
                    title=self.tr.title("copytxid_dialog"),
                    message=self.tr.message("copytxid_dialog")
                )
                

    def copy_address(self):
        selected_cells = self.transactions_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 1:
                address = cell.Value
                self.clipboard.copy(address)
                self.main.info_dialog(
                    title=self.tr.title("copyaddress_dialog"),
                    message=self.tr.message("copyaddress_dialog"),
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
        try:
            if self.no_more_transactions or self.scroll_toggle:
                return
            first_row = self.transactions_table.FirstDisplayedScrollingRowIndex
            if first_row < 0:
                return
            rows_visible = self.transactions_table.DisplayedRowCount(True)
            last_visible_row = first_row + rows_visible - 1
            total_rows = self.transactions_table.RowCount
            threshold = 5  
            if last_visible_row >= total_rows - 1 - threshold:
                self.scroll_toggle = True
                self.transactions_from += 50
                self.app.add_background_task(self.get_transactions_archive)
        except Exception as e:
            print(f"Error: {e}")



    async def get_transactions_archive(self, widget):
        try:
            sorted_transactions = self.get_transactions(self.transactions_count, self.transactions_from)
            if not sorted_transactions:
                self.no_more_transactions = True
                return
            for data in sorted_transactions:
                tx_type = data[0]
                category = data[1]
                if category == "send":
                    if tx_type == "private":
                        icon = "images/tx_send_private.png"
                    else:
                        icon = "images/tx_send_transparent.png"
                elif category == "receive":
                    if tx_type == "private":
                        icon = "images/tx_receive_private.png"
                    else:
                        icon = "images/tx_receive_transparent.png"
                elif category == "mining":
                    icon = "images/tx_mining.png"
                address = data[2]
                txid = data[3]
                amount = data[4]
                if self.settings.hidden_balances():
                    amount = "*.********"
                timereceived = data[5]
                formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                row = {
                    self.tr.text("column_category"): icon,
                    self.tr.text("column_address"): address,
                    self.tr.text("column_amount"): amount,
                    self.tr.text("column_time"): formatted_timereceived,
                    'TxID': txid,
                }
                last_index = self.transactions_table.RowCount
                self.add_transaction(last_index, row)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.scroll_toggle = None


    def transactions_table_double_click(self, sender, event):
        row_index = event.RowIndex
        txid = sender.Rows[row_index].Cells[4].Value
        self.transactions_info = Txid(txid)
        self.transactions_info._impl.native.ShowDialog(self.main._impl.native)

    
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
