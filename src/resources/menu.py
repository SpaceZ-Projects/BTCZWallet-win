
import asyncio
from framework import (
    App, Box, DockStyle, Color, Label,
    AlignLabel, FontStyle, Font, Image, SizeMode,
)

from .client import Client
from .utils import Utils
from .toolbar import AppToolBar
from .status import AppStatusBar
from .wallet import Wallet
from .home import Home
from .txs import Transactions
from .recieve import Recieve
from .send import Send
from .messages import Messages
from .mining import Mining

class Menu(Box):
    def __init__(self):
        super().__init__()

        self.size = (900,600)
        self.autosize=True
        self.dockstyle = DockStyle.FILL
        self.background_color = Color.rgb(30,33,36)
        self.on_resize=self.on_resize_menu

        self.app = App()
        self.commands = Client()
        self.utils = Utils()
        self.toolbar = AppToolBar()
        self.status_bar = AppStatusBar()
        self.app._main_window.min_width = 900
        self.app._main_window.min_height = 600
        self.app._main_window.on_resize = self.on_resize_window

        self.wallet = Wallet()
        self.wallet_info = Box(
            dockstyle=DockStyle.TOP,
            size=(0,120),
            autosize=False,
            background_color=Color.rgb(40,43,48),
            padding=(5,30,5,5)
        )
        self.menu_bar = Box(
            dockstyle=DockStyle.TOP,
            size = (0,40),
            autosize=False,
            background_color=Color.rgb(30,33,36),
            padding=(5,5,5,5)
        )
        self.pages = Box(
            dockstyle=DockStyle.FILL,
            background_color=Color.rgb(40,43,48),
            padding=(5,5,5,28)
        )

        self.home_page = Home()
        self.transactions_page = Transactions()
        self.recieve_page = Recieve()
        self.send_page = Send()
        self.message_page = Messages()
        self.mining_page = Mining()

        self.insert(
            [
                self.pages,
                self.menu_bar,
                self.wallet_info
            ]
        )

        self.wallet_info.insert([self.wallet])

        self.pages.insert(
            [
                self.home_page,
                self.transactions_page,
                self.recieve_page,
                self.send_page,
                self.message_page,
                self.mining_page
            ]
        )

        self.insert_toolbar()

    def insert_toolbar(self):
        self.app._main_window.insert([self.toolbar])
        self.insert_status_bar()

    def insert_status_bar(self):
        self.app._main_window.insert([self.status_bar])
        self.status_bar.update_statusbar()
        self.insert_menu_buttons()


    def insert_menu_buttons(self):
        self.home_icon = Image(
            image="images/home_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.home_button_mouse_enter,
            mouse_leave=self.home_button_mouse_leave,
            on_click=self.home_button_click
        )
        self.transactions_icon = Image(
            image="images/txs_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.transactions_button_mouse_enter,
            mouse_leave=self.transactions_button_mouse_leave,
            on_click=self.transactions_button_click
        )
        self.recieve_icon = Image(
            image="images/recieve_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.recieve_button_mouse_enter,
            mouse_leave=self.recieve_button_mouse_leave,
            on_click=self.recieve_button_click
        )
        self.send_icon = Image(
            image="images/send_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.send_button_mouse_enter,
            mouse_leave=self.send_button_mouse_leave,
            on_click=self.send_button_click
        )
        self.message_icon = Image(
            image="images/messages_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.message_button_mouse_enter,
            mouse_leave=self.message_button_mouse_leave,
            on_click=self.message_button_click
        )
        self.mining_icon = Image(
            image="images/mining_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.mining_button_mouse_enter,
            mouse_leave=self.mining_button_mouse_leave,
            on_click=self.mining_button_click
        )
        self.home_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36),
            padding=(5,5,5,5)
        )
        self.transactions_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36),
            padding=(5,5,5,5)
        )
        self.recieve_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36),
            padding=(5,5,5,5)
        )
        self.send_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36),
            padding=(5,5,5,5)
        )
        self.message_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36),
            padding=(5,5,5,5)
        )
        self.mining_button = Box(
            dockstyle=DockStyle.RIGHT,
            autosize=False,
            background_color=Color.rgb(30,33,36),
            padding=(5,5,5,5)
        )
        self.home_txt = Label(
            text="Home",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.home_button_mouse_enter,
            mouse_leave=self.home_button_mouse_leave,
            on_click=self.home_button_click
        )
        self.transactions_txt = Label(
            text="Txs",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.transactions_button_mouse_enter,
            mouse_leave=self.transactions_button_mouse_leave,
            on_click=self.transactions_button_click
        )
        self.recieve_txt = Label(
            text="Recieve",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.recieve_button_mouse_enter,
            mouse_leave=self.recieve_button_mouse_leave,
            on_click=self.recieve_button_click
        )
        self.send_txt = Label(
            text="Send",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.send_button_mouse_enter,
            mouse_leave=self.send_button_mouse_leave,
            on_click=self.send_button_click
        )
        self.message_txt = Label(
            text="Messages",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.message_button_mouse_enter,
            mouse_leave=self.message_button_mouse_leave,
            on_click=self.message_button_click
        )
        self.mining_txt = Label(
            text="Mining",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.mining_button_mouse_enter,
            mouse_leave=self.mining_button_mouse_leave,
            on_click=self.mining_button_click
        )

        self.home_button.insert([self.home_icon, self.home_txt])
        self.transactions_button.insert([self.transactions_icon, self.transactions_txt])
        self.recieve_button.insert([self.recieve_icon, self.recieve_txt])
        self.send_button.insert([self.send_icon, self.send_txt])
        self.message_button.insert([self.message_icon, self.message_txt])
        self.mining_button.insert([self.mining_icon, self.mining_txt])
        
        self.menu_bar.insert(
            [
                self.mining_button,
                self.message_button,
                self.send_button,
                self.recieve_button,
                self.transactions_button,
                self.home_button
            ]
        )
        self.home_button_toggle = None
        self.transactions_button_toggle = None
        self.recieve_button_toggle = None
        self.send_button_toggle = None
        self.message_button_toggle = None
        self.mining_button_toggle = None
        self.app.run_async(self.set_default_page())


    async def set_default_page(self):
        await asyncio.sleep(0.2)
        self.home_button_click(None)
        await asyncio.sleep(0.2)
        await self.wallet.insert_widgets()

    def home_button_click(self, button):
        self.clear_buttons()
        self.home_button_toggle = True
        self.home_icon.on_click = None
        self.home_txt.on_click = None
        self.home_icon.image = "images/home_a.png"
        self.app.run_async(self.home_button.gradient((255,255,0), steps=10))
        self.home_txt.text_color = Color.BLACK
        self.home_page.visible = True
        self.app.run_async(self.home_page.insert_widgets())

    def home_button_mouse_enter(self):
        if self.home_button_toggle:
            return
        self.home_button.background_color = Color.rgb(66,69,73)

    def home_button_mouse_leave(self):
        if self.home_button_toggle:
            return
        self.home_button.background_color = Color.rgb(30,33,36)

    def transactions_button_click(self, button):
        self.clear_buttons()
        self.transactions_button_toggle = True
        self.transactions_icon.on_click = None
        self.transactions_txt.on_click = None
        self.transactions_icon.image = "images/txs_a.png"
        self.app.run_async(self.transactions_button.gradient((255,255,0), steps=10))
        self.transactions_txt.text_color = Color.BLACK
        self.transactions_page.visible = True
        self.app.run_async(self.transactions_page.insert_widgets())

    def transactions_button_mouse_enter(self):
        if self.transactions_button_toggle:
            return
        self.transactions_button.background_color = Color.rgb(66,69,73)
    
    def transactions_button_mouse_leave(self):
        if self.transactions_button_toggle:
            return
        self.transactions_button.background_color = Color.rgb(30,33,36)

    def recieve_button_click(self, button):
        self.clear_buttons()
        self.recieve_button_toggle = True
        self.recieve_icon.on_click = None
        self.recieve_txt.on_click = None
        self.recieve_icon.image = "images/recieve_a.png"
        self.app.run_async(self.recieve_button.gradient((255,255,0), steps=10))
        self.recieve_txt.text_color = Color.BLACK
        self.recieve_page.visible = True
        self.app.run_async(self.recieve_page.insert_widgets())

    def recieve_button_mouse_enter(self):
        if self.recieve_button_toggle:
            return
        self.recieve_button.background_color = Color.rgb(66,69,73)

    def recieve_button_mouse_leave(self):
        if self.recieve_button_toggle:
            return
        self.recieve_button.background_color = Color.rgb(30,33,36)

    def send_button_click(self, button):
        self.clear_buttons()
        self.send_button_toggle = True
        self.send_icon.on_click = None
        self.send_txt.on_click = None
        self.send_icon.image = "images/send_a.png"
        self.app.run_async(self.send_button.gradient((255,255,0), steps=10))
        self.send_txt.text_color = Color.BLACK
        self.send_page.visible = True
        self.app.run_async(self.send_page.insert_widgets())

    def send_button_mouse_enter(self):
        if self.send_button_toggle:
            return
        self.send_button.background_color = Color.rgb(66,69,73)

    def send_button_mouse_leave(self):
        if self.send_button_toggle:
            return
        self.send_button.background_color = Color.rgb(30,33,36)

    def message_button_click(self, button):
        self.clear_buttons()
        self.message_button_toggle = True
        self.message_icon.on_click = None
        self.message_txt.on_click = None
        self.message_icon.image = "images/messages_a.png"
        self.app.run_async(self.message_button.gradient((255,255,0), steps=10))
        self.message_txt.text_color = Color.BLACK
        self.message_page.visible = True
        self.app.run_async(self.message_page.insert_widgets())

    def message_button_mouse_enter(self):
        if self.message_button_toggle:
            return
        self.message_button.background_color = Color.rgb(66,69,73)

    def message_button_mouse_leave(self):
        if self.message_button_toggle:
            return
        self.message_button.background_color = Color.rgb(30,33,36)

    def mining_button_click(self, button):
        self.clear_buttons()
        self.mining_button_toggle = True
        self.mining_icon.on_click = None
        self.mining_txt.on_click = None
        self.mining_icon.image = "images/mining_a.png"
        self.app.run_async(self.mining_button.gradient((255,255,0), steps=10))
        self.mining_txt.text_color = Color.BLACK
        self.mining_page.visible = True
        self.app.run_async(self.mining_page.insert_widgets())

    def mining_button_mouse_enter(self):
        if self.mining_button_toggle:
            return
        self.mining_button.background_color = Color.rgb(66,69,73)

    def mining_button_mouse_leave(self):
        if self.mining_button_toggle:
            return
        self.mining_button.background_color = Color.rgb(30,33,36)

    def clear_buttons(self):
        if self.home_button_toggle:
            self.home_button_toggle = None
            self.home_page.visible = False
            self.home_page.clear()
            self.home_icon.on_click = self.home_button_click
            self.home_txt.on_click = self.home_button_click
            self.app.run_async(self.home_button.gradient((30,33,36), steps=10))
            self.home_icon.image = "images/home_i.png"
            self.home_txt.text_color = Color.WHITE

        elif self.transactions_button_toggle:
            self.transactions_button_toggle = None
            self.transactions_page.visible = False
            self.transactions_page.clear()
            self.transactions_icon.on_click = self.transactions_button_click
            self.transactions_txt.on_click = self.transactions_button_click
            self.app.run_async(self.transactions_button.gradient((30,33,36), steps=10))
            self.transactions_icon.image = "images/txs_i.png"
            self.transactions_txt.text_color = Color.WHITE

        elif self.recieve_button_toggle:
            self.recieve_button_toggle = None
            self.recieve_page.visible = False
            self.recieve_page.clear()
            self.recieve_icon.on_click = self.recieve_button_click
            self.recieve_txt.on_click = self.recieve_button_click
            self.app.run_async(self.recieve_button.gradient((30,33,36), steps=10))
            self.recieve_icon.image = "images/recieve_i.png"
            self.recieve_txt.text_color = Color.WHITE

        elif self.send_button_toggle:
            self.send_button_toggle = None
            self.send_page.visible = False
            self.send_page.clear()
            self.send_icon.on_click = self.send_button_click
            self.send_txt.on_click = self.send_button_click
            self.app.run_async(self.send_button.gradient((30,33,36), steps=10))
            self.send_icon.image = "images/send_i.png"
            self.send_txt.text_color = Color.WHITE

        elif self.message_button_toggle:
            self.message_button_toggle = None
            self.message_page.visible = False
            self.message_page.clear()
            self.message_icon.on_click = self.message_button_click
            self.message_txt.on_click = self.message_button_click
            self.app.run_async(self.message_button.gradient((30,33,36), steps=10))
            self.message_icon.image = "images/messages_i.png"
            self.message_txt.text_color = Color.WHITE

        elif self.mining_button_toggle:
            self.mining_button_toggle = None
            self.mining_page.visible = False
            self.mining_page.clear()
            self.mining_icon.on_click = self.mining_button_click
            self.mining_txt.on_click = self.mining_button_click
            self.app.run_async(self.mining_button.gradient((30,33,36), steps=10))
            self.mining_icon.image = "images/mining_i.png"
            self.mining_txt.text_color = Color.WHITE


    def on_resize_menu(self, box):
        self.menu_bar.width = self.app._main_window.width
        total_width = self.menu_bar.width
        num_buttons = len(self.menu_bar.widgets)
        if num_buttons > 0:
            button_width = total_width // num_buttons
            for button in self.menu_bar.widgets:
                button.width = button_width

    def on_resize_window(self, window):
        pass