
import psutil

from toga import App, Box, Window
from ..framework import (
    Toolbar, Command, Color, Keys
)
from toga.style.pack import Pack
from toga.constants import ROW, TOP


class AppToolBar(Box):
    def __init__(self, app:App, main:Window, notify, home_page ,mining_page, settings, commands, tr):
        super().__init__(
            style=Pack(
                direction = ROW,
                height = 24,
                alignment = TOP
            )
        )
        self.app = app
        self.main = main
        self.notify = notify
        self.home_page = home_page
        self.mining_page = mining_page

        self.commands = commands
        self.settings = settings
        self.tr = tr

        self.app_menu_active = None
        self.settings_menu_active = None
        self.opacity_cmd_active = None
        self.network_menu_active = None
        self.wallet_menu_active = None
        self.messages_menu_active = None
        self.help_menu_active = None
        self.generate_address_cmd_active = None

        self.toolbar = Toolbar(
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48)
        )

        self.about_cmd = Command(
            title=self.tr.text("about_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            icon="images/about_i.ico",
            mouse_enter=self.about_cmd_mouse_enter,
            mouse_leave=self.about_cmd_mouse_leave,
            action=self.display_about_dialog,
            tooltip=self.tr.tooltip("about_cmd")
        )
        self.exit_cmd = Command(
            title=self.tr.text("exit_cmd"),
            color=Color.RED,
            background_color=Color.rgb(40,43,48),
            icon="images/exit.ico",
            action=self.exit_app,
            shortcut_key=Keys.Alt | Keys.F4,
            tooltip=self.tr.tooltip("exit_cmd")
        )
        self.stop_exit_cmd = Command(
            title=self.tr.text("stop_exit_cmd"),
            color=Color.RED,
            background_color=Color.rgb(40,43,48),
            icon="images/stop.ico",
            action=self.stop_node_exit,
            shortcut_key=Keys.Control | Keys.Q,
            tooltip=self.tr.tooltip("stop_exit_cmd")
        )
        self.app_menu = Command(
            title=self.tr.text("app_menu"),
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

        self.currency_cmd = Command(
            title=self.tr.text("currency_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.currency_cmd_mouse_enter,
            mouse_leave=self.currency_cmd_mouse_leave,
            icon="images/currency_i.ico",
            shortcut_key=Keys.Control | Keys.Shift | Keys.C,
            tooltip=self.tr.tooltip("currency_cmd")
        )
        self.languages_cmd = Command(
            title=self.tr.text("languages_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.languages_cmd_mouse_enter,
            mouse_leave=self.languages_cmd_mouse_leave,
            icon="images/languages_i.ico",
            shortcut_key=Keys.Control | Keys.Shift | Keys.L,
            tooltip=self.tr.tooltip("languages_cmd")
        )
        self.opacity_50_cmd = Command(
            title=self.tr.text("opacity_50_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.opacity_50_cmd_mouse_enter,
            mouse_leave=self.opacity_50_cmd_mouse_leave,
            action=self.change_window_opacity_50
        )
        self.opacity_75_cmd = Command(
            title=self.tr.text("opacity_75_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.opacity_75_cmd_mouse_enter,
            mouse_leave=self.opacity_75_cmd_mouse_leave,
            action=self.change_window_opacity_75
        )
        self.opacity_100_cmd = Command(
            title=self.tr.text("opacity_100_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.opacity_100_cmd_mouse_enter,
            mouse_leave=self.opacity_100_cmd_mouse_leave,
            action=self.change_window_opacity_100
        )
        self.opacity_cmd = Command(
            title=self.tr.text("opacity_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            sub_commands=[
                self.opacity_50_cmd,
                self.opacity_75_cmd,
                self.opacity_100_cmd
            ],
            icon="images/opacity_i.ico",
            drop_opened=self.opacity_cmd_opened,
            drop_closed=self.opacity_cmd_closed,
            mouse_enter=self.opacity_cmd_mouse_enter,
            mouse_leave=self.opacity_cmd_mouse_leave
        )
        self.hide_balances_cmd = Command(
            title=self.tr.text("hide_balances_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.hide_balances_cmd_mouse_enter,
            mouse_leave=self.hide_balances_cmd_mouse_leave,
            tooltip=self.tr.tooltip("hide_balances_cmd")
        )
        self.notification_txs_cmd = Command(
            title=self.tr.text("notification_txs_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.notification_txs_cmd_mouse_enter,
            mouse_leave=self.notification_txs_cmd_mouse_leave,
            tooltip=self.tr.tooltip("notification_txs_cmd")
        )
        self.notification_messages_cmd = Command(
            title=self.tr.text("notification_messages_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.notification_messages_cmd_mouse_enter,
            mouse_leave=self.notification_messages_cmd_mouse_leave,
            tooltip=self.tr.tooltip("notification_messages_cmd")
        )
        self.minimize_cmd = Command(
            title=self.tr.text("minimize_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.minimize_cmd_mouse_enter,
            mouse_leave=self.minimize_cmd_mouse_leave,
            tooltip=self.tr.tooltip("minimize_cmd")
        )
        self.startup_cmd = Command(
            title=self.tr.text("startup_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.startup_cmd_mouse_enter,
            mouse_leave=self.startup_cmd_mouse_leave,
            tooltip=self.tr.tooltip("startup_cmd")
        )
        self.settings_menu = Command(
            title=self.tr.text("settings_menu"),
            sub_commands=[
                self.currency_cmd,
                self.languages_cmd,
                self.opacity_cmd,
                self.hide_balances_cmd,
                self.notification_txs_cmd,
                self.notification_messages_cmd,
                self.minimize_cmd,
                self.startup_cmd
            ],
            background_color=Color.rgb(40,43,48),
            drop_opened=self.settings_menu_opened,
            drop_closed=self.settings_menu_closed,
            mouse_enter=self.settings_menu_mouse_enter,
            mouse_leave=self.settings_menu_mouse_leave,
            icon="images/settings_i.ico"
        )

        self.peer_info_cmd = Command(
            title=self.tr.text("peer_info_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.peer_info_cmd_mouse_enter,
            mouse_leave=self.peer_info_cmd_mouse_leave,
            shortcut_key=Keys.Control | Keys.Shift | Keys.N,
            icon="images/peer_i.ico",
            tooltip=self.tr.tooltip("peer_info_cmd")
        )
        self.add_node_cmd = Command(
            title=self.tr.text("add_node_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.add_node_cmd_mouse_enter,
            mouse_leave=self.add_node_cmd_mouse_leave,
            icon="images/add_node_i.ico",
            tooltip=self.tr.tooltip("add_node_cmd")
        )
        self.tor_config_cmd = Command(
            title=self.tr.text("tor_config_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.tor_config_cmd_mouse_enter,
            mouse_leave=self.tor_config_cmd_mouse_leave,
            icon="images/tor_i.ico",
            tooltip=self.tr.tooltip("tor_config_cmd")
        )
        self.network_menu = Command(
            title=self.tr.text("network_menu"),
            sub_commands=[
                self.peer_info_cmd,
                self.add_node_cmd,
                self.tor_config_cmd
            ],
            background_color=Color.rgb(40,43,48),
            drop_opened=self.network_menu_opened,
            drop_closed=self.network_menu_closed,
            mouse_enter=self.network_menu_mouse_enter,
            mouse_leave=self.network_menu_mouse_leave,
            icon="images/network_i.ico"
        )

        self.generate_t_cmd = Command(
            title=self.tr.text("generate_t_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.generate_t_cmd_mouse_enter,
            mouse_leave=self.generate_t_cmd_mouse_leave,
            icon="images/transparent_i.ico",
            tooltip=self.tr.tooltip("generate_t_cmd")
        )
        self.generate_z_cmd = Command(
            title=self.tr.text("generate_z_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.generate_z_cmd_mouse_enter,
            mouse_leave=self.generate_z_cmd_mouse_leave,
            icon="images/private_i.ico",
            tooltip=self.tr.tooltip("generate_z_cmd")
        )
        self.generate_address_cmd = Command(
            title=self.tr.text("generate_address_cmd"),
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
            title=self.tr.text("importkey_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.import_key_cmd_mouse_enter,
            mouse_leave=self.import_key_cmd_mouse_leave,
            icon = "images/importkey_i.ico",
            tooltip=self.tr.tooltip("importkey_cmd")
        )
        self.export_wallet_cmd = Command(
            title=self.tr.text("export_wallet_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.export_wallet_cmd_mouse_enter,
            mouse_leave=self.export_wallet_cmd_mouse_leave,
            icon="images/export_i.ico",
            tooltip=self.tr.tooltip("export_wallet_cmd")
        )
        self.import_wallet_cmd = Command(
            title=self.tr.text("import_wallet_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.import_wallet_cmd_mouse_enter,
            mouse_leave=self.import_wallet_cmd_mouse_leave,
            icon="images/import_i.ico",
            tooltip=self.tr.tooltip("import_wallet_cmd")
        )
        self.wallet_menu = Command(
            title=self.tr.text("wallet_menu"),
            icon="images/wallet_i.ico",
            drop_opened=self.wallet_menu_opened,
            drop_closed=self.wallet_menu_closed,
            mouse_enter=self.wallet_menu_mouse_enter,
            mouse_leave=self.wallet_menu_mouse_leave,
            sub_commands=[
                self.generate_address_cmd,
                self.import_key_cmd,
                self.export_wallet_cmd,
                self.import_wallet_cmd
            ]
        )

        self.edit_username_cmd = Command(
            title=self.tr.text("edit_username_cmd"),
            icon="images/edit_username_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.edit_username_cmd_mouse_enter,
            mouse_leave=self.edit_username_cmd_mouse_leave,
            tooltip=self.tr.tooltip("edit_username_cmd")
        )
        self.backup_messages_cmd = Command(
            title=self.tr.text("backup_messages_cmd"),
            icon="images/backup_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.backup_messages_cmd_mouse_enter,
            mouse_leave=self.backup_messages_cmd_mouse_leave,
            tooltip=self.tr.tooltip("backup_messages_cmd")
        )
        self.messages_menu = Command(
            title=self.tr.text("messages_menu"),
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
            title=self.tr.text("check_update_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.check_update_cmd_mouse_enter,
            mouse_leave=self.check_update_cmd_mouse_leave,
            icon="images/update_i.ico",
            tooltip=self.tr.tooltip("check_update_cmd")
        )
        self.join_us_cmd = Command(
            title=self.tr.text("join_us_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.join_us_cmd_mouse_enter,
            mouse_leave=self.join_us_cmd_mouse_leave,
            icon="images/discord_i.ico",
            tooltip=self.tr.tooltip("join_us_cmd")
        )
        self.help_menu = Command(
            title=self.tr.text("help_menu"),
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
                self.settings_menu,
                self.network_menu,
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

    def settings_menu_mouse_enter(self):
        self.settings_menu.icon = "images/settings_a.ico"
        self.settings_menu.color = Color.BLACK

    def settings_menu_mouse_leave(self):
        if self.settings_menu_active:
            return
        self.settings_menu.icon = "images/settings_i.ico"
        self.settings_menu.color = Color.WHITE

    def network_menu_mouse_enter(self):
        self.network_menu.icon = "images/network_a.ico"
        self.network_menu.color = Color.BLACK

    def network_menu_mouse_leave(self):
        if self.network_menu_active:
            return
        self.network_menu.icon = "images/network_i.ico"
        self.network_menu.color = Color.WHITE

    def settings_menu_opened(self):
        self.settings_menu_active = True
        self.settings_menu.icon = "images/settings_a.ico"
        self.settings_menu.color = Color.BLACK

    def settings_menu_closed(self):
        self.settings_menu_active = False
        self.settings_menu.icon = "images/settings_i.ico"
        self.settings_menu.color = Color.WHITE

    def network_menu_opened(self):
        self.network_menu_active = True
        self.network_menu.icon = "images/network_a.ico"
        self.network_menu.color = Color.BLACK

    def network_menu_closed(self):
        self.network_menu_active = False
        self.network_menu.icon = "images/network_i.ico"
        self.network_menu.color = Color.WHITE

    def peer_info_cmd_mouse_enter(self):
        self.peer_info_cmd.icon = "images/peer_a.ico"
        self.peer_info_cmd.color = Color.BLACK

    def peer_info_cmd_mouse_leave(self):
        self.peer_info_cmd.icon = "images/peer_i.ico"
        self.peer_info_cmd.color = Color.WHITE

    def add_node_cmd_mouse_enter(self):
        self.add_node_cmd.icon = "images/add_node_a.ico"
        self.add_node_cmd.color = Color.BLACK

    def add_node_cmd_mouse_leave(self):
        self.add_node_cmd.icon = "images/add_node_i.ico"
        self.add_node_cmd.color = Color.WHITE

    def tor_config_cmd_mouse_enter(self):
        self.tor_config_cmd.icon = "images/tor_a.ico"
        self.tor_config_cmd.color = Color.BLACK

    def tor_config_cmd_mouse_leave(self):
        self.tor_config_cmd.icon = "images/tor_i.ico"
        self.tor_config_cmd.color = Color.WHITE

    def currency_cmd_mouse_enter(self):
        self.currency_cmd.icon = "images/currency_a.ico"
        self.currency_cmd.color = Color.BLACK

    def currency_cmd_mouse_leave(self):
        self.currency_cmd.icon = "images/currency_i.ico"
        self.currency_cmd.color = Color.WHITE

    def languages_cmd_mouse_enter(self):
        self.languages_cmd.icon = "images/languages_a.ico"
        self.languages_cmd.color = Color.BLACK

    def languages_cmd_mouse_leave(self):
        self.languages_cmd.icon = "images/languages_i.ico"
        self.languages_cmd.color = Color.WHITE

    def hide_balances_cmd_mouse_enter(self):
        self.hide_balances_cmd.color = Color.BLACK

    def hide_balances_cmd_mouse_leave(self):
        self.hide_balances_cmd.color = Color.WHITE

    def notification_txs_cmd_mouse_enter(self):
        self.notification_txs_cmd.color = Color.BLACK

    def notification_txs_cmd_mouse_leave(self):
        self.notification_txs_cmd.color = Color.WHITE

    def notification_messages_cmd_mouse_enter(self):
        self.notification_messages_cmd.color = Color.BLACK

    def notification_messages_cmd_mouse_leave(self):
        self.notification_messages_cmd.color = Color.WHITE

    def minimize_cmd_mouse_enter(self):
        self.minimize_cmd.color = Color.BLACK

    def minimize_cmd_mouse_leave(self):
        self.minimize_cmd.color = Color.WHITE

    def startup_cmd_mouse_enter(self):
        self.startup_cmd.color = Color.BLACK

    def startup_cmd_mouse_leave(self):
        self.startup_cmd.color = Color.WHITE

    def opacity_cmd_opened(self):
        self.opacity_cmd_active = True
        self.opacity_cmd.icon = "images/opacity_a.ico"
        self.opacity_cmd.color = Color.BLACK

    def opacity_cmd_closed(self):
        self.opacity_cmd_active = False
        self.opacity_cmd.icon = "images/opacity_i.ico"
        self.opacity_cmd.color = Color.WHITE

    def opacity_cmd_mouse_enter(self):
        self.opacity_cmd.icon = "images/opacity_a.ico"
        self.opacity_cmd.color = Color.BLACK

    def opacity_cmd_mouse_leave(self):
        if self.opacity_cmd_active:
            return
        self.opacity_cmd.icon = "images/opacity_i.ico"
        self.opacity_cmd.color = Color.WHITE

    def opacity_50_cmd_mouse_enter(self):
        self.opacity_50_cmd.color = Color.BLACK

    def opacity_50_cmd_mouse_leave(self):
        self.opacity_50_cmd.color = Color.WHITE

    def opacity_75_cmd_mouse_enter(self):
        self.opacity_75_cmd.color = Color.BLACK

    def opacity_75_cmd_mouse_leave(self):
        self.opacity_75_cmd.color = Color.WHITE

    def opacity_100_cmd_mouse_enter(self):
        self.opacity_100_cmd.color = Color.BLACK

    def opacity_100_cmd_mouse_leave(self):
        self.opacity_100_cmd.color = Color.WHITE

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

    def export_wallet_cmd_mouse_enter(self):
        self.export_wallet_cmd.icon = "images/export_a.ico"
        self.export_wallet_cmd.color = Color.BLACK

    def export_wallet_cmd_mouse_leave(self):
        self.export_wallet_cmd.icon = "images/export_i.ico"
        self.export_wallet_cmd.color = Color.WHITE

    def import_wallet_cmd_mouse_enter(self):
        self.import_wallet_cmd.icon = "images/import_a.ico"
        self.import_wallet_cmd.color = Color.BLACK

    def import_wallet_cmd_mouse_leave(self):
        self.import_wallet_cmd.icon = "images/import_i.ico"
        self.import_wallet_cmd.color = Color.WHITE

    def change_window_opacity_50(self):
        self.main._impl.native.Opacity = 0.5
        if self.main.peer_toggle:
            self.main.peer_window._impl.native.Opacity = 0.5
        self.settings.update_settings("opacity", 0.5)

    def change_window_opacity_75(self):
        self.main._impl.native.Opacity = 0.75
        if self.main.peer_toggle:
            self.main.peer_window._impl.native.Opacity = 0.75
        self.settings.update_settings("opacity", 0.75)

    def change_window_opacity_100(self):
        self.main._impl.native.Opacity = 1
        if self.main.peer_toggle:
            self.main.peer_window._impl.native.Opacity = 1
        self.settings.update_settings("opacity", 1)

    def display_about_dialog(self):
        self.app.about()

    def exit_app(self):
        def on_result(widget, result):
            if result is True:
                self.home_page.bitcoinz_curve.image = None
                self.home_page.clear_cache()
                self.notify.hide()
                self.notify.dispose()
                self.app.exit()
        if self.mining_page.mining_status:
            return
        self.main.question_dialog(
            title=self.tr.title("exit_dialog"),
            message=self.tr.message("exit_dialog"),
            on_result=on_result
        )

    def stop_tor(self):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "tor.exe":
                    proc.kill()
        except Exception as e:
            pass
        

    def stop_node_exit(self):
        async def on_result(widget, result):
            if result is True:
                self.stop_tor()
                await self.commands.stopNode()
                self.home_page.bitcoinz_curve.image = None
                self.home_page.clear_cache()
                self.notify.hide()
                self.notify.dispose()
                self.app.exit()

        if self.mining_page.mining_status:
            return
        self.main.question_dialog(
            title=self.tr.title("stopexit_dialog"),
            message=self.tr.message("stopexit_dialog"),
            on_result=on_result
        )