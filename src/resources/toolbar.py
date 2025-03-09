
from toga import App, Box
from ..framework import (
    Toolbar, Command, Color, run_async
)
from toga.style.pack import Pack
from toga.constants import ROW, TOP

from .client import Client
from .utils import Utils

class AppToolBar(Box):
    def __init__(self, app:App, notify, home_page ,mining_page):
        super().__init__(
            style=Pack(
                direction = ROW,
                height = 24,
                alignment = TOP
            )
        )
        self.app = app
        self.notify = notify
        self.home_page = home_page
        self.mining_page = mining_page
        self.commands = Client(self.app)
        self.utils = Utils(self.app)

        self.app_menu_active = None
        self.wallet_menu_active = None
        self.messages_menu_active = None
        self.help_menu_active = None
        self.generate_address_cmd_active = None

        self.toolbar = Toolbar(
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48)
        )

        self.about_cmd = Command(
            title="About",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            icon="images/about_i.ico",
            mouse_enter=self.about_cmd_mouse_enter,
            mouse_leave=self.about_cmd_mouse_leave,
            action=self.display_about_dialog
        )
        self.exit_cmd = Command(
            title="Exit",
            color=Color.RED,
            background_color=Color.rgb(40,43,48),
            icon="images/exit.ico",
            action=self.exit_app
        )
        self.stop_exit_cmd = Command(
            title="Stop node",
            color=Color.RED,
            background_color=Color.rgb(40,43,48),
            icon="images/stop.ico",
            action=self.stop_node_exit
        )
        self.app_menu = Command(
            title="App",
            sub_commands=[
                self.about_cmd,
                self.exit_cmd,
                self.stop_exit_cmd
            ],
            icon="images/app_i.ico",
            drop_opened=self.app_menu_opened,
            drop_closed=self.app_menu_closed,
            mouse_enter=self.app_menu_mouse_enter,
            mouse_leave=self.app_menu_mouse_leave
        )
        self.generate_t_cmd = Command(
            title="Transparent address",
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.generate_t_cmd_mouse_enter,
            mouse_leave=self.generate_t_cmd_mouse_leave,
            icon="images/transparent_i.ico"
        )
        self.generate_z_cmd = Command(
            title="Private address",
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.generate_z_cmd_mouse_enter,
            mouse_leave=self.generate_z_cmd_mouse_leave,
            icon="images/private_i.ico"
        )
        self.generate_address_cmd = Command(
            title="Generate address",
            sub_commands=[
                self.generate_t_cmd,
                self.generate_z_cmd
            ],
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            drop_opened=self.generate_address_cmd_opened,
            drop_closed=self.generate_address_cmd_closed,
            mouse_enter=self.generate_address_cmd_mouse_enter,
            mouse_leave=self.generate_address_cmd_mouse_leave,
            icon="images/new_addr_i.ico"
        )
        self.import_key_cmd = Command(
            title="Import private key",
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.import_key_cmd_mouse_enter,
            mouse_leave=self.import_key_cmd_mouse_leave,
            icon = "images/importkey_i.ico"
        )
        self.wallet_menu = Command(
            title="Wallet",
            icon="images/wallet_i.ico",
            drop_opened=self.wallet_menu_opened,
            drop_closed=self.wallet_menu_closed,
            mouse_enter=self.wallet_menu_mouse_enter,
            mouse_leave=self.wallet_menu_mouse_leave,
            sub_commands=[
                self.generate_address_cmd,
                self.import_key_cmd
            ]
        )
        self.edit_username_cmd = Command(
            title="Edit username",
            icon="images/edit_username_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.edit_username_cmd_mouse_enter,
            mouse_leave=self.edit_username_cmd_mouse_leave,
        )
        self.backup_messages_cmd = Command(
            title="Backup messages",
            icon="images/backup_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.backup_messages_cmd_mouse_enter,
            mouse_leave=self.backup_messages_cmd_mouse_leave
        )
        self.messages_menu = Command(
            title="Messages",
            icon="images/messages_conf_i.ico",
            drop_opened=self.messages_menu_opened,
            drop_closed=self.messages_menu_closed,
            mouse_enter=self.messages_menu_mouse_enter,
            mouse_leave=self.messages_menu_mouse_leave,
            sub_commands=[
                self.edit_username_cmd,
                self.backup_messages_cmd
            ]
        )
        self.check_update_cmd = Command(
            title="Check update",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.check_update_cmd_mouse_enter,
            mouse_leave=self.check_update_cmd_mouse_leave,
            icon="images/update_i.ico"
        )
        self.join_us_cmd = Command(
            title="Join us",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.join_us_cmd_mouse_enter,
            mouse_leave=self.join_us_cmd_mouse_leave,
            icon="images/discord_i.ico"
        )
        self.help_menu = Command(
            title="Help",
            sub_commands=[
                self.check_update_cmd,
                self.join_us_cmd
            ],
            icon="images/help_i.ico",
            drop_opened=self.help_menu_opened,
            drop_closed=self.help_menu_closed,
            mouse_enter=self.help_menu_mouse_enter,
            mouse_leave=self.help_menu_mouse_leave
        )
        self.toolbar.add_command(
            [
                self.app_menu,
                self.wallet_menu,
                self.messages_menu,
                self.help_menu
            ]
        )
        self._impl.native.Controls.Add(self.toolbar)

    def app_menu_opened(self):
        self.app_menu_active = True
        self.app_menu.icon = "images/app_a.ico"
        self.app_menu.color = Color.BLACK

    def app_menu_closed(self):
        self.app_menu_active = False
        self.app_menu.icon = "images/app_i.ico"
        self.app_menu.color = Color.WHITE

    def app_menu_mouse_enter(self):
        self.app_menu.icon = "images/app_a.ico"
        self.app_menu.color = Color.BLACK

    def app_menu_mouse_leave(self):
        if self.app_menu_active:
            return
        self.app_menu.icon = "images/app_i.ico"
        self.app_menu.color = Color.WHITE

    def wallet_menu_opened(self):
        self.wallet_menu_active = True
        self.wallet_menu.icon = "images/wallet_a.ico"
        self.wallet_menu.color = Color.BLACK

    def wallet_menu_closed(self):
        self.wallet_menu_active = False
        self.wallet_menu.icon = "images/wallet_i.ico"
        self.wallet_menu.color = Color.WHITE

    def wallet_menu_mouse_enter(self):
        self.wallet_menu.icon = "images/wallet_a.ico"
        self.wallet_menu.color = Color.BLACK

    def wallet_menu_mouse_leave(self):
        if self.wallet_menu_active:
            return
        self.wallet_menu.icon = "images/wallet_i.ico"
        self.wallet_menu.color = Color.WHITE

    def messages_menu_opened(self):
        self.messages_menu_active = True
        self.messages_menu.icon = "images/messages_conf_a.ico"
        self.messages_menu.color = Color.BLACK

    def messages_menu_closed(self):
        self.messages_menu_active = False
        self.messages_menu.icon = "images/messages_conf_i.ico"
        self.messages_menu.color = Color.WHITE

    def messages_menu_mouse_enter(self):
        self.messages_menu.icon = "images/messages_conf_a.ico"
        self.messages_menu.color = Color.BLACK

    def messages_menu_mouse_leave(self):
        if self.messages_menu_active:
            return
        self.messages_menu.icon = "images/messages_conf_i.ico"
        self.messages_menu.color = Color.WHITE

    def generate_address_cmd_opened(self):
        self.generate_address_cmd_active = True
        self.generate_address_cmd.icon = "images/new_addr_a.ico"
        self.generate_address_cmd.color = Color.BLACK

    def generate_address_cmd_closed(self):
        self.generate_address_cmd_active = False
        self.generate_address_cmd.icon = "images/new_addr_i.ico"
        self.generate_address_cmd.color = Color.WHITE

    def generate_address_cmd_mouse_enter(self):
        self.generate_address_cmd.icon = "images/new_addr_a.ico"
        self.generate_address_cmd.color = Color.BLACK

    def generate_address_cmd_mouse_leave(self):
        if self.generate_address_cmd_active:
            return
        self.generate_address_cmd.icon = "images/new_addr_i.ico"
        self.generate_address_cmd.color = Color.WHITE

    def generate_t_cmd_mouse_enter(self):
        self.generate_t_cmd.icon = "images/transparent_a.ico"
        self.generate_t_cmd.color = Color.BLACK

    def generate_t_cmd_mouse_leave(self):
        self.generate_t_cmd.icon = "images/transparent_i.ico"
        self.generate_t_cmd.color = Color.WHITE

    def generate_z_cmd_mouse_enter(self):
        self.generate_z_cmd.icon = "images/private_a.ico"
        self.generate_z_cmd.color = Color.BLACK

    def generate_z_cmd_mouse_leave(self):
        self.generate_z_cmd.icon = "images/private_i.ico"
        self.generate_z_cmd.color = Color.WHITE

    def edit_username_cmd_mouse_enter(self):
        self.edit_username_cmd.icon = "images/edit_username_a.ico"
        self.edit_username_cmd.color = Color.BLACK

    def edit_username_cmd_mouse_leave(self):
        self.edit_username_cmd.icon = "images/edit_username_i.ico"
        self.edit_username_cmd.color = Color.WHITE

    def backup_messages_cmd_mouse_enter(self):
        self.backup_messages_cmd.icon = "images/backup_a.ico"
        self.backup_messages_cmd.color = Color.BLACK

    def backup_messages_cmd_mouse_leave(self):
        self.backup_messages_cmd.icon = "images/backup_i.ico"
        self.backup_messages_cmd.color = Color.WHITE

    def check_update_cmd_mouse_enter(self):
        self.check_update_cmd.icon = "images/update_a.ico"
        self.check_update_cmd.color = Color.BLACK

    def check_update_cmd_mouse_leave(self):
        self.check_update_cmd.icon = "images/update_i.ico"
        self.check_update_cmd.color = Color.WHITE

    def join_us_cmd_mouse_enter(self):
        self.join_us_cmd.icon = "images/discord_a.ico"
        self.join_us_cmd.color = Color.BLACK

    def join_us_cmd_mouse_leave(self):
        self.join_us_cmd.icon = "images/discord_i.ico"
        self.join_us_cmd.color = Color.WHITE

    def help_menu_opened(self):
        self.help_menu_active = True
        self.help_menu.icon = "images/help_a.ico"
        self.help_menu.color = Color.BLACK

    def help_menu_closed(self):
        self.help_menu_active = False
        self.help_menu.icon = "images/help_i.ico"
        self.help_menu.color = Color.WHITE

    def help_menu_mouse_enter(self):
        self.help_menu.icon = "images/help_a.ico"
        self.help_menu.color = Color.BLACK

    def help_menu_mouse_leave(self):
        if self.help_menu_active:
            return
        self.help_menu.icon = "images/help_i.ico"
        self.help_menu.color = Color.WHITE

    def about_cmd_mouse_enter(self):
        self.about_cmd.icon = "images/about_a.ico"
        self.about_cmd.color = Color.BLACK

    def about_cmd_mouse_leave(self):
        self.about_cmd.icon = "images/about_i.ico"
        self.about_cmd.color = Color.WHITE

    def import_key_cmd_mouse_enter(self):
        self.import_key_cmd.icon = "images/importkey_a.ico"
        self.import_key_cmd.color = Color.BLACK

    def import_key_cmd_mouse_leave(self):
        self.import_key_cmd.icon = "images/importkey_i.ico"
        self.import_key_cmd.color = Color.WHITE

    def display_about_dialog(self):
        self.app.about()

    def exit_app(self):
        if self.mining_page.mining_status:
            return
        self.home_page.bitcoinz_curve.image = None
        self.home_page.clear_cache()
        self.notify.hide()
        self.app.exit()

    def stop_node_exit(self):
        if self.mining_page.mining_status:
            return
        run_async(self.commands.stopNode())
        self.home_page.bitcoinz_curve.image = None
        self.home_page.clear_cache()
        self.notify.hide()
        self.app.exit()