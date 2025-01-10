
import asyncio
import json
from datetime import datetime

from framework import (
    App, Box, DockStyle, Color, Label,
    AlignLabel, FontStyle, Toolbar, Command,
    Font, Image, SizeMode, StatusBar, StatusLabel,
    Separator
)

from .commands import Client
from .utils import Utils

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
        self.app._main_window.min_width = 900
        self.app._main_window.min_height = 600
        self.app._main_window.on_resize = self.on_resize_window

        self.wallet_info = Box(
            dockstyle=DockStyle.TOP,
            size=(0,120),
            autosize=False,
            background_color=Color.rgb(40,43,48)
        )
        self.menu_bar = Box(
            dockstyle=DockStyle.TOP,
            size = (0,40),
            autosize=False,
            background_color=Color.rgb(30,33,36),
            padding=(5,5,5,5)
        )
        self.latest_txs = Box(
            dockstyle=DockStyle.FILL,
            background_color=Color.rgb(40,43,48)
        )

        self.insert(
            [
                self.latest_txs,
                self.menu_bar,
                self.wallet_info
            ]
        )

        self.insert_toolbar()

    def insert_toolbar(self):
        self.file_tool_active = None
        self.wallet_tool_active = None
        self.toolbar = Toolbar(
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36)
        )
        self.about_cmd = Command(
            title="About",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.about_cmd_mouse_enter,
            mouse_leave=self.about_cmd_mouse_leave
        )
        self.exit_cmd = Command(
            title="Exit",
            color=Color.RED,
            background_color=Color.rgb(30,33,36),
            action=self.exit_app
        )
        self.file_tool = Command(
            title="File",
            sub_commands=[
                self.about_cmd,
                self.exit_cmd
            ],
            drop_opened=self.file_tool_opened,
            drop_closed=self.file_tool_closed,
            mouse_enter=self.file_tool_mouse_enter,
            mouse_leave=self.file_tool_mouse_leave
        )
        self.wallet_tool = Command(
            title="Wallet",
            mouse_enter=self.wallet_tool_mouse_enter,
            mouse_leave=self.wallet_tool_mouse_leave
        )
        self.toolbar.add_command(
            [
                self.file_tool,
                self.wallet_tool
            ]
        )
        self.app._main_window.insert([self.toolbar])
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
        self.insert_status_bar()

    def insert_status_bar(self):
        self.status_label = StatusLabel(
            text="Status :",
            color=Color.GRAY,
            font=Font.SERIF,
            style=FontStyle.BOLD
        )
        self.status_icon = StatusLabel(
            image="images/off.png"
        )
        self.blocks_status = StatusLabel(
            text="Blocks :",
            color=Color.GRAY,
            font=Font.SERIF,
            style=FontStyle.BOLD
        )
        self.blocks_value = StatusLabel(
            text="",
            color=Color.WHITE,
            font=Font.SERIF,
            style=FontStyle.BOLD,
            spring=True,
            text_align=AlignLabel.LEFT
        )
        self.date_status = StatusLabel(
            text="Date :",
            color=Color.GRAY,
            font=Font.SERIF,
            style=FontStyle.BOLD
        )
        self.date_value = StatusLabel(
            text="",
            color=Color.WHITE,
            font=Font.SERIF,
            style=FontStyle.BOLD,
            spring=True,
            text_align=AlignLabel.LEFT
        )
        self.sync_status = StatusLabel(
            text="Sync :",
            color=Color.GRAY,
            font=Font.SERIF,
            style=FontStyle.BOLD
        )
        self.sync_value = StatusLabel(
            text="",
            color=Color.WHITE,
            font=Font.SERIF,
            style=FontStyle.BOLD,
            spring=True,
            text_align=AlignLabel.LEFT
        )
        self.size_status = StatusLabel(
            text="Size :",
            color=Color.GRAY,
            font=Font.SERIF,
            style=FontStyle.BOLD
        )
        self.size_value = StatusLabel(
            text="",
            color=Color.WHITE,
            font=Font.SERIF,
            style=FontStyle.BOLD,
            spring=True,
            text_align=AlignLabel.LEFT
        )
        self.status_bar = StatusBar(
            background_color=Color.rgb(30,33,36),
            dockstyle=DockStyle.BOTTOM
        )
        self.status_bar.add_items(
            [
                self.status_label,
                self.status_icon,
                Separator(),
                self.blocks_status,
                self.blocks_value,
                Separator(),
                self.date_status,
                self.date_value,
                Separator(),
                self.sync_status,
                self.sync_value,
                Separator(),
                self.size_status,
                self.size_value
            ]
        )
        self.app._main_window.insert([self.status_bar])
        self.app.run_async(self.update_statusbar())


    async def update_statusbar(self):
        node_status = None
        last_node_status = None
        while True:
            blockchaininfo, _ = await self.commands.getBlockchainInfo()
            if blockchaininfo is not None:
                if isinstance(blockchaininfo, str):
                    info = json.loads(blockchaininfo)
                if info is not None:
                    blocks = info.get('blocks')
                    sync = info.get('verificationprogress')
                    mediantime = info.get('mediantime')
                    node_status = True
                else:
                    blocks = sync = mediantime = "N/A"
                    node_status = False
            else:
                blocks = sync = mediantime = "N/A"
                node_status = False
            if isinstance(mediantime, int):
                mediantime_date = datetime.fromtimestamp(mediantime).strftime('%Y-%m-%d %H:%M:%S')
            else:
                mediantime_date = "N/A"
            bitcoinz_size = self.utils.get_bitcoinz_size()
            sync_percentage = sync * 100
            if node_status != last_node_status:
                self.update_statusbar_icon(node_status)
                last_node_status = node_status

            self.blocks_value.text = str(blocks)
            self.date_value.text = mediantime_date
            self.sync_value.text = f"%{float(sync_percentage):.2f}"
            self.size_value.text = f"{int(bitcoinz_size)} MB"
            await asyncio.sleep(5)

    def update_statusbar_icon(self, status):
        if status:
            status_icon = "images/on.png"
        else:
            status_icon = "images/off.png"
        self.status_icon.image = status_icon

    def home_button_click(self, button):
        self.clear_buttons()
        self.home_button_toggle = True
        self.home_icon.on_click = None
        self.home_txt.on_click = None
        self.home_icon.image = "images/home_a.png"
        self.app.run_async(self.home_button.gradient((255,255,0), steps=10))
        self.home_txt.text_color = Color.BLACK

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
            self.home_icon.on_click = self.home_button_click
            self.home_txt.on_click = self.home_button_click
            self.app.run_async(self.home_button.gradient((30,33,36), steps=10))
            self.home_icon.image = "images/home_i.png"
            self.home_txt.text_color = Color.WHITE
        elif self.transactions_button_toggle:
            self.transactions_button_toggle = None
            self.transactions_icon.on_click = self.transactions_button_click
            self.transactions_txt.on_click = self.transactions_button_click
            self.app.run_async(self.transactions_button.gradient((30,33,36), steps=10))
            self.transactions_icon.image = "images/txs_i.png"
            self.transactions_txt.text_color = Color.WHITE
        elif self.recieve_button_toggle:
            self.recieve_button_toggle = None
            self.recieve_icon.on_click = self.recieve_button_click
            self.recieve_txt.on_click = self.recieve_button_click
            self.app.run_async(self.recieve_button.gradient((30,33,36), steps=10))
            self.recieve_icon.image = "images/recieve_i.png"
            self.recieve_txt.text_color = Color.WHITE
        elif self.send_button_toggle:
            self.send_button_toggle = None
            self.send_icon.on_click = self.send_button_click
            self.send_txt.on_click = self.send_button_click
            self.app.run_async(self.send_button.gradient((30,33,36), steps=10))
            self.send_icon.image = "images/send_i.png"
            self.send_txt.text_color = Color.WHITE
        elif self.message_button_toggle:
            self.message_button_toggle = None
            self.message_icon.on_click = self.message_button_click
            self.message_txt.on_click = self.message_button_click
            self.app.run_async(self.message_button.gradient((30,33,36), steps=10))
            self.message_icon.image = "images/messages_i.png"
            self.message_txt.text_color = Color.WHITE
        elif self.mining_button_toggle:
            self.mining_button_toggle = None
            self.mining_icon.on_click = self.mining_button_click
            self.mining_txt.on_click = self.mining_button_click
            self.app.run_async(self.mining_button.gradient((30,33,36), steps=10))
            self.mining_icon.image = "images/mining_i.png"
            self.mining_txt.text_color = Color.WHITE

    def file_tool_opened(self):
        self.file_tool_active = True
        self.file_tool.color = Color.BLACK

    def file_tool_closed(self):
        self.file_tool_active = False
        self.file_tool.color = Color.WHITE

    def file_tool_mouse_enter(self):
        self.file_tool.color = Color.BLACK

    def file_tool_mouse_leave(self):
        if self.file_tool_active:
            return
        self.file_tool.color = Color.WHITE

    def wallet_tool_mouse_enter(self):
        self.wallet_tool.color = Color.BLACK

    def wallet_tool_mouse_leave(self):
        self.wallet_tool.color = Color.WHITE

    def about_cmd_mouse_enter(self):
        self.about_cmd.color = Color.BLACK

    def about_cmd_mouse_leave(self):
        self.about_cmd.color = Color.WHITE


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

    def exit_app(self, command):
        self.app._main_window.exit()