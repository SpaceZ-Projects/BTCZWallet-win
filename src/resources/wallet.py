
import asyncio
import json

from toga import (
    App, Box, Label, ImageView, Window, TextInput,
    Button
)
from ..framework import Cursors, FlatStyle
from toga.style.pack import Pack
from toga.colors import (
    rgb, WHITE, GRAY, YELLOW, RED, GREENYELLOW, BLACK
)
from toga.constants import (
    TOP, ROW, LEFT, BOLD, COLUMN,
    RIGHT, CENTER, BOTTOM, HIDDEN, VISIBLE
)

from .client import Client
from .utils import Utils
from .units import Units

class Wallet(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                height = 120,
                alignment = TOP,
                background_color = rgb(40,43,48),
                padding =5
            )
        )

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.units = Units(self.app)

        self.bitcoinz_logo = ImageView(
            image="images/BTCZ.png",
            style=Pack(
                width=100,
                height=100,
                background_color = rgb(40,43,48),
                padding_top = 10,
                padding_left = 10
            )
        )
        self.bitcoinz_title = Label(
            text="Full Node Wallet",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size = 20,
                font_weight = BOLD,
                text_align = LEFT,
                flex = 1,
                padding_top = 35
            )
        )
        self.balances_box = Box(
            style=Pack(
                direction = COLUMN,
                padding = 10,
                alignment = RIGHT,
                width = 350,
                background_color = rgb(30,33,36)
            )
        )
        self.total_balances_label = Label(
            text="Total Balances",
            style=Pack(
                font_size = 13,
                font_weight = BOLD,
                text_align = CENTER,
                color = GRAY,
                background_color = rgb(30,33,36),
                padding_top = 5,
                flex =1
            )
        )
        self.total_value = Label(
            text="",
            style=Pack(
                font_size = 13,
                font_weight = BOLD,
                text_align = CENTER,
                color = WHITE,
                background_color = rgb(30,33,36),
                padding_top = 5
            )
        )
        self.balances_type_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = BOTTOM,
                flex = 1
            )
        )

        self.transparent_balance_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                padding = 5,
                flex = 1
            )
        )
        self.private_balance_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                padding = 5,
                flex = 1
            )
        )

        self.transparent_label = Label(
            text="Transparent",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = GRAY,
                font_weight = BOLD
            )
        )

        self.transparent_value = Label(
            text="",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = YELLOW,
                font_weight = BOLD
            )
        )

        self.private_label = Label(
            text="Private",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = GRAY,
                font_weight = BOLD
            )
        )

        self.private_value = Label(
            text="",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = rgb(114,137,218),
                font_weight = BOLD
            )
        )
        self.unconfirmed_label = Label(
            text="Unconfirmed Balance",
            style=Pack(
                background_color = rgb(30,33,36),
                text_align = CENTER,
                color = GRAY,
                font_weight = BOLD,
                padding_top = 5,
                visibility = HIDDEN
            )
        )
        self.unconfirmed_value = Label(
            text="",
            style=Pack(
                background_color = rgb(30,33,36),
                text_align = CENTER,
                color = RED,
                font_weight = BOLD,
                padding_bottom = 5,
                visibility = HIDDEN
            )
        )
        self.unconfirmed_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = CENTER,
                background_color = rgb(30,33,36),
                padding_top = 70,
                visibility = HIDDEN
            )
        )

        self.add(
            self.bitcoinz_logo,
            self.bitcoinz_title,
            self.unconfirmed_box,
            self.balances_box
        )
        self.unconfirmed_box.add(
            self.unconfirmed_label,
            self.unconfirmed_value
        )

        self.balances_box.add(
            self.total_balances_label,
            self.total_value,
            self.balances_type_box
        )

        self.balances_type_box.add(
            self.transparent_balance_box,
            self.private_balance_box
        )

        self.transparent_balance_box.add(
            self.transparent_label,
            self.transparent_value
        )
        self.private_balance_box.add(
            self.private_label,
            self.private_value
        )

        self.app.add_background_task(self.update_balances)


    async def update_balances(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            totalbalances,_ = await self.commands.z_getTotalBalance()
            if totalbalances is not None:
                balances = json.loads(totalbalances)
                totalbalance = self.units.format_balance(float(balances.get('total')))
                transparentbalance = self.units.format_balance(float(balances.get('transparent')))
                privatebalance = self.units.format_balance(float(balances.get('private')))
                self.total_value.text = totalbalance
                self.transparent_value.text = transparentbalance
                self.private_value.text = privatebalance
            unconfirmed_balance,_ = await self.commands.getUnconfirmedBalance()
            if unconfirmed_balance is not None:
                unconfirmed = self.units.format_balance(float(unconfirmed_balance))
                if float(unconfirmed) > 0:
                    self.unconfirmed_box.style.visibility = VISIBLE
                    self.unconfirmed_label.style.visibility = VISIBLE
                    self.unconfirmed_value.style.visibility = VISIBLE
                    self.unconfirmed_value.text = unconfirmed
                else:
                    self.unconfirmed_box.style.visibility = HIDDEN
                    self.unconfirmed_label.style.visibility = HIDDEN
                    self.unconfirmed_value.style.visibility = HIDDEN
            await asyncio.sleep(5)



class ImportKey(Window):
    def __init__(self, main:Window):
        super().__init__(
            size = (600, 150),
            resizable= False,
            minimizable = False,
            closable=False
        )
        
        self.main = main
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
        
        self.import_button = Button(
            text="Import",
            style=Pack(
                color= GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size=10,
                flex = 1,
                padding = (0,10,0,10)
            ),
            on_press=self.import_button_click
        )
        self.import_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.import_button._impl.native.MouseEnter += self.import_button_mouse_enter
        self.import_button._impl.native.MouseLeave += self.import_button_mouse_leave

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (10,0,10,0)
            )
        )

        self.cancel_button = Button(
            text="Cancel",
            style=Pack(
                color = RED,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_import_key
        )
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.input_box,
            self.cancel_button
        )
        self.input_box.add(
            self.key_input,
            self.import_button
        )

    def import_button_click(self, button):
        if not self.key_input.value:
            self.error_dialog(
                "Missing Private Key",
                "Please enter a private key to proceed."
            )
            self.key_input.focus()
            return
        self.key_input.readonly = True
        self.import_button.on_press = None
        self.import_button._impl.native.Cursor = Cursors.WAIT
        self.cancel_button.enabled = False
        self.main.import_key_toggle = True
        self.app.add_background_task(self.import_private_key)


    async def import_private_key(self, widget):
        def on_result(widget, result):
            if result is None:
                self.main.import_key_toggle = None
                self.update_import_window()
        key = self.key_input.value
        result, error_message = await self.commands.ImportPrivKey(key)
        if error_message:
            result, error_message = await self.commands.z_ImportKey(key)
            if error_message:
                self.error_dialog(
                    "Invalid Private Key",
                    "The private key you entered is not valid. Please check the format and try again.",
                    on_result=on_result
                )
                return     
        await self.update_import_window()


    async def update_import_window(self):
        while True:
            result,_ = await self.commands.getInfo()
            if result:
                await self.main.transactions_page.reload_transactions()
                await self.main.mining_page.reload_addresses()
                self.main.import_key_toggle = None
                self.close()
                return
            
            await asyncio.sleep(5)


    def import_button_mouse_enter(self, sender, event):
        self.import_button.style.color = BLACK
        self.import_button.style.background_color = GREENYELLOW

    def import_button_mouse_leave(self, sender, event):
        self.import_button.style.color = GRAY
        self.import_button.style.background_color = rgb(30,33,36)

    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)

    def close_import_key(self, button):
        self.close()




class ImportWallet(Window):
    def __init__(self, main:Window):
        super().__init__(
            size = (600, 150),
            resizable= False,
            minimizable = False,
            closable=False
        )
        
        self.main = main
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
            text="Please set your wallet file.\n(This operation may take up to 10 minutes to complete.)",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_size = 11,
                padding_top = 5
            )
        )
        self.key_input = TextInput(
            value="Open file...",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 3,
                padding_left = 10
            ),
            readonly=True
        )
        self.key_input._impl.native.Click += self.select_wallet_file
        
        self.import_button = Button(
            text="Import",
            style=Pack(
                color= GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size=10,
                flex = 1,
                padding = (0,10,0,10)
            )
        )
        self.import_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.import_button._impl.native.MouseEnter += self.import_button_mouse_enter
        self.import_button._impl.native.MouseLeave += self.import_button_mouse_leave

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (10,0,10,0)
            )
        )

        self.cancel_button = Button(
            text="Cancel",
            style=Pack(
                color = RED,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_import_key
        )
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.input_box,
            self.cancel_button
        )
        self.input_box.add(
            self.key_input,
            self.import_button
        )

    def select_wallet_file(self, sender, event):
        def on_result(widget, result):
            if result:
                self.key_input.value = result
                self.import_button.on_press = self.import_button_click
        self.open_file_dialog(
            title="Select file",
            on_result=on_result
        )

    def import_button_click(self, button):
        if not self.key_input.value:
            self.error_dialog(
                "Missing file",
                "Please set a wallet file to proceed."
            )
            return
        self.key_input._impl.native.Click -= self.select_wallet_file
        self.import_button.on_press = None
        self.import_button._impl.native.Cursor = Cursors.WAIT
        self.cancel_button.enabled = False
        self.main.import_key_toggle = True
        self.app.add_background_task(self.import_wallet_file)


    async def import_wallet_file(self, widget):
        wallet = self.key_input.value
        await self.commands.z_ImportWallet(wallet)      
        await self.update_import_window()


    async def update_import_window(self):
        while True:
            result,_ = await self.commands.getInfo()
            if result:
                await self.main.transactions_page.reload_transactions()
                await self.main.mining_page.reload_addresses()
                self.main.import_key_toggle = None
                self.close()
                return
            
            await asyncio.sleep(5)


    def import_button_mouse_enter(self, sender, event):
        self.import_button.style.color = BLACK
        self.import_button.style.background_color = GREENYELLOW

    def import_button_mouse_leave(self, sender, event):
        self.import_button.style.color = GRAY
        self.import_button.style.background_color = rgb(30,33,36)

    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)

    def close_import_key(self, button):
        self.close()