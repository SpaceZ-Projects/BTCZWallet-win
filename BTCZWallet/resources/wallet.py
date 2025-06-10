
import asyncio
import json

from toga import (
    App, Box, Label, ImageView, Window, TextInput,
    Button, ProgressBar
)
from ..framework import (
    Cursors, FlatStyle, Forms, ProgressStyle, Os,
    CustomFont
)
from toga.style.pack import Pack
from toga.colors import (
    rgb, WHITE, GRAY, YELLOW, RED, GREENYELLOW, BLACK
)
from toga.constants import (
    TOP, ROW, LEFT, COLUMN, RIGHT, CENTER,
    BOTTOM, HIDDEN, VISIBLE
)

from .client import Client
from .utils import Utils
from .units import Units
from .settings import Settings
from ..translations import Translations



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
        self.settings = Settings(self.app)
        self.tr = Translations(self.settings)

        self.monda_font = CustomFont()

        self.bitcoinz_logo = ImageView(
            image="images/BitcoinZ.png",
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
                text_align = LEFT,
                padding_top = 25
            )
        )
        self.bitcoinz_title._impl.native.Font = self.monda_font.get(22, True)

        self.bitcoinz_version = Label(
            text="",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                text_align = LEFT,
                padding_left = 13
            )
        )
        self.bitcoinz_version._impl.native.Font = self.monda_font.get(8, True)
        
        self.bitcoinz_title_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment=CENTER,
                flex = 1
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
            text=self.tr.text("total_balances_label"),
            style=Pack(
                text_align = CENTER,
                color = GRAY,
                background_color = rgb(30,33,36),
                padding_top = 5,
                flex =1
            )
        )
        self.total_balances_label._impl.native.Font = self.monda_font.get(14, True)

        self.total_value = Label(
            text="",
            style=Pack(
                text_align = CENTER,
                color = WHITE,
                background_color = rgb(30,33,36)
            )
        )
        self.total_value._impl.native.Font = self.monda_font.get(14, True)

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
            text=self.tr.text("transparent_label"),
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = GRAY
            )
        )
        self.transparent_label._impl.native.Font = self.monda_font.get(8, True)

        self.transparent_value = Label(
            text="",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = YELLOW
            )
        )
        self.transparent_value._impl.native.Font = self.monda_font.get(9, True)

        self.private_label = Label(
            text=self.tr.text("private_label"),
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = GRAY
            )
        )
        self.private_label._impl.native.Font = self.monda_font.get(8, True)

        self.private_value = Label(
            text="",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = rgb(114,137,218)
            )
        )
        self.private_value._impl.native.Font = self.monda_font.get(9, True)

        self.unconfirmed_label = Label(
            text=self.tr.text("unconfirmed_label"),
            style=Pack(
                background_color = rgb(30,33,36),
                text_align = CENTER,
                color = GRAY,
                visibility = HIDDEN
            )
        )
        self.unconfirmed_label._impl.native.Font = self.monda_font.get(8, True)

        self.unconfirmed_value = Label(
            text="",
            style=Pack(
                background_color = rgb(30,33,36),
                text_align = CENTER,
                color = RED,
                visibility = HIDDEN
            )
        )
        self.unconfirmed_value._impl.native.Font = self.monda_font.get(9, True)
        
        self.unconfirmed_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = CENTER,
                background_color = rgb(30,33,36),
                padding_top = 82,
                visibility = HIDDEN
            )
        )

        self.add(
            self.bitcoinz_logo,
            self.bitcoinz_title_box,
            self.unconfirmed_box,
            self.balances_box
        )
        self.bitcoinz_title_box.add(
            self.bitcoinz_title,
            self.bitcoinz_version
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
        self.app.add_background_task(self.get_node_version)
        self.app.add_background_task(self.update_balances)


    async def get_node_version(self, widget):
        result, _ = await self.commands.getInfo()
        if result:
            result = json.loads(result)
            subversion = result.get('subversion')
            build = result.get('build')
            clean_version = subversion.strip('/')
            if ':' in clean_version:
                name, version = clean_version.split(':', 1)
                formatted_version = f"{name} v {version}"
            else:
                formatted_version = clean_version
            build_suffix = build.split('-')[1] if build and '-' in build else build
            self.bitcoinz_version.text = f"Core : {formatted_version} | Build : {build_suffix}"


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
                if self.settings.hidden_balances():
                    totalbalance = "*.********"
                    transparentbalance = "*.********"
                    privatebalance = "*.********"
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
                    if self.settings.hidden_balances():
                        unconfirmed = "*.********"
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
            resizable= False
        )
        
        self.main = main
        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.settings = Settings(self.app)
        self.tr = Translations(self.settings)

        self.title = self.tr.title("importkey_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        self.monda_font = CustomFont()

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.info_label = Label(
            text=self.tr.text("info_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                padding_top = 5
            )
        )
        self.info_label._impl.native.Font = self.monda_font.get(11)

        self.key_input = TextInput(
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                flex = 3,
                padding_left = 10
            )
        )
        self.key_input._impl.native.Font = self.monda_font.get(11, True)
        
        self.import_button = Button(
            text=self.tr.text("import_button"),
            style=Pack(
                color= GRAY,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (0,10,0,10)
            ),
            on_press=self.import_button_click
        )
        self.import_button._impl.native.Font = self.monda_font.get(9, True)
        self.import_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.import_button._impl.native.MouseEnter += self.import_button_mouse_enter
        self.import_button._impl.native.MouseLeave += self.import_button_mouse_leave

        self.progress_bar = ProgressBar(
            style=Pack(
                height= 25,
                flex = 1,
                padding = (0,10,0,10)
            )
        )
        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (5,0,10,0)
            )
        )

        self.cancel_button = Button(
            text=self.tr.text("cancel_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_import_key
        )
        self.cancel_button._impl.native.Font = self.monda_font.get(9, True)
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
                title=self.tr.title("missingkey_dialog"),
                message=self.tr.message("missingkey_dialog")
            )
            self.key_input.focus()
            return
        self.input_box.remove(
            self.import_button
        )
        self.input_box.add(
            self.progress_bar
        )
        self.key_input.readonly = True
        self.cancel_button.enabled = False
        self.main.import_key_toggle = True
        self.app.add_background_task(self.import_private_key)


    async def import_private_key(self, widget):
        def on_result(widget, result):
            if result is None:
                self.main.import_key_toggle = None
                self.input_box.remove(
                    self.progress_bar
                )
                self.input_box.add(
                    self.import_button
                )
                self.key_input.readonly = False
                self.cancel_button.enabled = True
        key = self.key_input.value
        result, error_message = await self.commands.ImportPrivKey(key)
        if error_message:
            result, error_message = await self.commands.z_ImportKey(key)
            if error_message:
                self.error_dialog(
                    title=self.tr.title("invalidkey_dialog"),
                    message=self.tr.message("invalidkey_dialog"),
                    on_result=on_result
                )
                return     
        await self.update_import_window()


    async def update_import_window(self):
        while True:
            result,_ = await self.commands.getInfo()
            if result:
                self.main.transactions_page.reload_transactions()
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
        self.app.current_window = self.main




class ImportWallet(Window):
    def __init__(self, main:Window):
        super().__init__(
            size = (600, 150),
            resizable= False
        )
        
        self.main = main
        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.settings = Settings(self.app)
        self.tr = Translations(self.settings)

        self.title = self.tr.title("importwallet_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        self.monda_font = CustomFont()

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.info_label = Label(
            text=self.tr.text("info_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                padding_top = 5
            )
        )
        self.info_label._impl.native.Font = self.monda_font.get(11)

        self.file_input = TextInput(
            value=self.tr.text("file_input"),
            style=Pack(
                color = GRAY,
                text_align= CENTER,
                background_color = rgb(40,43,48),
                flex = 3,
                padding_left = 10
            ),
            readonly=True
        )
        self.file_input._impl.native.Font = self.monda_font.get(11, True)
        self.file_input._impl.native.AllowDrop = True
        self.file_input._impl.native.Click += self.select_wallet_file
        self.file_input._impl.native.DragEnter += Forms.DragEventHandler(self.on_drag_enter)
        self.file_input._impl.native.DragDrop += Forms.DragEventHandler(self.on_drag_drop)
        self.file_input._impl.native.Cursor = Cursors.HAND
        
        self.import_button = Button(
            text=self.tr.text("import_button"),
            style=Pack(
                color= GRAY,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (0,10,0,10)
            ),
            on_press = self.import_button_click
        )
        self.import_button._impl.native.Font = self.monda_font.get(9, True)
        self.import_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.import_button._impl.native.MouseEnter += self.import_button_mouse_enter
        self.import_button._impl.native.MouseLeave += self.import_button_mouse_leave

        self.progress_bar = ProgressBar(
            style=Pack(
                height= 25,
                flex = 1,
                padding = (0,10,0,10)
            )
        )
        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE

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
            text=self.tr.text("cancel_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_import_file
        )
        self.cancel_button._impl.native.Font = self.monda_font.get(9, True)
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
            self.file_input,
            self.import_button
        )

    def select_wallet_file(self, sender, event):
        def on_result(widget, result):
            if result:
                self.file_input.value = result
                self.file_input.style.color = WHITE
        self.open_file_dialog(
            title=self.tr.title("selectfile_dialog"),
            on_result=on_result
        )
        

    def on_drag_enter(self, sender, event):
        if event.Data.GetDataPresent("FileDrop"):
            event.Effect = Forms.DragDropEffects.Copy
        else:
            event.Effect = Forms.DragDropEffects(0)


    def on_drag_drop(self, sender, event):
        files = event.Data.GetData("FileDrop")
        if files and len(files) > 0:
            self.file_input.value = files[0]
            self.file_input.style.color = WHITE


    def import_button_click(self, button):
        if self.file_input.value == self.tr.text("file_input"):
            self.error_dialog(
                title=self.tr.title("missingfile_dialog"),
                message=self.tr.message("missingfile_dialog")
            )
            return

        extension = Os.Path.GetExtension(self.file_input.value)
        if extension:
            self.error_dialog(
                title=self.tr.title("invalidfile_dialog"),
                message=self.tr.message("invalidfile_dialog")
            )
            return
        
        self.input_box.remove(
            self.import_button
        )
        self.input_box.add(
            self.progress_bar
        )
        self.file_input._impl.native.Click -= self.select_wallet_file
        self.file_input._impl.native.AllowDrop = False
        self.cancel_button.enabled = False
        self.main.import_key_toggle = True
        self.app.add_background_task(self.import_wallet_file)


    async def import_wallet_file(self, widget):
        file_path = self.file_input.value
        await self.commands.z_ImportWallet(file_path) 
        await self.update_import_window()


    async def update_import_window(self):
        while True:
            result,_ = await self.commands.getInfo()
            if result:
                self.main.transactions_page.reload_transactions()
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

    def close_import_file(self, button):
        self.close()
        self.app.current_window = self.main