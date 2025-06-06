
from toga import (
    App, Window, Box, ImageView, Label
)
from .framework import CustomFont
from toga.colors import rgb, WHITE, YELLOW
from toga.style.pack import Pack
from toga.constants import RIGHT, COLUMN, ROW, LEFT

from .resources import BTCZSetup, Utils

class BitcoinZGUI(Window):
    def __init__(self):
        super().__init__(
            size=(350, 400),
            resizable= False,
            minimizable = False
        )

        self.utils = Utils(self.app)

        self.monda_font = CustomFont()

        self.title = "BitcoinZ Wallet"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

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
            text=f"v{self.app.version}",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = RIGHT,
                padding_right = 10,
                flex = 1
            )
        )
        self.app_version._impl.native.Font = self.monda_font.get(9, True)

        self.tor_icon = ImageView(
            image="images/tor_off.png",
            style=Pack(
                background_color = rgb(30,33,36),
                padding_left = 10,
            )
        )
        self.network_status = Label(
            text="",
            style=Pack(
                background_color = rgb(30,33,36),
                text_align = LEFT,
                padding_left = 3,
                flex = 1
            )
        )
        self.network_status._impl.native.Font = self.monda_font.get(9, True)
        
        self.startup = BTCZSetup(
            self.app,
            self
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
        version = "1.3.0"
    )
    app.main_loop()

if __name__ == "__main__":
    main()