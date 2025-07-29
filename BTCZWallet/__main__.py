
from toga import (
    App, Window, Box, ImageView, Label
)
from .framework import CustomFont, ToolTip, Color
from toga.colors import rgb, WHITE, YELLOW
from toga.style.pack import Pack
from toga.constants import RIGHT, COLUMN, ROW, LEFT

from .resources import *
from .translations import *

class BitcoinZGUI(Window):
    def __init__(self):
        super().__init__(
            size=(350, 400),
            resizable= False,
            minimizable = False
        )
        
        self.settings = Settings(self.app)
        self.commands = Client(self.app)
        self.units = Units(self.app, self.commands)
        self.tr = Translations(self.settings)
        self.utils = Utils(self.app, self.settings, self.units, self.tr)
        self.font = CustomFont(self.settings)
        self.tooltip = ToolTip()

        self.title = self.tr.title("main_window")
        self._impl.native.BackColor = Color.rgb(30,33,36)
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self.rtl = None
        lang = self.settings.language()
        if lang:
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
        self.bitcoinz_logo = ImageView(
            image="images/BitcoinZ.png",
            style=Pack(
                background_color = rgb(30,33,36),
                padding_top = 22,
                flex = 8
            )
        )
        self.version_box = Box(
            style=Pack(
                direction = ROW,
                background_color= rgb(30,33,36),
            )
        )
        self.app_version = Label(
            text=f"v {version}",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = RIGHT,
                padding_right = 10,
                flex = 1
            )
        )
        self.app_version._impl.native.Font = self.font.get(9, True)

        self.tor_icon = ImageView(
            image="images/tor_off.png",
            style=Pack(
                background_color = rgb(30,33,36),
                padding = self.tr.padding("tor_icon"),
            )
        )
        self.tooltip.insert(self.tor_icon._impl.native, "Tor Network")
        
        self.network_status = Label(
            text="",
            style=Pack(
                background_color = rgb(30,33,36),
                text_align = LEFT,
                padding_left = 3,
                flex = 1
            )
        )
        self.network_status._impl.native.Font = self.font.get(9, True)
        
        self.startup = BTCZSetup(
            self.app, self, self.settings, self.utils, self.units, self.commands, self.tr, self.font
        )
        self.startup_panel.add(
            self.bitcoinz_logo,
            self.version_box,
            self.startup
        )
        self.version_box.add(
            self.tor_icon,
            self.network_status,
            self.app_version
        )
        self.content = self.startup_panel
        
        self.app_version._impl.native.MouseEnter += self.app_version_mouse_enter
        self.app_version._impl.native.MouseLeave += self.app_version_mouse_leave

    def app_version_mouse_enter(self, mouse, event):
        self.app_version.style.color = YELLOW

    def app_version_mouse_leave(self, mouse, event):
        self.app_version.style.color = WHITE


class BitcoinZWallet(App):
    
    def startup(self):
        self.main_window = BitcoinZGUI()
        self.main_window._impl.native.TopMost = True
        self.main_window._impl.native.Shown += self.on_show
        self.main_window.show()

    def on_show(self, sender, event):
        self.main_window._impl.native.TopMost = False
        self.main_window._impl.native.Activate()


def main():
    app = BitcoinZWallet(
        icon="images/BitcoinZ",
        formal_name = "BTCZWallet",
        app_id = "com.btcz",
        home_page = "https://getbtcz.com",
        author = "BTCZCommunity",
        version = "1.3.2"
    )
    app.main_loop()

if __name__ == "__main__":
    main()