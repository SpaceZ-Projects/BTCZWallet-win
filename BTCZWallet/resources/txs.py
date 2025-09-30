
import asyncio
import operator
from datetime import datetime
import webbrowser

from toga import App, Box, Label, Window, Button
from ..framework import (
    Table, Command, Color, DockStyle,
    AlignTable, SelectMode, BorderStyle,
    ClipBoard, FlatStyle, Keys
)
from toga.style.pack import Pack
from toga.colors import rgb, GRAY, WHITE, GREEN, RED, ORANGE, BLACK
from toga.constants import COLUMN, CENTER, BOLD, ROW

from .storage import StorageMessages, StorageTxs, StorageMobile



class Txid(Window):
    def __init__(self, main:Window, txid, address, settings, utils, units, rpc, tr, font):
        super().__init__(
            size =(600, 180),
            resizable= False
        )
        
        self.main = main
        self.updating_txid = None
        self.txid = txid
        self.address = address

        self.utils = utils
        self.units = units
        self.rpc = rpc
        self.settings = settings
        self.tr = tr
        self.font = font

        self.title = self.tr.title("txinfo_window")
        position_center = self.utils.window_center_to_parent(self.main, self)
        self.position = position_center
        self._impl.native.ControlBox = False

        self.storagetxs = StorageTxs(self.app)

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

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
                padding = self.tr.padding("txid_label")
            )
        )
        self.txid_label._impl.native.Font = self.font.get(9)

        self.txid_value = Label(
            text=self.txid,
            style=Pack(
                text_align = CENTER,
                color = WHITE,
                background_color = rgb(30,33,36)
            )
        )
        self.txid_value._impl.native.Font = self.font.get(9)

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
        self.confirmations_label._impl.native.Font = self.font.get(9)

        self.confirmations_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = self.tr.align("confirmations_value"),
                flex = 1
            )
        )
        self.confirmations_value._impl.native.Font = self.font.get(9)
        
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
        self.category_label._impl.native.Font = self.font.get(9)

        self.category_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = self.tr.align("category_value"),
                flex = 1
            )
        )
        self.category_value._impl.native.Font = self.font.get(9)

        self.time_label = Label(
            text=self.tr.text("time_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48)
            )
        )
        self.time_label._impl.native.Font = self.font.get(9)

        self.time_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48)
            )
        )
        self.time_value._impl.native.Font = self.font.get(9)

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
        self.amount_label._impl.native.Font = self.font.get(9)

        self.amount_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = self.tr.align("amount_value"),
                flex = 1
            )
        )
        self.amount_value._impl.native.Font = self.font.get(9)

        self.fee_label = Label(
            text=self.tr.text("fee_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48)
            )
        )
        self.fee_label._impl.native.Font = self.font.get(9)

        self.fee_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48)
            )
        )
        self.fee_value._impl.native.Font = self.font.get(9)

        self.amount_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (0,50,0,50)
            )
        )
        
        self.close_button = Button(
            text=self.tr.text("close_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (10,0,10,0),
                width = 100
            ),
            on_press=self.close_transaction_info
        )
        self.close_button._impl.native.Font = self.font.get(self.tr.size("close_button"), True)
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
        if self.rtl:
            self.txid_box.add(
                self.txid_value,
                self.txid_label
            )
            self.confirmations_box.add(
                self.confirmations_value,
                self.confirmations_label
            )
            self.category_box.add(
                self.time_value,
                self.time_label,
                self.category_value,
                self.category_label
            )
            self.amount_box.add(
                self.fee_value,
                self.fee_label,
                self.amount_value,
                self.amount_label
            )
        else:
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

        asyncio.create_task(self.update_transaction_info())


    async def update_transaction_info(self):
        if not self.updating_txid:
            self.updating_txid = True
            while True:
                if not self.updating_txid:
                    return
                if self.address.startswith("z"):
                    transaction_info = self.storagetxs.get_transaction(self.txid)
                    tx_type, category, address, txid, amount_val, blocks, fee_val, timestamp = transaction_info

                    amount = self.units.format_balance(amount_val)
                    fee = self.units.format_balance(fee_val) if category == "send" else "NaN"

                    if self.rtl:
                        amount = self.units.arabic_digits(amount)
                        if category == "send":
                            fee = self.units.arabic_digits(fee)
                            category = self.tr.text("category_send")
                        else:
                            category = self.tr.text("category_receive")

                    if self.settings.hidden_balances():
                        amount = "*.********"

                    confirmations = 0
                    if blocks > 0:
                        if tx_type == "shielded":
                            confirmations = self.main.home_page.current_blocks - blocks
                        else:
                            confirmations = (self.main.home_page.current_blocks - blocks) + 1
                    if confirmations <= 0:
                        color = RED
                    elif 1 <= confirmations < 6:
                        color = ORANGE
                    else:
                        color = GREEN

                    formatted_timereceived = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    if self.rtl:
                        formatted_timereceived = self.units.arabic_digits(formatted_timereceived)
                        confirmations = self.units.arabic_digits(str(confirmations))
                else:
                    transaction_info,_ = await self.rpc.getTransaction(self.txid)
                    details = transaction_info.get('details', [])
                    if details:
                        category = details[0]['category']
                    else:
                        category = "unknown"

                    if category == "send":
                        fee = self.units.format_balance(float(transaction_info.get('fee', 0)))
                        if self.rtl:
                            category = self.tr.text("category_send")
                            fee = self.units.arabic_digits(fee)
                    else:
                        category = self.tr.text("category_receive")
                        fee = "NaN"

                    amount = self.units.format_balance(float(transaction_info.get('amount', 0)))
                    if self.rtl:
                        amount = self.units.arabic_digits(amount)
                    if self.settings.hidden_balances():
                        amount = "*.********"

                    confirmations = transaction_info.get('confirmations', 0)
                    if confirmations <= 0:
                        color = RED
                    elif 1 <= confirmations < 6:
                        color = ORANGE
                    else:
                        color = GREEN

                    timereceived = transaction_info.get('timereceived', 0)
                    formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                    if self.rtl:
                        confirmations = self.units.arabic_digits(str(confirmations))
                        formatted_timereceived = self.units.arabic_digits(formatted_timereceived)
                    

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
        self.app.current_window = self.main



class Transactions(Box):
    def __init__(self, app:App, main:Window, settings, utils, units, rpc, tr, font):
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
        self.rpc = rpc
        self.utils = utils
        self.units = units
        self.settings = settings
        self.tr = tr
        self.font = font

        self.storagemsgs = StorageMessages(self.app)
        self.storagetxs = StorageTxs(self.app)
        self.storage_mobile = StorageMobile(self.app)
        self.clipboard = ClipBoard()
        self.notify = self.main.notify

        self.transactions_toggle = None
        self.no_transaction_toggle = None
        self.no_more_transactions = None
        self.scroll_toggle = None
        self.txid_toggle = None

        self.transactions_count = 50
        self.transactions_from = 0
        self.transactions_ids = []
        self.transactions_data = []

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.copy_txid_cmd = Command(
            title=self.tr.text("copy_txid_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.copy_transaction_id,
            icon="images/copy_i.ico",
            mouse_enter=self.copy_txid_cmd_mouse_enter,
            mouse_leave=self.copy_txid_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
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

        self.explorer_cmd = Command(
            title=self.tr.text("explorer_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.open_transaction_in_explorer,
            icon="images/explorer_i.ico",
            mouse_enter=self.explorer_cmd_mouse_enter,
            mouse_leave=self.explorer_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )

        self.transactions_table = Table(
            dockstyle=DockStyle.FILL,
            background_color=Color.rgb(30,33,36),
            text_color=Color.GRAY,
            cell_color=Color.rgb(30,33,36),
            align=AlignTable.MIDCENTER,
            column_count=5,
            row_visible=False,
            column_visible=False,
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
            on_double_click=self.transactions_table_double_click,
            font=self.font.get(7, True),
            cell_font=self.font.get(9, True),
            rtl=self.rtl
        )
        self.transactions_table.KeyDown += self.table_keydown

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


    async def run_tasks(self):
        self.app.loop.create_task(self.gather_transparent_transactions())
        await asyncio.sleep(0.5)
        self.app.loop.create_task(self.update_unconfirmed_transactions())
        await asyncio.sleep(0.5)
        self.app.loop.create_task(self.gather_shielded_transactions())
        await asyncio.sleep(1)
        self.app.loop.create_task(self.update_transactions_table())


    def insert_widgets(self):
        if not self.transactions_toggle:
            sorted_transactions = self.get_transactions(self.transactions_count, self.transactions_from)
            if sorted_transactions:
                self._impl.native.Controls.Add(self.transactions_table)
                self.create_rows(sorted_transactions)
            else:
                self.no_transactions_found()
            self.transactions_toggle = True


    def get_transactions(self, limit, offset):
        transactions_list = self.storagetxs.get_transactions()
        if not transactions_list:
            return []
        sorted_transactions = sorted(
            transactions_list,
            key=operator.itemgetter(7),
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
                if tx_type == "shielded":
                    icon = "images/tx_send_shielded.png"
                else:
                    icon = "images/tx_send_transparent.png"
            elif category == "receive":
                if tx_type == "shielded":
                    icon = "images/tx_receive_shielded.png"
                else:
                    icon = "images/tx_receive_transparent.png"

            txid = data[3]
            amount = data[4]
            if self.settings.hidden_balances():
                amount = "*.********"
            timereceived = data[7]
            formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
            if self.rtl:
                amount = self.units.arabic_digits(str(amount))
                formatted_timereceived = self.units.arabic_digits(formatted_timereceived)
            row = {
                self.tr.text("column_category"): icon,
                self.tr.text("column_address"): address,
                self.tr.text("column_amount"): amount,
                self.tr.text("column_time"): formatted_timereceived,
                'TxID': txid,
            }
            self.transactions_data.append(row)
        
        self.transactions_table.data_source = self.transactions_data


    def table_keydown(self, sender, e):
        if e.KeyCode == Keys.F5:
            self.reload_transactions()


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


    async def gather_transparent_transactions(self):
        self.app.console.event_log(f"✔: Transparent transactions")
        tx_type = "transparent"
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            new_transactions = await self.get_transaparent_transactions(9999, 0)
            if new_transactions:
                stored_transactions = self.storagetxs.get_transactions(True, "transparent")
                for data in new_transactions:
                    txid = data["txid"]
                    address = data.get("address", "Shielded")
                    category = data["category"]
                    amount = data["amount"]
                    timereceived = data["timereceived"]
                    vout = data["vout"]
                    fee = 0
                    if "fee" in data:
                        fee = data["fee"]
                    if txid not in stored_transactions and vout == 0:
                        if "blockhash" not in data:
                            blocks = 0
                            self.storagetxs.insert_transaction(tx_type, category, address, txid, amount, blocks, fee, timereceived)
                        else:
                            blockhash = data["blockhash"]
                            await self.get_block_height(blockhash, tx_type, category, address, txid, amount, fee, timereceived)
                        
            await asyncio.sleep(10)
            


    async def update_unconfirmed_transactions(self):
        self.app.console.event_log(f"✔: Unconfirmed transactions")
        while True:
            unconfirmed_transactions = self.storagetxs.get_unconfirmed_transactions()
            if unconfirmed_transactions:
                for txid in unconfirmed_transactions:
                    result,_ = await self.rpc.getTransaction(txid)
                    if "blockhash" in result:
                        blockhash = result["blockhash"]
                        result,_ = await self.rpc.getBlock(blockhash)
                        if result:
                            height = result.get("height")
                            self.storagetxs.update_transaction(txid, height)

            await asyncio.sleep(10)



    async def get_block_height(self, blockhash, tx_type, category, address, txid, amount, fee, timereceived):
        result,_ = await self.rpc.getBlock(blockhash)
        if result:
            height = result.get("height")
            self.storagetxs.insert_transaction(tx_type, category, address, txid, amount, height, fee, timereceived)


    async def get_transaparent_transactions(self, count, tx_from):
        transactions,_ = await self.rpc.listTransactions(
            count, tx_from
        )
        if transactions:
            return transactions
        return None


    async def gather_shielded_transactions(self):
        self.app.console.event_log(f"✔: Shielded transactions")
        tx_type = "shielded"
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            new_transactions = await self.get_shielded_transactions()
            if new_transactions:
                stored_transactions = self.storagetxs.get_transactions(True, "shielded")
                for tx_list in new_transactions:
                    for data in tx_list:
                        txid = data['txid']
                        confirmations = data["confirmations"]
                        address = data["address"]
                        category = "receive"
                        amount = data["amount"]
                        if confirmations > 0:
                            blocks = self.main.home_page.current_blocks - confirmations
                        elif confirmations == 0:
                            blocks = self.main.home_page.current_blocks
                        if txid not in stored_transactions:
                            await self.get_block_timestamp(blocks, tx_type, category, address, txid, amount)
                            
            await asyncio.sleep(10)


    async def get_block_timestamp(self, height, tx_type, category, address, txid, amount):
        result,_ = await self.rpc.getBlock(height)
        if result:
            timereceived = result.get("time")
            self.storagetxs.insert_transaction(tx_type, category, address, txid, amount, height, None, timereceived)


    async def get_shielded_transactions(self):
        transactions_data = []
        addresses_data,_ = await self.rpc.z_listAddresses()
        if addresses_data:
            message_address = self.storagemsgs.get_identity("address")
            if message_address:
                address_items = {address_info for address_info in addresses_data if address_info != message_address[0]}
            else:
                address_items = {address_info for address_info in addresses_data}
        else:
            address_items = []
        for address in address_items:
            listunspent,_ = await self.rpc.z_listUnspent(address, 0)
            if listunspent:
                transactions_data.append(listunspent)

        return transactions_data
    
    

    async def update_transactions_table(self):
        sorted_transactions = self.get_transactions(self.transactions_count, self.transactions_from)
        for data in sorted_transactions:
            txid = data[3]
            self.transactions_ids.append(txid)
        self.app.console.event_log(f"✔: Transactions list")
        while True:
            sorted_transactions = self.get_transactions(50, 0)
            if sorted_transactions:
                for data in sorted_transactions:
                    txid = data[3]
                    if txid not in self.transactions_ids:
                        data = self.storagetxs.get_transaction(txid)
                        tx_type = data[0]
                        category = data[1]
                        if category == "send":
                            if tx_type == "shielded":
                                icon = "images/tx_send_shielded.png"
                            else:
                                icon = "images/tx_send_transparent.png"
                            notify_categoty = self.tr.text("notify_send")
                        elif category == "receive":
                            if tx_type == "shielded":
                                icon = "images/tx_receive_shielded.png"
                            else:
                                icon = "images/tx_receive_transparent.png"
                            notify_categoty = self.tr.text("notify_receive")

                        address = data[2]
                        amount = data[4]
                        if self.settings.hidden_balances():
                            amount = "*.********"
                        timereceived = data[7]
                        formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                        if self.rtl:
                            amount = self.units.arabic_digits(str(amount))
                            formatted_timereceived = self.units.arabic_digits(formatted_timereceived)
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
                            self.notify.send_note(
                                title=f"{notify_categoty} : {amount} BTCZ",
                                text=f"TxID : {txid}"
                            )

            await asyncio.sleep(6)


    def show_transaction_info(self, txid, address):
        self.transactions_info = Txid(
            self.main, txid, address, self.settings, self.utils, self.units, self.rpc, self.tr, self.font
        )
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
        url = "https://explorer.btcz.zelcore.io/tx/"
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
                self.app.loop.create_task(self.get_transactions_archive())
        except Exception as e:
            print(f"Error: {e}")



    async def get_transactions_archive(self):
        try:
            sorted_transactions = self.get_transactions(self.transactions_count, self.transactions_from)
            if not sorted_transactions:
                self.no_more_transactions = True
                return
            for data in sorted_transactions:
                tx_type = data[0]
                category = data[1]
                if category == "send":
                    if tx_type == "shielded":
                        icon = "images/tx_send_shielded.png"
                    else:
                        icon = "images/tx_send_transparent.png"
                elif category == "receive":
                    if tx_type == "shielded":
                        icon = "images/tx_receive_shielded.png"
                    else:
                        icon = "images/tx_receive_transparent.png"

                address = data[2]
                txid = data[3]
                amount = data[4]
                if self.settings.hidden_balances():
                    amount = "*.********"
                timereceived = data[7]
                formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                if self.rtl:
                    amount = self.units.arabic_digits(str(amount))
                    formatted_timereceived = self.units.arabic_digits(formatted_timereceived)
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
        address = sender.Rows[row_index].Cells[1].Value
        self.show_transaction_info(txid, address)

    
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
