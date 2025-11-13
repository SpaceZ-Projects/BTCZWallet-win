
from toga import App, Box, Window, ImageView
from ..framework import (
    Toolbar, Command, Color, Keys, Separator,
    Forms, ToolTip
)
from toga.style.pack import Pack
from toga.constants import ROW, TOP, CENTER, COLUMN
from toga.colors import rgb, RED, GRAY


class AppToolBar(Box):
    def __init__(self, app:App, main:Window, settings, utils, commands, tr, font):
        super().__init__(
            style=Pack(
                direction = ROW,
                height = 26,
                alignment = TOP
            )
        )
        self.app = app
        self.main = main

        self.commands = commands
        self.settings = settings
        self.utils = utils
        self.tr = tr
        self.font = font

        self.tooltip = ToolTip()

        self.app_menu_active = None
        self.settings_menu_active = None
        self.opacity_cmd_active = None
        self.network_menu_active = None
        self.wallet_menu_active = None
        self.messages_menu_active = None
        self.help_menu_active = None
        self.generate_address_cmd_active = None

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.bitcoinz_label = ImageView(
            image="images/btcz_label.png",
            style=Pack(
                background_color=rgb(40,43,48),
                width = 70,
                height = 26,
                padding = (3,5,0,10)
            )
        )

        self.bitcoinz_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(40,43,48),
                alignment = CENTER,
                height = 26
            )
        )

        self.toolbar = Toolbar(
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            rtl = self.rtl
        )

        self.toolbar_box = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(40,43,48),
                flex = 1
            )
        )

        self.minimize_icon = ImageView(
            image="images/minimize.png",
            style=Pack(
                background_color=rgb(40,43,48),
                width = 22,
                padding = (0,0,0,11)
            )
        )
        self.tooltip.insert(self.minimize_icon._impl.native, "Minimize")
        self.minimize_icon._impl.native.MouseEnter += self.minimize_control_mouse_enter
        self.minimize_icon._impl.native.MouseLeave += self.minimize_control_mouse_leave

        self.minimize_control = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(40,43,48),
                width = 44,
                height = 26,
                alignment = CENTER
            )
        )
        self.tooltip.insert(self.minimize_control._impl.native, "Minimize")
        self.minimize_control._impl.native.MouseEnter += self.minimize_control_mouse_enter
        self.minimize_control._impl.native.MouseLeave += self.minimize_control_mouse_leave

        self.resize_icon = ImageView(
            image="images/maximize.png",
            style=Pack(
                background_color=rgb(40,43,48),
                width = 22,
                padding = (0,0,0,11)
            )
        )
        self.tooltip.insert(self.resize_icon._impl.native, "Maximize")
        self.resize_icon._impl.native.MouseEnter += self.resize_control_mouse_enter
        self.resize_icon._impl.native.MouseLeave += self.resize_control_mouse_leave

        self.resize_control = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(40,43,48),
                width = 44,
                height = 26,
                alignment = CENTER
            )
        )
        self.tooltip.insert(self.resize_control._impl.native, "Maximize")
        self.resize_control._impl.native.MouseEnter += self.resize_control_mouse_enter
        self.resize_control._impl.native.MouseLeave += self.resize_control_mouse_leave

        self.close_icon = ImageView(
            image="images/exit_i.png",
            style=Pack(
                background_color=rgb(40,43,48),
                width = 22,
                padding = (0,0,0,11)
            )
        )
        self.tooltip.insert(self.close_icon._impl.native, "Close")
        self.close_icon._impl.native.MouseEnter += self.close_control_mouse_enter
        self.close_icon._impl.native.MouseLeave += self.close_control_mouse_leave

        self.close_control = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(40,43,48),
                width = 44,
                height = 26,
                alignment = CENTER
            )
        )
        self.tooltip.insert(self.close_control._impl.native, "Close")
        self.close_control._impl.native.MouseEnter += self.close_control_mouse_enter
        self.close_control._impl.native.MouseLeave += self.close_control_mouse_leave

        self.controls_box = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(40,43,48)
            )
        )

        self.about_cmd = Command(
            title=self.tr.text("about_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            icon="images/about_i.ico",
            mouse_enter=self.about_cmd_mouse_enter,
            mouse_leave=self.about_cmd_mouse_leave,
            action=self.display_about_dialog,
            tooltip=self.tr.tooltip("about_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.app_console_cmd = Command(
            title="Console",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            icon="images/console_i.ico",
            mouse_enter=self.app_console_cmd_mouse_enter,
            mouse_leave=self.app_console_cmd_mouse_leave,
            shortcut_key=Keys.F12,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.mobile_wallet_cmd = Command(
            title="Mobile server",
            background_color=Color.rgb(40,43,48),
            icon="images/mobile_i.ico",
            color=Color.WHITE,
            mouse_enter=self.mobile_wallet_cmd_mouse_enter,
            mouse_leave=self.mobile_wallet_cmd_mouse_leave,
            shortcut_key=Keys.Control | Keys.Shift | Keys.M,
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.restart_cmd = Command(
            title="Restart",
            color=Color.YELLOW,
            background_color=Color.rgb(40,43,48),
            icon="images/restart_i.ico",
            mouse_enter=self.restart_cmd_mouse_enter,
            mouse_leave=self.restart_cmd_mouse_leave,
            shortcut_key=Keys.Control | Keys.R,
            action=lambda : self.exit_app("restart"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.exit_cmd = Command(
            title=self.tr.text("exit_cmd"),
            color=Color.RED,
            background_color=Color.rgb(40,43,48),
            icon="images/exit.ico",
            action=lambda : self.exit_app("default"),
            shortcut_key=Keys.Alt | Keys.F4,
            tooltip=self.tr.tooltip("exit_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.stop_exit_cmd = Command(
            title=self.tr.text("stop_exit_cmd"),
            color=Color.RED,
            background_color=Color.rgb(40,43,48),
            icon="images/stop.ico",
            action=lambda : self.exit_app("full"),
            shortcut_key=Keys.Control | Keys.Q,
            tooltip=self.tr.tooltip("stop_exit_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.app_menu = Command(
            title=self.tr.text("app_menu"),
            sub_commands=[
                self.about_cmd,
                self.app_console_cmd,
                self.mobile_wallet_cmd,
                Separator(),
                self.restart_cmd,
                self.exit_cmd,
                self.stop_exit_cmd
            ],
            icon="images/app_i.ico",
            drop_opened=self.app_menu_opened,
            drop_closed=self.app_menu_closed,
            mouse_enter=self.app_menu_mouse_enter,
            mouse_leave=self.app_menu_mouse_leave,
            font=self.font.get(9),
            rtl = self.rtl
        )

        self.currency_cmd = Command(
            title=self.tr.text("currency_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.currency_cmd_mouse_enter,
            mouse_leave=self.currency_cmd_mouse_leave,
            icon="images/currency_i.ico",
            shortcut_key=Keys.Control | Keys.Shift | Keys.C,
            tooltip=self.tr.tooltip("currency_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.languages_cmd = Command(
            title=self.tr.text("languages_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.languages_cmd_mouse_enter,
            mouse_leave=self.languages_cmd_mouse_leave,
            icon="images/languages_i.ico",
            shortcut_key=Keys.Control | Keys.Shift | Keys.L,
            tooltip=self.tr.tooltip("languages_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.opacity_50_cmd = Command(
            title=self.tr.text("opacity_50_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.opacity_50_cmd_mouse_enter,
            mouse_leave=self.opacity_50_cmd_mouse_leave,
            action=self.change_window_opacity_50,
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.opacity_75_cmd = Command(
            title=self.tr.text("opacity_75_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.opacity_75_cmd_mouse_enter,
            mouse_leave=self.opacity_75_cmd_mouse_leave,
            action=self.change_window_opacity_75,
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.opacity_100_cmd = Command(
            title=self.tr.text("opacity_100_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.opacity_100_cmd_mouse_enter,
            mouse_leave=self.opacity_100_cmd_mouse_leave,
            action=self.change_window_opacity_100,
            font=self.font.get(9),
            rtl = self.rtl
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
            mouse_leave=self.opacity_cmd_mouse_leave,
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.hide_balances_cmd = Command(
            title=self.tr.text("hide_balances_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.hide_balances_cmd_mouse_enter,
            mouse_leave=self.hide_balances_cmd_mouse_leave,
            tooltip=self.tr.tooltip("hide_balances_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.notification_txs_cmd = Command(
            title=self.tr.text("notification_txs_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.notification_txs_cmd_mouse_enter,
            mouse_leave=self.notification_txs_cmd_mouse_leave,
            tooltip=self.tr.tooltip("notification_txs_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.notification_messages_cmd = Command(
            title=self.tr.text("notification_messages_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.notification_messages_cmd_mouse_enter,
            mouse_leave=self.notification_messages_cmd_mouse_leave,
            tooltip=self.tr.tooltip("notification_messages_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.minimize_cmd = Command(
            title=self.tr.text("minimize_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.minimize_cmd_mouse_enter,
            mouse_leave=self.minimize_cmd_mouse_leave,
            tooltip=self.tr.tooltip("minimize_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.startup_cmd = Command(
            title=self.tr.text("startup_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.startup_cmd_mouse_enter,
            mouse_leave=self.startup_cmd_mouse_leave,
            tooltip=self.tr.tooltip("startup_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
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
            icon="images/settings_i.ico",
            font=self.font.get(9),
            rtl = self.rtl
        )

        self.peer_info_cmd = Command(
            title=self.tr.text("peer_info_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.peer_info_cmd_mouse_enter,
            mouse_leave=self.peer_info_cmd_mouse_leave,
            shortcut_key=Keys.Control | Keys.Shift | Keys.N,
            icon="images/peer_i.ico",
            tooltip=self.tr.tooltip("peer_info_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.add_node_cmd = Command(
            title=self.tr.text("add_node_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.add_node_cmd_mouse_enter,
            mouse_leave=self.add_node_cmd_mouse_leave,
            icon="images/add_node_i.ico",
            tooltip=self.tr.tooltip("add_node_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.tor_config_cmd = Command(
            title=self.tr.text("tor_config_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.tor_config_cmd_mouse_enter,
            mouse_leave=self.tor_config_cmd_mouse_leave,
            icon="images/tor_i.ico",
            tooltip=self.tr.tooltip("tor_config_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
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
            icon="images/network_i.ico",
            font=self.font.get(9),
            rtl = self.rtl
        )

        self.address_book_cmd = Command(
            title="Address book",
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            icon="images/address_book_i.ico",
            mouse_enter=self.address_book_cmd_mouse_enter,
            mouse_leave=self.address_book_cmd_mouse_leave,
            shortcut_key=Keys.Control | Keys.Shift | Keys.B,
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.generate_t_cmd = Command(
            title=self.tr.text("generate_t_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.generate_t_cmd_mouse_enter,
            mouse_leave=self.generate_t_cmd_mouse_leave,
            icon="images/transparent_i.ico",
            tooltip=self.tr.tooltip("generate_t_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.generate_z_cmd = Command(
            title=self.tr.text("generate_z_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.generate_z_cmd_mouse_enter,
            mouse_leave=self.generate_z_cmd_mouse_leave,
            icon="images/shielded_i.ico",
            tooltip=self.tr.tooltip("generate_z_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
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
            icon="images/new_addr_i.ico",
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.import_key_cmd = Command(
            title=self.tr.text("importkey_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.import_key_cmd_mouse_enter,
            mouse_leave=self.import_key_cmd_mouse_leave,
            icon = "images/importkey_i.ico",
            tooltip=self.tr.tooltip("importkey_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.export_wallet_cmd = Command(
            title=self.tr.text("export_wallet_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.export_wallet_cmd_mouse_enter,
            mouse_leave=self.export_wallet_cmd_mouse_leave,
            icon="images/export_i.ico",
            tooltip=self.tr.tooltip("export_wallet_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.import_wallet_cmd = Command(
            title=self.tr.text("import_wallet_cmd"),
            background_color=Color.rgb(40,43,48),
            color=Color.WHITE,
            mouse_enter=self.import_wallet_cmd_mouse_enter,
            mouse_leave=self.import_wallet_cmd_mouse_leave,
            icon="images/import_i.ico",
            tooltip=self.tr.tooltip("import_wallet_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.wallet_menu = Command(
            title=self.tr.text("wallet_menu"),
            icon="images/wallet_i.ico",
            drop_opened=self.wallet_menu_opened,
            drop_closed=self.wallet_menu_closed,
            mouse_enter=self.wallet_menu_mouse_enter,
            mouse_leave=self.wallet_menu_mouse_leave,
            sub_commands=[
                self.address_book_cmd,
                self.generate_address_cmd,
                self.import_key_cmd,
                self.export_wallet_cmd,
                self.import_wallet_cmd
            ],
            font=self.font.get(9),
            rtl = self.rtl
        )

        self.edit_username_cmd = Command(
            title=self.tr.text("edit_username_cmd"),
            icon="images/edit_username_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.edit_username_cmd_mouse_enter,
            mouse_leave=self.edit_username_cmd_mouse_leave,
            tooltip=self.tr.tooltip("edit_username_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.market_place_cmd = Command(
            title="Marketplace",
            icon="images/marketplace_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.market_place_cmd_mouse_enter,
            mouse_leave=self.market_place_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.backup_messages_cmd = Command(
            title=self.tr.text("backup_messages_cmd"),
            icon="images/backup_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.backup_messages_cmd_mouse_enter,
            mouse_leave=self.backup_messages_cmd_mouse_leave,
            tooltip=self.tr.tooltip("backup_messages_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
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
                self.market_place_cmd,
                self.backup_messages_cmd
            ],
            font=self.font.get(9),
            rtl = self.rtl
        )

        self.check_update_cmd = Command(
            title=self.tr.text("check_update_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.check_update_cmd_mouse_enter,
            mouse_leave=self.check_update_cmd_mouse_leave,
            icon="images/update_i.ico",
            tooltip=self.tr.tooltip("check_update_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
        )
        self.join_us_cmd = Command(
            title=self.tr.text("join_us_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(40,43,48),
            mouse_enter=self.join_us_cmd_mouse_enter,
            mouse_leave=self.join_us_cmd_mouse_leave,
            icon="images/discord_i.ico",
            tooltip=self.tr.tooltip("join_us_cmd"),
            font=self.font.get(9),
            rtl = self.rtl
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
            mouse_leave=self.help_menu_mouse_leave,
            font=self.font.get(9),
            rtl = self.rtl
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
        self.toolbar_box._impl.native.Controls.Add(self.toolbar)
        
        self.add(
            self.bitcoinz_box,
            self.toolbar_box,
            self.controls_box
        )
        self.bitcoinz_box.add(
            self.bitcoinz_label
        )
        self.controls_box.add(
            self.minimize_control,
            self.resize_control,
            self.close_control
        )
        self.minimize_control.add(
            self.minimize_icon
        )
        self.resize_control.add(
            self.resize_icon
        )
        self.close_control.add(
            self.close_icon
        )

    def update_resize_icon(self, value):
        if value == "restore":
            icon = "images/normal.png"
            tooltip = "Restore"
        elif value == "maximize":
            icon = "images/maximize.png"
            tooltip = "Maximize"
        self.resize_icon.image = icon
        self.resize_control.style.background_color = rgb(40,43,48)
        self.resize_icon.style.background_color = rgb(40,43,48)
        self.tooltip.insert(self.resize_icon._impl.native, tooltip)
        self.tooltip.insert(self.resize_control._impl.native, tooltip)


    def minimize_control_mouse_enter(self, sender, event):
        self.minimize_control.style.background_color = GRAY
        self.minimize_icon.style.background_color = GRAY

    def minimize_control_mouse_leave(self, sender, event):
        pos = self.minimize_control._impl.native.PointToClient(Forms.Cursor.Position)
        if self.minimize_control._impl.native.ClientRectangle.Contains(pos):
            return
        self.minimize_control.style.background_color = rgb(40,43,48)
        self.minimize_icon.style.background_color = rgb(40,43,48)


    def resize_control_mouse_enter(self, sender, event):
        self.resize_control.style.background_color = GRAY
        self.resize_icon.style.background_color = GRAY

    def resize_control_mouse_leave(self, sender, event):
        pos = self.resize_control._impl.native.PointToClient(Forms.Cursor.Position)
        if self.resize_control._impl.native.ClientRectangle.Contains(pos):
            return
        self.resize_control.style.background_color = rgb(40,43,48)
        self.resize_icon.style.background_color = rgb(40,43,48)

    
    def close_control_mouse_enter(self, sender, event):
        self.close_control.style.background_color = RED
        self.close_icon.style.background_color = RED

    def close_control_mouse_leave(self, sender, event):
        pos = self.close_control._impl.native.PointToClient(Forms.Cursor.Position)
        if self.close_control._impl.native.ClientRectangle.Contains(pos):
            return
        self.close_control.style.background_color = rgb(40,43,48)
        self.close_icon.style.background_color = rgb(40,43,48)


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

    def app_console_cmd_mouse_enter(self):
        self.app_console_cmd.icon = "images/console_a.ico"
        self.app_console_cmd.color = Color.BLACK

    def app_console_cmd_mouse_leave(self):
        self.app_console_cmd.icon = "images/console_i.ico"
        self.app_console_cmd.color = Color.WHITE

    def mobile_wallet_cmd_mouse_enter(self):
        self.mobile_wallet_cmd.icon = "images/mobile_a.ico"
        self.mobile_wallet_cmd.color = Color.BLACK

    def mobile_wallet_cmd_mouse_leave(self):
        self.mobile_wallet_cmd.icon = "images/mobile_i.ico"
        self.mobile_wallet_cmd.color = Color.WHITE

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

    def address_book_cmd_mouse_enter(self):
        self.address_book_cmd.icon = "images/address_book_a.ico"
        self.address_book_cmd.color = Color.BLACK

    def address_book_cmd_mouse_leave(self):
        self.address_book_cmd.icon = "images/address_book_i.ico"
        self.address_book_cmd.color = Color.WHITE

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
        self.generate_z_cmd.icon = "images/shielded_a.ico"
        self.generate_z_cmd.color = Color.BLACK

    def generate_z_cmd_mouse_leave(self):
        self.generate_z_cmd.icon = "images/shielded_i.ico"
        self.generate_z_cmd.color = Color.WHITE

    def edit_username_cmd_mouse_enter(self):
        self.edit_username_cmd.icon = "images/edit_username_a.ico"
        self.edit_username_cmd.color = Color.BLACK

    def edit_username_cmd_mouse_leave(self):
        self.edit_username_cmd.icon = "images/edit_username_i.ico"
        self.edit_username_cmd.color = Color.WHITE

    def market_place_cmd_mouse_enter(self):
        self.market_place_cmd.icon = "images/marketplace_a.ico"
        self.market_place_cmd.color = Color.BLACK

    def market_place_cmd_mouse_leave(self):
        self.market_place_cmd.icon = "images/marketplace_i.ico"
        self.market_place_cmd.color = Color.WHITE

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

    def restart_cmd_mouse_enter(self):
        self.restart_cmd.icon = "images/restart_a.ico"
        self.restart_cmd.color = Color.BLACK

    def restart_cmd_mouse_leave(self):
        self.restart_cmd.icon = "images/restart_i.ico"
        self.restart_cmd.color = Color.YELLOW

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

    def exit_app(self, option):
        async def on_result(widget, result):
            if result is True:
                if option == "full":
                    self.utils.stop_tor()
                    await self.commands.stopNode()

                elif option == "restart":
                    result = self.utils.restart_app()
                    if not result:
                        return
                    self.utils.stop_tor()
                    await self.commands.stopNode()

                if self.main.console_toggle:
                    self.app.console._impl.native.Close()
                self.main.notify.hide()
                self.main.notify.dispose()
                if self.main.market_server.server_status:
                    self.main.notifymarket.hide()
                    self.main.notifymarket.dispose()
                if self.main.mobile_server.server_status:
                    self.main.notifymobile.hide()
                    self.main.notifymobile.dispose()
                self.app.exit()

        if self.main.mining_page.mining_status:
            async def on_stop_mining(widget, result):
                if result:
                    await self.main.mining_page.stop_mining()
                    self.exit_app(option)

            self.main.question_dialog(
                title="Mining in Progress",
                message="Mining is currently active. Do you want to stop mining before exiting ?",
                on_result=on_stop_mining
            )
            return
        if option == "full":
            title=self.tr.title("stopexit_dialog")
            message=self.tr.message("stopexit_dialog")

        elif option == "restart":
            title="Restart App"
            message="Are you sure you want to restart the application ?"

        else:
            title=self.tr.title("exit_dialog")
            message=self.tr.message("exit_dialog")

        self.main.question_dialog(
            title=title,
            message=message,
            on_result=on_result
        )