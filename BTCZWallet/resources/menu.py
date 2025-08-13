
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
    COLUMN, ROW, TOP, CENTER
)

from .toolbar import AppToolBar
from .status import AppStatusBar
from .notify import Notify, NotifyMining, NotifyMarket
from .wallet import Wallet, ImportKey, ImportWallet
from .home import Home, Currency, Languages
from .txs import Transactions
from .receive import Receive
from .send import Send
from .messages import Messages, EditUser
from .mining import Mining
from .storage import StorageMessages, StorageMarket
from .network import Peer, AddNode, TorConfig
from .marketplace import MarketPlace
from .server import MarketServer


class Menu(Window):
    def __init__(self, tor_enabled, settings, utils, units, commands, tr, font):
        super().__init__()

        self.tor_enabled = tor_enabled
        self._is_minimized = None
        self._is_hidden = None
        self.import_key_toggle = None
        self.peer_toggle = None
        self.marketplace_toggle = None

        self.commands = commands
        self.units = units
        self.settings = settings
        self.tr = tr
        self.utils = utils
        self.font = font

        self.title = self.tr.title("main_window")
        self.size = (900,607)
        self._impl.native.BackColor = Color.rgb(30,33,36)

        self.storage = StorageMessages(self.app)
        self.market_storage = StorageMarket(self.app)
        self.statusbar = AppStatusBar(self.app, self, settings, utils, units, commands, tr, font)
        self.wallet = Wallet(self.app, self, settings, units, commands, tr, font)

        self.home_page = Home(self.app, self, settings, utils, units, commands, tr, font)
        self.transactions_page = Transactions(self.app, self, settings, utils, units, commands, tr, font)
        self.receive_page = Receive(self.app, self, settings, utils, units, commands, tr, font)
        self.send_page = Send(self.app, self, settings, units, commands, tr, font)
        self.message_page = Messages(self.app, self, settings, utils, units, commands, tr, font)
        self.mining_page = Mining(self.app, self, settings, utils, units, commands, tr, font)
        self.notifymining = NotifyMining(font)
        self.notifymarket = NotifyMarket()
        self.notify = Notify(self.app, self, self.notifymarket, self.home_page, self.mining_page, settings, utils, commands, tr, font)
        self.toolbar = AppToolBar(self.app, self, self.notify, self.notifymarket, self.home_page, self.mining_page, settings, utils, commands, tr, font)
        self.server = MarketServer(self.app, settings=self.settings, notify=self.notifymarket)

        opacity = self.settings.opacity()
        if opacity:
            self._impl.native.Opacity = opacity
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self.on_close = self.on_close_menu
        self._impl.native.Resize += self._handle_on_resize
        self._impl.native.Activated += self._handle_on_activated
        self._impl.native.Deactivate += self._handle_on_deactivated

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
        if self.rtl:
            relation = Relation.TEXTBEFORIMAGE
            align = AlignContent.LEFT
        else:
            relation = Relation.IMAGEBEFORETEXT
            align = AlignContent.RIGHT
        self.home_button = Button(
            text=self.tr.text("home_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                flex = 1
            ),
            on_press=self.home_button_click
        )
        self.home_button._impl.native.Font = self.font.get(self.tr.size("home_button"), True)
        self.home_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.home_button._impl.native.TextImageRelation = relation
        self.home_button._impl.native.ImageAlign = align
        self.home_button._impl.native.MouseEnter += self.home_button_mouse_enter
        self.home_button._impl.native.MouseLeave += self.home_button_mouse_leave

        self.transactions_button = Button(
            text=self.tr.text("transactions_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                flex = 1
            ),
            on_press=self.transactions_button_click
        )
        transactions_i_icon = self.menu_icon("images/txs_i.png")
        self.transactions_button._impl.native.Font = self.font.get(self.tr.size("transactions_button"), True)
        self.transactions_button._impl.native.Image = Drawing.Image.FromFile(transactions_i_icon)
        self.transactions_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.transactions_button._impl.native.TextImageRelation = relation
        self.transactions_button._impl.native.ImageAlign = align
        self.transactions_button._impl.native.MouseEnter += self.transactions_button_mouse_enter
        self.transactions_button._impl.native.MouseLeave += self.transactions_button_mouse_leave

        self.receive_button = Button(
            text=self.tr.text("receive_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                flex = 1
            ),
            on_press=self.receive_button_click
        )
        receive_i_icon = self.menu_icon("images/receive_i.png")
        self.receive_button._impl.native.Font = self.font.get(self.tr.size("receive_button"), True)
        self.receive_button._impl.native.Image = Drawing.Image.FromFile(receive_i_icon)
        self.receive_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.receive_button._impl.native.TextImageRelation = relation
        self.receive_button._impl.native.ImageAlign = align
        self.receive_button._impl.native.MouseEnter += self.receive_button_mouse_enter
        self.receive_button._impl.native.MouseLeave += self.receive_button_mouse_leave

        self.send_button = Button(
            text=self.tr.text("send_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                flex = 1
            ),
            on_press=self.send_button_click
        )
        send_i_icon = self.menu_icon("images/send_i.png")
        self.send_button._impl.native.Font = self.font.get(self.tr.size("send_button"), True)
        self.send_button._impl.native.Image = Drawing.Image.FromFile(send_i_icon)
        self.send_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.send_button._impl.native.TextImageRelation = relation
        self.send_button._impl.native.ImageAlign = align
        self.send_button._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_button._impl.native.MouseLeave += self.send_button_mouse_leave

        self.message_button = Button(
            text=self.tr.text("messages_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                flex = 1
            ),
            on_press=self.message_button_click
        )
        message_i_icon = self.menu_icon("images/messages_i.png")
        self.message_button._impl.native.Font = self.font.get(self.tr.size("messages_button"), True)
        self.message_button._impl.native.Image = Drawing.Image.FromFile(message_i_icon)
        self.message_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.message_button._impl.native.TextImageRelation = relation
        self.message_button._impl.native.ImageAlign = align
        self.message_button._impl.native.MouseEnter += self.message_button_mouse_enter
        self.message_button._impl.native.MouseLeave += self.message_button_mouse_leave
        
        self.mining_button = Button(
            text=self.tr.text("mining_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                flex = 1
            ),
            on_press=self.mining_button_click
        )
        mining_i_icon = self.menu_icon("images/mining_i.png")
        self.mining_button._impl.native.Font = self.font.get(self.tr.size("mining_button"), True)
        self.mining_button._impl.native.Image = Drawing.Image.FromFile(mining_i_icon)
        self.mining_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.mining_button._impl.native.TextImageRelation = relation
        self.mining_button._impl.native.ImageAlign = align
        self.mining_button._impl.native.MouseEnter += self.mining_button_mouse_enter
        self.mining_button._impl.native.MouseLeave += self.mining_button_mouse_leave

        if self.rtl:
            self.menu_bar.add(
                self.mining_button,
                self.message_button,
                self.send_button,
                self.receive_button,
                self.transactions_button,
                self.home_button,
            )
        else:
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
        self.app.add_background_task(self.transactions_page.run_tasks)
        await asyncio.sleep(1)
        self.app.add_background_task(self.message_page.gather_unread_memos)
        await asyncio.sleep(1)
        self.app.add_background_task(self.updating_orders_status)

    def add_actions_cmds(self):
        if self.settings.hidden_balances():
            self.toolbar.hide_balances_cmd.checked = True
        else:
            self.toolbar.hide_balances_cmd.checked = self.settings.hidden_balances()
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

        self.toolbar.hide_balances_cmd.action = self.update_balances_visibility
        self.toolbar.notification_txs_cmd.action = self.update_notifications_txs
        self.toolbar.notification_messages_cmd.action = self.update_notifications_messages
        self.toolbar.minimize_cmd.action = self.update_minimize_to_tray
        self.toolbar.startup_cmd.action = self.update_app_startup
        self.toolbar.peer_info_cmd.action = self.show_peer_info
        self.toolbar.add_node_cmd.action = self.show_add_node
        self.toolbar.tor_config_cmd.action = self.show_tor_config
        self.toolbar.currency_cmd.action = self.show_currencies_list
        self.toolbar.languages_cmd.action = self.show_languages
        self.toolbar.generate_t_cmd.action = self.new_transparent_address
        self.toolbar.generate_z_cmd.action = self.new_private_address
        self.toolbar.check_update_cmd.action = self.check_app_version
        self.toolbar.join_us_cmd.action = self.join_us
        self.toolbar.import_key_cmd.action = self.show_import_key
        self.toolbar.export_wallet_cmd.action = self.export_wallet
        self.toolbar.import_wallet_cmd.action = self.show_import_wallet
        self.toolbar.edit_username_cmd.action = self.edit_messages_username
        self.toolbar.market_place_cmd.action = self.show_marketplace
        self.toolbar.backup_messages_cmd.action = self.backup_messages



    def update_balances_visibility(self, sender, event):
        if self.toolbar.hide_balances_cmd.checked:
            self.toolbar.hide_balances_cmd.checked = False
            self.settings.update_settings("hidden_balances", False)
        else:
            self.toolbar.hide_balances_cmd.checked = True
            self.settings.update_settings("hidden_balances", True)
        self.transactions_page.reload_transactions()


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
        self.currencies_window = Currency(self, self.settings, self.utils, self.tr, self.font)
        self.currencies_window._impl.native.ShowDialog(self._impl.native)

    def show_languages(self, sender, event):
        self.languages_window = Languages(self, self.settings, self.utils, self.tr, self.font)
        self.languages_window._impl.native.ShowDialog(self._impl.native)

    def show_peer_info(self, sender, event):
        if not self.peer_toggle:
            peer_window = Peer(
                self, self.settings, self.utils, self.units, self.commands, self.tr, self.font
            )
            self.peer_window = peer_window
            self.peer_toggle = True
        else:
            self.peer_window._impl.native.Activate()

    def show_add_node(self, sender, event):
        self.add_node_window = AddNode(
            self, self.utils, self.commands, self.tr, self.font
        )
        self.add_node_window._impl.native.ShowDialog(self._impl.native)

    def show_tor_config(self, sender, event):
        self.tor_config = TorConfig(
            self.settings, self.utils, self.commands, self.tr, self.font, main=self
        )
        self.tor_config._impl.native.ShowDialog(self._impl.native)

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
                    await self.mining_page.reload_addresses()
        new_address,_ = await self.commands.getNewAddress()
        if new_address:
            message = self.tr.message("newaddress_dialog")
            self.info_dialog(
                title=self.tr.title("newaddress_dialog"),
                message=f"{message} {new_address}",
                on_result=on_result
            )

    async def generate_private_address(self, widget):
        async def on_result(widget, result):
            if result is None:
                if self.receive_page.private_toggle:
                    self.insert_new_address(new_address)
                if self.send_page.private_toggle:
                    await self.send_page.update_send_options(None)
                if self.mining_page.mining_toggle:
                    await self.mining_page.reload_addresses()
        new_address,_ = await self.commands.z_getNewAddress()
        if new_address:
            message = self.tr.message("newaddress_dialog")
            self.info_dialog(
                title=self.tr.title("newaddress_dialog"),
                message=f"{message} {new_address}",
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
                edit_window = EditUser(self, username[0], self.settings, self.utils, self.tr, self.font)
                edit_window._impl.native.ShowDialog(self._impl.native)


    def show_marketplace(self, sender, event):
        if self.settings.market_service():
            if not self.marketplace_toggle:
                marketplace_window = MarketPlace(
                    self, self.notifymarket, self.settings, self.utils, self.units, self.commands, self.tr, self.font, self.server
                )
                marketplace_window.show()
                self.marketplace_window = marketplace_window
                self.marketplace_toggle = True
            else:
                self.marketplace_window._impl.native.Activate()
        else:
            self.error_dialog(
                title="Marketplace Disabled",
                message=(
                    "To access the marketplace, you need to enable the market server\n\n"
                    "  Network → Tor network\n"
                    "and enable the Market Server option"
                )
            )


    async def updating_orders_status(self, widget):
        while True:
            if self.settings.market_service():
                market_orders = self.market_storage.get_market_orders()
                if market_orders:
                    for order in market_orders:
                        order_id = order[0]
                        item_id = order[1]
                        order_quantity = order[4]
                        order_status = order[6]
                        order_expired = order[8]
                        if order_status in ("expired", "completed", "paid", "cancelled"):
                            continue

                        now = int(datetime.now().timestamp())
                        if order_expired < now:
                            self.market_storage.update_order_status(order_id, "expired")
                            item = self.market_storage.get_item(item_id)
                            quantity = order_quantity + item[6]
                            self.market_storage.update_item_quantity(item_id, quantity)

            await asyncio.sleep(5)


    def backup_messages(self, sender, event):
        def on_result(widget, result):
            if result:
                Os.File.Copy(str(data), str(result), True)
                message = self.tr.message("backupmessages_dialog")
                self.info_dialog(
                    title=self.tr.title("backupmessages_dialog"),
                    message=f"{message}\n{result}"
                )
        data = self.storage.is_exists()
        if data:
            self.save_file_dialog(
                title=self.tr.title("savefile_dialog"),
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
        git_version, link = await self.utils.get_repo_info(self.tor_enabled)
        if git_version:
            self.git_link = link
            current_version = self.app.version
            current_version_text = self.tr.text("current_version")
            if git_version == current_version:
                message = self.tr.message("checkupdates_dialog")
                self.info_dialog(
                    title=self.tr.title("checkupdates_dialog"),
                    message=f"{current_version_text} {current_version}\n{message}"
                )
            else:
                git_version_text = self.tr.text("git_version")
                message = self.tr.message("questionupdates_dialog")
                self.question_dialog(
                    title=self.tr.title("checkupdates_dialog"),
                    message=f"{current_version_text} {current_version}\n{git_version_text} {git_version}\n{message}",
                    on_result=on_result
                )

    def show_import_key(self, sender, event):
        self.import_window = ImportKey(
            self, self.settings, self.utils, self.commands, self.tr, self.font
        )
        self.import_window._impl.native.ShowDialog(self._impl.native)

    
    def export_wallet(self, sender, event):
        def on_result(widget, result):
            if result is True:
                self.set_export_dir()
        export_dir = self.utils.verify_export_dir()
        if export_dir:
            self.app.add_background_task(self.run_export_wallet)
        else:
            if self.mining_page.mining_status:
                return
            self.question_dialog(
                title=self.tr.title("missingexportdir_dialog"),
                message=self.tr.message("missingexportdir_dialog"),
                on_result=on_result
            )

    def set_export_dir(self):
        def on_result(widget, result):
            if result is not None:
                self.utils.update_config(result)
                self.question_dialog(
                    title=self.tr.title("exportdirset_dialog"),
                    message=self.tr.message("exportdirset_dialog"),
                    on_result=self.restart_node
                )
        self.select_folder_dialog(
            title=self.tr.title("selectfolder_dialog"),
            on_result=on_result
        )
        

    async def restart_node(self, widget, result):
        if result is True:
            restart = self.utils.restart_app()
            if restart:
                self.utils.stop_tor()
                await self.commands.stopNode()
                self.home_page.bitcoinz_curve.image = None
                self.home_page.clear_cache()
                self.notify.hide()
                self.notify.dispose()
                self.app.exit()


    async def run_export_wallet(self, widget):
        file_name = f"wallet{datetime.today().strftime('%d%m%Y%H%M%S')}"
        exported_file, error_message = await self.commands.z_ExportWallet(file_name)
        if exported_file and error_message is None:
            message = self.tr.message("walletexported_dialog")
            self.info_dialog(
                title=self.tr.title("walletexported_dialog"),
                message=f"{message} '{exported_file}'."
            )

    def show_import_wallet(self, sender, event):
        self.import_window = ImportWallet(
            self, self.settings, self.utils, self.commands, self.tr, self.font
        )
        self.import_window._impl.native.ShowDialog(self._impl.native)


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
                self.notifymining.show()
            self.hide()
            self._is_hidden = True
            return
        self.toolbar.exit_app()