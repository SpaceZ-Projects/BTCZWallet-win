
import asyncio
import webbrowser

from toga import (
    Window, Box, Label
)
from ..framework import (
    Drawing, Color
)

from toga.style.pack import Pack
from toga.colors import rgb, WHITE, YELLOW, GRAY
from toga.constants import (
    COLUMN, ROW, TOP, CENTER, BOLD
)

from .client import Client
from .utils import Utils
from .toolbar import AppToolBar
from .status import AppStatusBar
from .notify import Notify
from .wallet import Wallet
from .home import Home
from .txs import Transactions
from .recieve import Recieve, ImportKey
from .send import Send
from .messages import Messages
from .mining import Mining

class Menu(Window):
    def __init__(self):
        super().__init__()

        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.notify = Notify(self.app)
        self.toolbar = AppToolBar(self.app, self.notify)
        self.statusbar = AppStatusBar(self.app)
        self.wallet = Wallet(self.app)

        self.title = "BitcoinZ Wallet"
        self.size = (900,600)
        self._impl.native.BackColor = Color.rgb(30,33,36)
        
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self.on_close = self.on_close_menu
        self._impl.native.Resize += self._handle_on_resize

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )
        self.menu_bar = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = TOP,
                height = 32,
                flex = 1,
                padding = (0,4,5,4)
            )
        )
        self.pages = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(30,33,36)
            )
        )
        self.home_page = Home(self.app)
        self.transactions_page = Transactions(self.app, self)
        self.recieve_page = Recieve(self.app, self)
        self.send_page = Send(self.app, self)
        self.message_page = Messages(self.app)
        self.mining_page = Mining(self.app)

        self.main_box.add(
            self.toolbar,
            self.wallet,
            self.menu_bar,
            self.pages,
            self.statusbar
        )
        self.content = self.main_box

        self.statusbar.update_statusbar()
        self.insert_menu_buttons()

    def insert_menu_buttons(self):
        self.home_label = Label(
            text="Home",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
        self.home_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (5,0,2,5)
            )
        )
        self.home_button._impl.native.MouseEnter += self.home_button_mouse_enter
        self.home_button._impl.native.MouseLeave += self.home_button_mouse_leave
        self.home_label._impl.native.MouseEnter += self.home_button_mouse_enter
        self.home_label._impl.native.MouseLeave += self.home_button_mouse_leave
        self.home_button._impl.native.Click += self.home_button_click
        self.home_label._impl.native.Click += self.home_button_click

        self.transactions_label = Label(
            text="Transactions",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
        self.transactions_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (5,0,2,0)
            )
        )
        self.transactions_button._impl.native.MouseEnter += self.transactions_button_mouse_enter
        self.transactions_button._impl.native.MouseLeave += self.transactions_button_mouse_leave
        self.transactions_label._impl.native.MouseEnter += self.transactions_button_mouse_enter
        self.transactions_label._impl.native.MouseLeave += self.transactions_button_mouse_leave
        self.transactions_button._impl.native.Click += self.transactions_button_click
        self.transactions_label._impl.native.Click += self.transactions_button_click

        self.recieve_label = Label(
            text="Recieve",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
        self.recieve_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (5,0,2,0)
            )
        )
        self.recieve_button._impl.native.MouseEnter += self.recieve_button_mouse_enter
        self.recieve_button._impl.native.MouseLeave += self.recieve_button_mouse_leave
        self.recieve_label._impl.native.MouseEnter += self.recieve_button_mouse_enter
        self.recieve_label._impl.native.MouseLeave += self.recieve_button_mouse_leave
        self.recieve_button._impl.native.Click += self.recieve_button_click
        self.recieve_label._impl.native.Click += self.recieve_button_click

        self.send_label = Label(
            text="Send",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
        self.send_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (5,0,2,0)
            )
        )
        self.send_button._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_button._impl.native.MouseLeave += self.send_button_mouse_leave
        self.send_label._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_label._impl.native.MouseLeave += self.send_button_mouse_leave
        self.send_button._impl.native.Click += self.send_button_click
        self.send_label._impl.native.Click += self.send_button_click

        self.message_label = Label(
            text="Messages",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
        self.message_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (5,0,2,0)
            )
        )
        self.message_button._impl.native.MouseEnter += self.message_button_mouse_enter
        self.message_button._impl.native.MouseLeave += self.message_button_mouse_leave
        self.message_label._impl.native.MouseEnter += self.message_button_mouse_enter
        self.message_label._impl.native.MouseLeave += self.message_button_mouse_leave
        self.message_button._impl.native.Click += self.message_button_click
        self.message_label._impl.native.Click += self.message_button_click
        
        self.mining_label = Label(
            text="Mining",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
        self.mining_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (5,5,2,0)
            )
        )
        self.mining_button._impl.native.MouseEnter += self.mining_button_mouse_enter
        self.mining_button._impl.native.MouseLeave += self.mining_button_mouse_leave
        self.mining_label._impl.native.MouseEnter += self.mining_button_mouse_enter
        self.mining_label._impl.native.MouseLeave += self.mining_button_mouse_leave
        self.mining_button._impl.native.Click += self.mining_button_click
        self.mining_label._impl.native.Click += self.mining_button_click

        self.menu_bar.add(
            self.home_button,
            self.transactions_button,
            self.recieve_button,
            self.send_button,
            self.message_button,
            self.mining_button
        )
        self.home_button.add(
            self.home_label
        )
        self.transactions_button.add(
            self.transactions_label
        )
        self.recieve_button.add(
            self.recieve_label
        )
        self.send_button.add(
            self.send_label
        )
        self.message_button.add(
            self.message_label
        )
        self.mining_button.add(
            self.mining_label
        )

        self.home_button_toggle = None
        self.transactions_button_toggle = None
        self.recieve_button_toggle = None
        self.send_button_toggle = None
        self.message_button_toggle = None
        self.mining_button_toggle = None
        self.app.add_background_task(self.set_default_page)

    async def set_default_page(self, widget):
        await asyncio.sleep(0.5)
        self.home_button_click(None, None)
        self.add_actions_cmds()
        await self.transactions_page.update_transactions()

    def add_actions_cmds(self):
        self.toolbar.generate_t_cmd.action = self.new_transparent_address
        self.toolbar.generate_z_cmd.action = self.new_private_address
        self.toolbar.check_update_cmd.action = self.check_app_version
        self.toolbar.import_key_cmd.action = self.show_import_key

    def new_transparent_address(self, sender, event):
        self.app.add_background_task(self.generate_transparent_address)

    def new_private_address(self, sender, event):
        self.app.add_background_task(self.generate_private_address)

    async def generate_transparent_address(self, widget):
        new_address = await self.commands.getNewAddress()
        if new_address:
            if self.recieve_page.transparent_toggle:
                self.insert_new_address(new_address[0])
            if self.send_page.transparent_toggle:
                await self.send_page.update_send_options(None)
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address[0]}"
            )

    async def generate_private_address(self, widget):
        new_address = await self.commands.z_getNewAddress()
        if new_address:
            if self.recieve_page.private_toggle:
                self.insert_new_address(new_address[0])
            if self.send_page.private_toggle:
                await self.send_page.update_send_options(None)
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address[0]}"
            )

    def insert_new_address(self, address):
        self.recieve_page.addresses_table.add_row(
            index=0,
            row_data={0: address}
        )

    def check_app_version(self, sender, event):
        self.app.add_background_task(self.fetch_repo_info)

    async def fetch_repo_info(self, widget):
        git_version, link = await self.utils.get_repo_info()
        if git_version:
            self.git_link = link
            current_version = self.app.version
            if git_version == current_version:
                self.info_dialog(
                    title="Check updates",
                    message=f"Current version: {current_version}\nThe app version is up to date."
                )
            else:
                self.question_dialog(
                    title="Check updates",
                    message=f"Current version: {current_version}\nGit version: {git_version}\nWould you like to update the app ?",
                    on_result=self.update_app_result
                )

    def update_app_result(self, widget, result):
        if result is True:
            webbrowser.open(self.git_link)

    def show_import_key(self, sender, event):
        self.import_window = ImportKey()
        self.import_window._impl.native.ShowDialog()


    def home_button_click(self, sender, event):
        self.clear_buttons()
        self.home_button_toggle = True
        self.home_button._impl.native.Click -= self.home_button_click
        self.home_label._impl.native.Click -= self.home_button_click
        self.home_label.style.color = WHITE
        self.home_button.style.background_color = YELLOW
        self.pages.add(self.home_page)
        self.app.add_background_task(self.home_page.insert_widgets)


    def home_button_mouse_enter(self, sender, event):
        if self.home_button_toggle:
            return
        self.home_button.style.background_color = rgb(66,69,73)

    def home_button_mouse_leave(self, sender, event):
        if self.home_button_toggle:
            return
        self.home_button.style.background_color = rgb(30,33,36)

    def transactions_button_click(self, sender, event):
        self.clear_buttons()
        self.transactions_button_toggle = True
        self.transactions_button._impl.native.Click -= self.transactions_button_click
        self.transactions_label._impl.native.Click -= self.transactions_button_click
        self.transactions_label.style.color = WHITE
        self.transactions_button.style.background_color = YELLOW
        self.pages.add(self.transactions_page)
        self.app.add_background_task(self.transactions_page.insert_widgets)

    def transactions_button_mouse_enter(self, sender, event):
        if self.transactions_button_toggle:
            return
        self.transactions_button.style.background_color = rgb(66,69,73)

    def transactions_button_mouse_leave(self, sender, event):
        if self.transactions_button_toggle:
            return
        self.transactions_button.style.background_color = rgb(30,33,36)

    def recieve_button_click(self, sender, event):
        self.clear_buttons()
        self.recieve_button_toggle = True
        self.recieve_button._impl.native.Click -= self.recieve_button_click
        self.recieve_label._impl.native.Click -= self.recieve_button_click
        self.recieve_label.style.color = WHITE
        self.recieve_button.style.background_color = YELLOW
        self.pages.add(self.recieve_page)
        self.app.add_background_task(self.recieve_page.insert_widgets)

    def recieve_button_mouse_enter(self, sender, event):
        if self.recieve_button_toggle:
            return
        self.recieve_button.style.background_color = rgb(66,69,73)

    def recieve_button_mouse_leave(self, sender, event):
        if self.recieve_button_toggle:
            return
        self.recieve_button.style.background_color = rgb(30,33,36)

    def send_button_click(self, sender, event):
        self.clear_buttons()
        self.send_button_toggle = True
        self.send_button._impl.native.Click -= self.send_button_click
        self.send_label._impl.native.Click -= self.send_button_click
        self.send_label.style.color = WHITE
        self.send_button.style.background_color = YELLOW
        self.pages.add(self.send_page)
        self.app.add_background_task(self.send_page.insert_widgets)

    def send_button_mouse_enter(self, sender, event):
        if self.send_button_toggle:
            return
        self.send_button.style.background_color = rgb(66,69,73)

    def send_button_mouse_leave(self, sender, event):
        if self.send_button_toggle:
            return
        self.send_button.style.background_color = rgb(30,33,36)

    def message_button_click(self, sender, event):
        self.clear_buttons()
        self.message_button_toggle = True
        self.message_button._impl.native.Click -= self.message_button_click
        self.message_label._impl.native.Click -= self.message_button_click
        self.message_label.style.color = WHITE
        self.message_button.style.background_color = YELLOW
        self.pages.add(self.message_page)
        self.app.add_background_task(self.message_page.insert_widgets)
    
    def message_button_mouse_enter(self, sender, event):
        if self.message_button_toggle:
            return
        self.message_button.style.background_color = rgb(66,69,73)

    def message_button_mouse_leave(self, sender, event):
        if self.message_button_toggle:
            return
        self.message_button.style.background_color = rgb(30,33,36)

    def mining_button_click(self, sender, event):
        self.clear_buttons()
        self.mining_button_toggle = True
        self.mining_button._impl.native.Click -= self.mining_button_click
        self.mining_label._impl.native.Click -= self.mining_button_click
        self.mining_label.style.color = WHITE
        self.mining_button.style.background_color = YELLOW
        self.pages.add(self.mining_page)

    def mining_button_mouse_enter(self, sender, event):
        if self.mining_button_toggle:
            return
        self.mining_button.style.background_color = rgb(66,69,73)

    def mining_button_mouse_leave(self, sender, event):
        if self.mining_button_toggle:
            return
        self.mining_button.style.background_color = rgb(30,33,36)

    def clear_buttons(self):
        if self.home_button_toggle:
            self.home_button_toggle = None
            self.pages.remove(self.home_page)
            self.home_button._impl.native.Click += self.home_button_click
            self.home_label._impl.native.Click += self.home_button_click
            self.home_label.style.color = GRAY
            self.home_button.style.background_color = rgb(30,33,36)

        elif self.transactions_button_toggle:
            self.transactions_button_toggle = None
            self.pages.remove(self.transactions_page)
            self.transactions_button._impl.native.Click += self.transactions_button_click
            self.transactions_label._impl.native.Click += self.transactions_button_click
            self.transactions_label.style.color = GRAY
            self.transactions_button.style.background_color = rgb(30,33,36)

        elif self.recieve_button_toggle:
            self.recieve_button_toggle = None
            self.pages.remove(self.recieve_page)
            self.recieve_button._impl.native.Click += self.recieve_button_click
            self.recieve_label._impl.native.Click += self.recieve_button_click
            self.recieve_label.style.color = GRAY
            self.recieve_button.style.background_color = rgb(30,33,36)

        elif self.send_button_toggle:
            self.send_button_toggle = None
            self.pages.remove(self.send_page)
            self.send_button._impl.native.Click += self.send_button_click
            self.send_label._impl.native.Click += self.send_button_click
            self.send_label.style.color = GRAY
            self.send_button.style.background_color = rgb(30,33,36)

        elif self.message_button_toggle:
            self.message_button_toggle = None
            self.pages.remove(self.message_page)
            self.message_button._impl.native.Click += self.message_button_click
            self.message_label._impl.native.Click += self.message_button_click
            self.message_label.style.color = GRAY
            self.message_button.style.background_color = rgb(30,33,36)

        elif self.mining_button_toggle:
            self.mining_button_toggle = None
            self.pages.remove(self.mining_page)
            self.mining_button._impl.native.Click += self.mining_button_click
            self.mining_label._impl.native.Click += self.mining_button_click
            self.mining_label.style.color = GRAY
            self.mining_button.style.background_color = rgb(30,33,36)

    
    def _handle_on_resize(self, sender, event):
        min_width = 916
        min_height = 639
        self._impl.native.MinimumSize = Drawing.Size(min_width, min_height)        
            

    def on_close_menu(self, widget):
        self.notify.hide()
        self.app.exit()