
import asyncio
import webbrowser
from datetime import datetime

from toga import (
    Window, Box, Button
)
from ..framework import (
    Drawing, Color, Sys, FormState, Os, FlatStyle,
    Relation, AlignContent
)

from toga.style.pack import Pack
from toga.colors import rgb, WHITE, YELLOW, GRAY, BLACK
from toga.constants import (
    COLUMN, ROW, TOP, CENTER, BOLD
)

from .client import Client
from .utils import Utils
from .toolbar import AppToolBar
from .status import AppStatusBar
from .notify import Notify
from .wallet import Wallet, ImportKey, ImportWallet
from .home import Home, Currency
from .txs import Transactions
from .receive import Receive
from .send import Send
from .messages import Messages, EditUser
from .mining import Mining
from .storage import Storage
from .settings import Settings
from .network import Peer, AddNode


class Menu(Window):
    def __init__(self):
        super().__init__()

        self.title = "BitcoinZ Wallet"
        self.size = (900,607)
        self._impl.native.BackColor = Color.rgb(30,33,36)

        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.storage = Storage(self.app)
        self.statusbar = AppStatusBar(self.app, self)
        self.wallet = Wallet(self.app, self)
        self.settings = Settings(self.app)
        
        self._is_minimized = None
        self._is_hidden = None
        self.import_key_toggle = None
        self.peer_toggle = None
        
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self.on_close = self.on_close_menu
        self._impl.native.Resize += self._handle_on_resize
        self._impl.native.Activated += self._handle_on_activated
        self._impl.native.Deactivate += self._handle_on_deactivated

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

        self.home_page = Home(self.app, self)
        self.transactions_page = Transactions(self.app, self)
        self.receive_page = Receive(self.app, self)
        self.send_page = Send(self.app, self)
        self.message_page = Messages(self.app, self)
        self.mining_page = Mining(self.app, self)
        self.notify = Notify(self.app, self, self.home_page, self.mining_page)
        self.toolbar = AppToolBar(self.app, self, self.notify, self.home_page, self.mining_page)

        self.main_box.add(
            self.toolbar,
            self.wallet,
            self.menu_bar,
            self.pages,
            self.statusbar
        )
        self.content = self.main_box

        self.statusbar.run_statusbar_tasks()
        self.insert_menu_buttons()

    def insert_menu_buttons(self):
        self.home_button = Button(
            text="  Home",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            ),
            on_press=self.home_button_click
        )
        self.home_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.home_button._impl.native.TextImageRelation = Relation.IMAGEBEFORETEXT
        self.home_button._impl.native.ImageAlign = AlignContent.RIGHT
        self.home_button._impl.native.MouseEnter += self.home_button_mouse_enter
        self.home_button._impl.native.MouseLeave += self.home_button_mouse_leave

        self.transactions_button = Button(
            text="  Transactions",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            ),
            on_press=self.transactions_button_click
        )
        transactions_i_icon = self.menu_icon("images/txs_i.png")
        self.transactions_button._impl.native.Image = Drawing.Image.FromFile(transactions_i_icon)
        self.transactions_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.transactions_button._impl.native.TextImageRelation = Relation.IMAGEBEFORETEXT
        self.transactions_button._impl.native.ImageAlign = AlignContent.RIGHT
        self.transactions_button._impl.native.MouseEnter += self.transactions_button_mouse_enter
        self.transactions_button._impl.native.MouseLeave += self.transactions_button_mouse_leave

        self.receive_button = Button(
            text="  Receive",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            ),
            on_press=self.receive_button_click
        )
        receive_i_icon = self.menu_icon("images/receive_i.png")
        self.receive_button._impl.native.Image = Drawing.Image.FromFile(receive_i_icon)
        self.receive_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.receive_button._impl.native.TextImageRelation = Relation.IMAGEBEFORETEXT
        self.receive_button._impl.native.ImageAlign = AlignContent.RIGHT
        self.receive_button._impl.native.MouseEnter += self.receive_button_mouse_enter
        self.receive_button._impl.native.MouseLeave += self.receive_button_mouse_leave

        self.send_button = Button(
            text="  Send",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            ),
            on_press=self.send_button_click
        )
        send_i_icon = self.menu_icon("images/send_i.png")
        self.send_button._impl.native.Image = Drawing.Image.FromFile(send_i_icon)
        self.send_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.send_button._impl.native.TextImageRelation = Relation.IMAGEBEFORETEXT
        self.send_button._impl.native.ImageAlign = AlignContent.RIGHT
        self.send_button._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_button._impl.native.MouseLeave += self.send_button_mouse_leave

        self.message_button = Button(
            text="  Messages",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            ),
            on_press=self.message_button_click
        )
        message_i_icon = self.menu_icon("images/messages_i.png")
        self.message_button._impl.native.Image = Drawing.Image.FromFile(message_i_icon)
        self.message_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.message_button._impl.native.TextImageRelation = Relation.IMAGEBEFORETEXT
        self.message_button._impl.native.ImageAlign = AlignContent.RIGHT
        self.message_button._impl.native.MouseEnter += self.message_button_mouse_enter
        self.message_button._impl.native.MouseLeave += self.message_button_mouse_leave
        
        self.mining_button = Button(
            text="  Mining",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            ),
            on_press=self.mining_button_click
        )
        mining_i_icon = self.menu_icon("images/mining_i.png")
        self.mining_button._impl.native.Image = Drawing.Image.FromFile(mining_i_icon)
        self.mining_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.mining_button._impl.native.TextImageRelation = Relation.IMAGEBEFORETEXT
        self.mining_button._impl.native.ImageAlign = AlignContent.RIGHT
        self.mining_button._impl.native.MouseEnter += self.mining_button_mouse_enter
        self.mining_button._impl.native.MouseLeave += self.mining_button_mouse_leave

        self.menu_bar.add(
            self.home_button,
            self.transactions_button,
            self.receive_button,
            self.send_button,
            self.message_button,
            self.mining_button
        )

        self.home_button_toggle = None
        self.transactions_button_toggle = None
        self.receive_button_toggle = None
        self.send_button_toggle = None
        self.message_button_toggle = None
        self.mining_button_toggle = None
        self.app.add_background_task(self.set_default_page)

    async def set_default_page(self, widget):
        await asyncio.sleep(0.5)
        self.home_button_click(None)
        self.add_actions_cmds()
        self.app.add_background_task(self.transactions_page.update_transactions)
        await asyncio.sleep(1)
        await self.message_page.gather_unread_memos()

    def add_actions_cmds(self):
        if self.settings.notification_txs():
            self.toolbar.notification_txs_cmd.checked = True
        else:
            self.toolbar.notification_txs_cmd.checked = self.settings.notification_txs()
        if self.settings.notification_messages():
            self.toolbar.notification_messages_cmd.checked = True
        else:
            self.toolbar.notification_messages_cmd.checked = self.settings.notification_messages()
        if self.settings.minimize_to_tray():
            self.toolbar.minimize_cmd.checked = True
        else:
            self.toolbar.minimize_cmd.checked = self.settings.minimize_to_tray()
        if self.settings.startup():
            self.toolbar.startup_cmd.checked = True
        else:
            self.toolbar.startup_cmd.checked = self.settings.startup()

        self.toolbar.notification_txs_cmd.action = self.update_notifications_txs
        self.toolbar.notification_messages_cmd.action = self.update_notifications_messages
        self.toolbar.minimize_cmd.action = self.update_minimize_to_tray
        self.toolbar.startup_cmd.action = self.update_app_startup
        self.toolbar.peer_info_cmd.action = self.show_peer_info
        self.toolbar.add_node_cmd.action = self.show_add_node
        self.toolbar.currency_cmd.action = self.show_currencies_list
        self.toolbar.generate_t_cmd.action = self.new_transparent_address
        self.toolbar.generate_z_cmd.action = self.new_private_address
        self.toolbar.check_update_cmd.action = self.check_app_version
        self.toolbar.join_us_cmd.action = self.join_us
        self.toolbar.import_key_cmd.action = self.show_import_key
        self.toolbar.export_wallet_cmd.action = self.export_wallet
        self.toolbar.import_wallet_cmd.action = self.show_import_wallet
        self.toolbar.edit_username_cmd.action = self.edit_messages_username
        self.toolbar.backup_messages_cmd.action = self.backup_messages


    def update_notifications_txs(self, sender, event):
        if self.toolbar.notification_txs_cmd.checked:
            self.toolbar.notification_txs_cmd.checked = False
            self.settings.update_settings("notifications_txs", False)
        else:
            self.toolbar.notification_txs_cmd.checked = True
            self.settings.update_settings("notifications_txs", True)

    def update_notifications_messages(self, sender, event):
        if self.toolbar.notification_messages_cmd.checked:
            self.toolbar.notification_messages_cmd.checked = False
            self.settings.update_settings("notifications_messages", False)
        else:
            self.toolbar.notification_messages_cmd.checked = True
            self.settings.update_settings("notifications_messages", True)

    def update_minimize_to_tray(self, sender, event):
        if self.toolbar.minimize_cmd.checked:
            self.toolbar.minimize_cmd.checked = False
            self.settings.update_settings("minimize", False)
        else:
            self.toolbar.minimize_cmd.checked = True
            self.settings.update_settings("minimize", True)

    def update_app_startup(self, sender, event):
        if self.toolbar.startup_cmd.checked:
            reg = self.utils.remove_from_startup()
            if reg:
                self.toolbar.startup_cmd.checked = False
                self.settings.update_settings("startup", False)
        else:
            reg = self.utils.add_to_startup()
            if reg:
                self.toolbar.startup_cmd.checked = True
                self.settings.update_settings("startup", True)

    def show_currencies_list(self, sender, event):
        self.currencies_window = Currency()
        self.currencies_window._impl.native.ShowDialog()

    def show_peer_info(self, sender, event):
        if not self.peer_toggle:
            peer_window = Peer(self)
            peer_window.show()
            self.peer_window = peer_window
            self.peer_toggle = True
        else:
            self.peer_window._impl.native.Activate()

    def show_add_node(self, sender, event):
        self.add_node_window = AddNode()
        self.add_node_window._impl.native.ShowDialog()

    def new_transparent_address(self, sender, event):
        self.app.add_background_task(self.generate_transparent_address)

    def new_private_address(self, sender, event):
        self.app.add_background_task(self.generate_private_address)

    async def generate_transparent_address(self, widget):
        async def on_result(widget, result):
            if result is None:
                if self.receive_page.transparent_toggle:
                    self.insert_new_address(new_address)
                if self.send_page.transparent_toggle:
                    await self.send_page.update_send_options(None)
                if self.mining_page.mining_toggle:
                    await self.mining_page.update_mining_options(None)
        new_address,_ = await self.commands.getNewAddress()
        if new_address:
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address}",
                on_result=on_result
            )

    async def generate_private_address(self, widget):
        async def on_result(widget, result):
            if result is None:
                if self.receive_page.private_toggle:
                    self.insert_new_address(new_address)
                if self.send_page.private_toggle:
                    await self.send_page.update_send_options(None)
        new_address,_ = await self.commands.z_getNewAddress()
        if new_address:
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address}",
                on_result=on_result
            )

    def insert_new_address(self, address):
        self.receive_page.addresses_table.add_row(
            index=0,
            row_data={0: address}
        )

    def edit_messages_username(self, sender, event):
        data = self.storage.is_exists()
        if data:
            username = self.storage.get_identity("username")
            if username:
                edit_window = EditUser(username[0])
                edit_window._impl.native.ShowDialog()


    def backup_messages(self, sender, event):
        def on_result(widget, result):
            if result:
                Os.File.Copy(str(data), str(result), True)
                self.info_dialog(
                    title="Backup Successful!",
                    message=f"Your messages have been successfully backed up to:\n{result}"
                )
        data = self.storage.is_exists()
        if data:
            self.save_file_dialog(
                title="Save backup to...",
                suggested_filename=data,
                file_types=["dat"],
                on_result=on_result
            )
                

    def check_app_version(self, sender, event):
        self.app.add_background_task(self.fetch_repo_info)

    async def fetch_repo_info(self, widget):
        def on_result(widget, result):
                if result is True:
                    webbrowser.open(self.git_link)
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
                    on_result=on_result
                )

    def show_import_key(self, sender, event):
        self.import_window = ImportKey(self)
        self.import_window._impl.native.ShowDialog()

    
    def export_wallet(self, sender, event):
        def on_result(widget, result):
            if result is True:
                self.set_export_dir()
        export_dir = self.utils.verify_export_dir()
        if export_dir:
            self.app.add_background_task(self.run_export_wallet)
        else:
            self.question_dialog(
                title="Missing Export Dir",
                message="The '-exportdir' option is not configured in your bitcoinz.conf file.\n"
                        "Would you like to configure it ?",
                on_result=on_result
            )

    def set_export_dir(self):
        def on_result(widget, result):
            if result is not None:
                self.utils.update_config(result)
                self.question_dialog(
                    title="Export Directory Set",
                    message="Your export folder has been successfully saved. Would you like to restart your node now to apply this change?",
                    on_result=self.restart_node
                )
        self.select_folder_dialog(
            title="Select Folder",
            on_result=on_result
        )
        

    async def restart_node(self, widget, result):
        if result is True:
            restart = self.utils.restart_app()
            if restart:
                await self.commands.stopNode()
                self.notify.hide()
                self.app.exit()


    async def run_export_wallet(self, widget):
        file_name = f"wallet{datetime.today().strftime('%d%m%Y%H%M%S')}"
        exported_file, error_message = await self.commands.z_ExportWallet(file_name)
        if exported_file and error_message is None:
            self.info_dialog(
                title="Wallet Exported Successfully",
                message=f"Your wallet has been exported as '{exported_file}'."
            )

    def show_import_wallet(self, sender, event):
        self.import_window = ImportWallet(self)
        self.import_window._impl.native.ShowDialog()


    def join_us(self, sender, event):
        discord = "https://discord.com/invite/aAU2WeJ"
        webbrowser.open(discord)


    def home_button_click(self, button):
        self.clear_buttons()
        self.home_button_toggle = True
        self.home_button.on_press = None
        home_a_icon = self.menu_icon("images/home_a.png")
        self.home_button._impl.native.Image = Drawing.Image.FromFile(home_a_icon)
        self.home_button.style.color = BLACK
        self.home_button.style.background_color = YELLOW
        self.pages.add(self.home_page)
        self.app.add_background_task(self.home_page.insert_widgets)


    def home_button_mouse_enter(self, sender, event):
        if self.home_button_toggle:
            return
        self.home_button.style.color = WHITE
        self.home_button.style.background_color = rgb(66,69,73)

    def home_button_mouse_leave(self, sender, event):
        if self.home_button_toggle:
            return
        self.home_button.style.color = GRAY
        self.home_button.style.background_color = rgb(30,33,36)

    def transactions_button_click(self, button):
        self.clear_buttons()
        self.transactions_button_toggle = True
        self.transactions_button.on_press = None
        transactions_a_icon = self.menu_icon("images/txs_a.png")
        self.transactions_button._impl.native.Image = Drawing.Image.FromFile(transactions_a_icon)
        self.transactions_button.style.color= BLACK
        self.transactions_button.style.background_color = YELLOW
        self.pages.add(self.transactions_page)
        self.app.add_background_task(self.transactions_page.insert_widgets)

    def transactions_button_mouse_enter(self, sender, event):
        if self.transactions_button_toggle:
            return
        self.transactions_button.style.color = WHITE
        self.transactions_button.style.background_color = rgb(66,69,73)

    def transactions_button_mouse_leave(self, sender, event):
        if self.transactions_button_toggle:
            return
        self.transactions_button.style.color = GRAY
        self.transactions_button.style.background_color = rgb(30,33,36)

    def receive_button_click(self, button):
        self.clear_buttons()
        self.receive_button_toggle = True
        self.receive_button.on_press = None
        receive_a_icon = self.menu_icon("images/receive_a.png")
        self.receive_button._impl.native.Image = Drawing.Image.FromFile(receive_a_icon)
        self.receive_button.style.color = BLACK
        self.receive_button.style.background_color = YELLOW
        self.pages.add(self.receive_page)
        self.app.add_background_task(self.receive_page.insert_widgets)

    def receive_button_mouse_enter(self, sender, event):
        if self.receive_button_toggle:
            return
        self.receive_button.style.color = WHITE
        self.receive_button.style.background_color = rgb(66,69,73)

    def receive_button_mouse_leave(self, sender, event):
        if self.receive_button_toggle:
            return
        self.receive_button.style.color = GRAY
        self.receive_button.style.background_color = rgb(30,33,36)

    def send_button_click(self, button):
        self.clear_buttons()
        self.send_button_toggle = True
        self.send_button.on_press = None
        send_a_icon = self.menu_icon("images/send_a.png")
        self.send_button._impl.native.Image = Drawing.Image.FromFile(send_a_icon)
        self.send_button.style.color = BLACK
        self.send_button.style.background_color = YELLOW
        self.pages.add(self.send_page)
        self.app.add_background_task(self.send_page.insert_widgets)

    def send_button_mouse_enter(self, sender, event):
        if self.send_button_toggle:
            return
        self.send_button.style.color = WHITE
        self.send_button.style.background_color = rgb(66,69,73)

    def send_button_mouse_leave(self, sender, event):
        if self.send_button_toggle:
            return
        self.send_button.style.color = GRAY
        self.send_button.style.background_color = rgb(30,33,36)

    def message_button_click(self, button):
        self.clear_buttons()
        self.message_button_toggle = True
        self.message_button.on_press = None
        message_a_icon = self.menu_icon("images/messages_a.png")
        self.message_button._impl.native.Image = Drawing.Image.FromFile(message_a_icon)
        self.message_button.style.color = BLACK
        self.message_button.style.background_color = YELLOW
        self.pages.add(self.message_page)
        self.app.add_background_task(self.message_page.insert_widgets)
    
    def message_button_mouse_enter(self, sender, event):
        if self.message_button_toggle:
            return
        self.message_button.style.color = WHITE
        self.message_button.style.background_color = rgb(66,69,73)

    def message_button_mouse_leave(self, sender, event):
        if self.message_button_toggle:
            return
        self.message_button.style.color = GRAY
        self.message_button.style.background_color = rgb(30,33,36)

    def mining_button_click(self, button):
        self.clear_buttons()
        self.mining_button_toggle = True
        self.mining_button.on_press = None
        mining_a_icon = self.menu_icon("images/mining_a.png")
        self.mining_button._impl.native.Image = Drawing.Image.FromFile(mining_a_icon)
        self.mining_button.style.color = BLACK
        self.mining_button.style.background_color = YELLOW
        self.pages.add(self.mining_page)
        self.app.add_background_task(self.mining_page.insert_widgets)

    def mining_button_mouse_enter(self, sender, event):
        if self.mining_button_toggle:
            return
        self.mining_button.style.color = WHITE
        self.mining_button.style.background_color = rgb(66,69,73)

    def mining_button_mouse_leave(self, sender, event):
        if self.mining_button_toggle:
            return
        self.mining_button.style.color = GRAY
        self.mining_button.style.background_color = rgb(30,33,36)

    def clear_buttons(self):
        if self.home_button_toggle:
            self.home_button_toggle = None
            self.pages.remove(self.home_page)
            home_i_icon = self.menu_icon("images/home_i.png")
            self.home_button._impl.native.Image = Drawing.Image.FromFile(home_i_icon)
            self.home_button.style.color = GRAY
            self.home_button.style.background_color = rgb(30,33,36)
            self.home_button.on_press = self.home_button_click

        elif self.transactions_button_toggle:
            self.transactions_button_toggle = None
            self.pages.remove(self.transactions_page)
            transactions_i_icon = self.menu_icon("images/txs_i.png")
            self.transactions_button._impl.native.Image = Drawing.Image.FromFile(transactions_i_icon)
            self.transactions_button.style.color = GRAY
            self.transactions_button.style.background_color = rgb(30,33,36)
            self.transactions_button.on_press = self.transactions_button_click

        elif self.receive_button_toggle:
            self.receive_button_toggle = None
            self.pages.remove(self.receive_page)
            receive_i_icon = self.menu_icon("images/receive_i.png")
            self.receive_button._impl.native.Image = Drawing.Image.FromFile(receive_i_icon)
            self.receive_button.style.color = GRAY
            self.receive_button.style.background_color = rgb(30,33,36)
            self.receive_button.on_press = self.receive_button_click

        elif self.send_button_toggle:
            self.send_button_toggle = None
            self.pages.remove(self.send_page)
            send_i_icon = self.menu_icon("images/send_i.png")
            self.send_button._impl.native.Image = Drawing.Image.FromFile(send_i_icon)
            self.send_button.style.color = GRAY
            self.send_button.style.background_color = rgb(30,33,36)
            self.send_button.on_press = self.send_button_click

        elif self.message_button_toggle:
            self.message_button_toggle = None
            self.pages.remove(self.message_page)
            message_i_icon = self.menu_icon("images/messages_i.png")
            self.message_button._impl.native.Image = Drawing.Image.FromFile(message_i_icon)
            self.message_button.style.color = GRAY
            self.message_button.style.background_color = rgb(30,33,36)
            self.message_button.on_press = self.message_button_click

        elif self.mining_button_toggle:
            self.mining_button_toggle = None
            self.pages.remove(self.mining_page)
            mining_i_icon = self.menu_icon("images/mining_i.png")
            self.mining_button._impl.native.Image = Drawing.Image.FromFile(mining_i_icon)
            self.mining_button.style.color = GRAY
            self.mining_button.style.background_color = rgb(30,33,36)
            self.mining_button.on_press = self.mining_button_click


    def menu_icon(self, path):
        return Os.Path.Combine(str(self.app.paths.app), path)

    
    def _handle_on_resize(self, sender, event:Sys.EventArgs):
        min_width = 916
        min_height = 646
        self._impl.native.MinimumSize = Drawing.Size(min_width, min_height)

        if self._impl.native.WindowState == FormState.NORMAL:
            self._is_minimized = False
        elif self._impl.native.WindowState == FormState.MINIMIZED:
            self._is_minimized = True


    def _handle_on_activated(self, sender, event):
        self._is_active = True

    def _handle_on_deactivated(self, sender, event):
        self._is_active = False
            

    def on_close_menu(self, widget):
        if self.settings.minimize_to_tray():
            if self.mining_page.mining_status:
                self.mining_page.notify.show()
            self.hide()
            self._is_hidden = True
            return
        self.toolbar.exit_app()