
import asyncio
import json

from toga import (
    App, Box, Label, ImageView, Window, TextInput,
    Button, ProgressBar
)
from ..framework import (
    Cursors, FlatStyle, Forms, ProgressStyle, Os
)
from toga.style.pack import Pack
from toga.colors import (
    rgb, WHITE, GRAY, YELLOW, RED, GREENYELLOW, BLACK
)
from toga.constants import (
    TOP, ROW, COLUMN, RIGHT, CENTER,
    BOTTOM, HIDDEN, VISIBLE
)



class Wallet(Box):
    def __init__(self, app:App, main:Window, settings, units, commands, tr, font):
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

        self.commands = commands
        self.units = units
        self.settings = settings
        self.tr = tr
        self.font = font

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.bitcoinz_logo = ImageView(
            image="images/BitcoinZ.png",
            style=Pack(
                width=100,
                height=100,
                background_color = rgb(40,43,48),
                padding = self.tr.padding("bitcoinz_logo"),
            )
        )
        self.bitcoinz_title = Label(
            text=self.tr.text("bitcoinz_title"),
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = self.tr.align("bitcoinz_title"),
                padding = self.tr.padding("bitcoinz_title")
            )
        )
        self.bitcoinz_title._impl.native.Font = self.font.get(self.tr.size("bitcoinz_title"), True)

        self.bitcoinz_version = Label(
            text="",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                text_align = self.tr.align("bitcoinz_version"),
                padding = self.tr.padding("bitcoinz_version")
            )
        )
        self.bitcoinz_version._impl.native.Font = self.font.get(8, True)
        
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
        self.total_balances_label._impl.native.Font = self.font.get(self.tr.size("total_balances_label"), True)

        self.total_value = Label(
            text="",
            style=Pack(
                text_align = CENTER,
                color = WHITE,
                background_color = rgb(30,33,36)
            )
        )
        self.total_value._impl.native.Font = self.font.get(self.tr.size("total_value"), True)

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
        self.transparent_label._impl.native.Font = self.font.get(8, True)

        self.transparent_value = Label(
            text="",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = YELLOW
            )
        )
        self.transparent_value._impl.native.Font = self.font.get(9, True)

        self.private_label = Label(
            text=self.tr.text("private_label"),
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = GRAY
            )
        )
        self.private_label._impl.native.Font = self.font.get(8, True)

        self.private_value = Label(
            text="",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = CENTER,
                color = rgb(114,137,218)
            )
        )
        self.private_value._impl.native.Font = self.font.get(9, True)

        self.unconfirmed_label = Label(
            text=self.tr.text("unconfirmed_label"),
            style=Pack(
                background_color = rgb(30,33,36),
                text_align = CENTER,
                color = GRAY,
                visibility = HIDDEN
            )
        )
        self.unconfirmed_label._impl.native.Font = self.font.get(8, True)

        self.unconfirmed_value = Label(
            text="",
            style=Pack(
                background_color = rgb(30,33,36),
                text_align = CENTER,
                color = RED,
                visibility = HIDDEN
            )
        )
        self.unconfirmed_value._impl.native.Font = self.font.get(9, True)
        
        self.unconfirmed_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = CENTER,
                background_color = rgb(30,33,36),
                padding = self.tr.padding("unconfirmed_box"),
                visibility = HIDDEN
            )
        )
        
        if self.rtl:
            self.add(
                self.balances_box,
                self.unconfirmed_box,
                self.bitcoinz_title_box,
                self.bitcoinz_logo
            )
        else:
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
        if self.rtl:
            self.balances_type_box.add(
                self.private_balance_box,
                self.transparent_balance_box
            )
        else:
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
                if self.rtl:
                    totalbalance = self.units.arabic_digits(totalbalance)
                    transparentbalance = self.units.arabic_digits(transparentbalance)
                    privatebalance = self.units.arabic_digits(privatebalance)
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
                    if self.rtl:
                        unconfirmed = self.units.arabic_digits(unconfirmed)
                    if self.settings.hidden_balances():
                        unconfirmed = "*.********"
                    self.unconfirmed_value.text = unconfirmed
                else:
                    self.unconfirmed_box.style.visibility = HIDDEN
                    self.unconfirmed_label.style.visibility = HIDDEN
                    self.unconfirmed_value.style.visibility = HIDDEN
            await asyncio.sleep(5)



class ImportKey(Window):
    def __init__(self, main:Window, settings, utils, commands, tr, font):
        super().__init__(
            size = (600, 150),
            resizable= False
        )
        
        self.main = main
        self.utils = utils
        self.commands = commands
        self.settings = settings
        self.tr = tr
        self.font = font

        self.title = self.tr.title("importkey_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

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
        self.info_label._impl.native.Font = self.font.get(11)

        self.key_input = TextInput(
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                flex = 3,
                padding_left = 10
            )
        )
        self.key_input._impl.native.Font = self.font.get(self.tr.size("key_input"), True)
        
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
        self.import_button._impl.native.Font = self.font.get(self.tr.size("import_button"), True)
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
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
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
                await self.main.receive_page.reload_addresses()
                await self.main.mining_page.reload_addresses()
                self.main.import_key_toggle = None
                self.close()
                self.app.current_window = self.main
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
    def __init__(self, main:Window, settings, utils, commands, tr, font):
        super().__init__(
            size = (600, 150),
            resizable= False
        )
        
        self.main = main
        self.utils = utils
        self.commands = commands
        self.settings = settings
        self.tr = tr
        self.font = font

        self.title = self.tr.title("importwallet_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

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
        self.info_label._impl.native.Font = self.font.get(11)

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
        self.file_input._impl.native.Font = self.font.get(self.tr.size("file_input"), True)
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
        self.import_button._impl.native.Font = self.font.get(self.tr.size("import_button"), True)
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
            on_press=self.close_import_file
        )
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
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
                await self.main.receive_page.reload_addresses()
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