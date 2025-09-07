
import ctypes
import sys

from toga import (
    App, Window, Box, ImageView, Label
)
from .framework import CustomFont, ToolTip, Color, Forms, Keys, FormBorderStyle
from toga.colors import rgb, WHITE, YELLOW, TRANSPARENT
from toga.style.pack import Pack
from toga.constants import COLUMN

from .resources import *
from .translations import *

class BitcoinZGUI(Window):
    def __init__(self):
        super().__init__(
            size=(600, 400),
            resizable= False,
            minimizable = False
        )
        
        self.settings = Settings(self.app)
        self.commands = Client(self.app)
        self.units = Units(self.app, self.commands)
        self.tr = Translations(self.settings)
        self.utils = Utils(self.app, self.settings, self.units, self.tr)
        self.rpc = RPC(self.app, self.utils)
        self.font = CustomFont(self.settings)
        self.tooltip = ToolTip()

        self.app.console = Console(self, self.settings, self.utils, self.commands, self.font)
        self.console_toggle = None

        self.title = self.tr.title("main_window")
        self._impl.native.BackColor = Color.rgb(30,33,36)
        position_center = self.utils.windows_screen_center(self, self)
        self.position = position_center
        self._impl.native.FormBorderStyle = FormBorderStyle.NONE
        self._impl.native.Move += self._hadler_on_move
        self._impl.native.KeyPreview = True
        self._impl.native.Shown += self.on_show
        self._impl.native.KeyDown += Forms.KeyEventHandler(self.on_key_down)

        mode = 0
        ui = self.utils.get_app_theme()
        if ui == "dark":
            mode = 1
        self.app.console.info_log(f"UI Mode : {ui.capitalize()}")
        self.utils.apply_title_bar_mode(self, mode)

        self.rtl = None
        lang = self.settings.language()
        if lang:
            self.app.console.info_log(f"Language : {lang}")
            if lang == "Arabic":
                self.rtl = True

        if self.rtl:
            version = self.units.arabic_digits(self.app.version)
        else:
            version = self.app.version

        self.startup_panel = Box(
            style=Pack(
                direction= COLUMN, 
                background_color = rgb(30,33,36),
                flex = 10
            )
        )
        self.exit_button = ImageView(
            image="images/exit_i.png",
            style=Pack(
                background_color = TRANSPARENT
            )
        )
        self.exit_button._impl.native.Width = 30
        self.exit_button._impl.native.Height = 30
        self.exit_button._impl.native.Left = 560
        self.exit_button._impl.native.Height = 40
        self.exit_button._impl.native.MouseEnter += self.exit_button_mouse_enter
        self.exit_button._impl.native.MouseLeave += self.exit_button_mouse_leave
        self.exit_button._impl.native.Click += self.exit_app

        self.startup_background = ImageView(
            image="images/startup.png",
            style=Pack(
                background_color = rgb(30,33,36),
                width = 600,
                height = 350
            )
        )
        self.startup_background._impl.native.MouseDown += self._on_mouse_down

        self.app_version = Label(
            text=f"v {version}",
            style=Pack(
                color = WHITE,
                background_color = TRANSPARENT
            )
        )
        self.app_version._impl.native.Font = self.font.get(9, True)
        self.app_version._impl.native.Left = 530
        self.app_version._impl.native.Top = 320

        self.tor_icon = ImageView(
            image="images/tor_off.png",
            style=Pack(
                background_color = TRANSPARENT
            )
        )
        self.tor_icon._impl.native.Width = 12
        self.tor_icon._impl.native.Height = 16
        self.tor_icon._impl.native.Left = 25
        self.tor_icon._impl.native.Top = 320
        self.tooltip.insert(self.tor_icon._impl.native, "Tor Network")
        
        self.network_status = Label(
            text="",
            style=Pack(
                background_color = TRANSPARENT
            )
        )
        self.network_status._impl.native.Left = 35
        self.network_status._impl.native.Top = 320
        self.network_status._impl.native.Font = self.font.get(9, True)
        
        self.startup = BTCZSetup(
            self.app, self, self.settings, self.utils, self.units, self.commands, self.rpc, self.tr, self.font
        )
        self.startup_panel.add(
            self.startup_background,
            self.startup
        )

        self.startup_background._impl.native.Controls.Add(self.exit_button._impl.native)
        self.startup_background._impl.native.Controls.Add(self.tor_icon._impl.native)
        self.startup_background._impl.native.Controls.Add(self.network_status._impl.native)
        self.startup_background._impl.native.Controls.Add(self.app_version._impl.native)

        self.content = self.startup_panel
        
        self.app_version._impl.native.MouseEnter += self.app_version_mouse_enter
        self.app_version._impl.native.MouseLeave += self.app_version_mouse_leave


    def on_show(self, sender, event):
        if self.settings.console():
            self.app.console.show_console(True)
            self.console_toggle = True
        self._impl.native.TopMost = False
        self._impl.native.Activate()


    def on_key_down(self, sender, e):
        if e.KeyCode == Keys.F12:
            self.show_app_console()


    def show_app_console(self):
        if not self.console_toggle:
            self.settings.update_settings("console", True)
            self.app.console.show_console(True)
            self.console_toggle = True
        else:
            self.settings.update_settings("console", False)
            self.app.console.hide()
            self.console_toggle = None


    def _on_mouse_down(self, sender: object, e: Forms.MouseEventArgs):
        if e.Button == Forms.MouseButtons.Left:
            hwnd = int(self._impl.native.Handle.ToInt32())
            self.drag_window(hwnd)


    def drag_window(self, hwnd):
        user32 = ctypes.windll.user32
        WM_NCLBUTTONDOWN = 0xA1
        HTCAPTION = 0x2
        user32.ReleaseCapture()
        user32.SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0)


    def exit_button_mouse_enter(self, sender, event):
        self.exit_button.image = "images/exit_a.png"

    def exit_button_mouse_leave(self, sender, event):
        self.exit_button.image = "images/exit_i.png"


    def _hadler_on_move(self, sender, event):
        self.app.console.move(True)

    def app_version_mouse_enter(self, mouse, event):
        self.app_version.style.color = YELLOW

    def app_version_mouse_leave(self, mouse, event):
        self.app_version.style.color = WHITE

    def exit_app(self, sender, event):
        self.app.exit()


class BitcoinZWallet(App):
    
    def startup(self):
        self.console = None
        self.main_window = BitcoinZGUI()
        self.main_window.show()


def main():
    mutex_name = "Global\\BTCZWalletMutex"
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW(None, False, ctypes.c_wchar_p(mutex_name))
    last_error = kernel32.GetLastError()

    if last_error == 183:
        print("Another instance is already running.")
        sys.exit(0)

    app = BitcoinZWallet(
        icon="images/BitcoinZ",
        formal_name = "BTCZWallet",
        app_id = "com.btcz",
        home_page = "https://getbtcz.com",
        author = "BTCZCommunity",
        version = "1.3.9"
    )
    app.main_loop()

if __name__ == "__main__":
    main()