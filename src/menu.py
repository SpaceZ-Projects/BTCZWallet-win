
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

        self.size = (800,600)
        self.autosize=True
        self.dockstyle = DockStyle.FILL
        self.background_color = Color.rgb(30,33,36)
        self.on_resize=self.on_resize_menu

        self.app = App()
        self.commands = Client()
        self.utils = Utils()
        self.app._main_window.min_width = 800
        self.app._main_window.min_height = 600
        self.app._main_window.on_resize = self.on_resize_window

        self.blockchain_box = Box(
            dockstyle=DockStyle.TOP,
            size=(0,100),
            autosize=False,
            background_color=Color.rgb(40,43,48)
        )
        self.menu_bar = Box(
            dockstyle=DockStyle.TOP,
            size = (0,40),
            autosize=False,
            background_color=Color.rgb(30,33,36)
        )
        self.latest_box = Box(
            dockstyle=DockStyle.FILL,
            background_color=Color.rgb(40,43,48)
        )

        self.insert(
            [
                self.latest_box,
                self.menu_bar,
                self.blockchain_box
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
            mouse_leave=self.home_button_mouse_leave
        )
        self.transactions_icon = Image(
            image="images/txs_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.transactions_button_mouse_enter,
            mouse_leave=self.transactions_button_mouse_leave
        )
        self.recieve_icon = Image(
            image="images/recieve_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.recieve_button_mouse_enter,
            mouse_leave=self.recieve_button_mouse_leave
        )
        self.send_icon = Image(
            image="images/send_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.send_button_mouse_enter,
            mouse_leave=self.send_button_mouse_leave
        )
        self.message_icon = Image(
            image="images/messages_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.message_button_mouse_enter,
            mouse_leave=self.message_button_mouse_leave
        )
        self.mining_icon = Image(
            image="images/mining_i.png",
            dockstyle=DockStyle.LEFT,
            size_mode=SizeMode.ZOOM,
            mouse_enter=self.mining_button_mouse_enter,
            mouse_leave=self.mining_button_mouse_leave
        )
        self.home_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36)
        )
        self.transactions_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36)
        )
        self.recieve_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36)
        )
        self.send_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36)
        )
        self.message_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36)
        )
        self.mining_button = Box(
            dockstyle=DockStyle.LEFT,
            autosize=False,
            background_color=Color.rgb(30,33,36)
        )
        self.home_txt = Label(
            text="Home",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.home_button_mouse_enter,
            mouse_leave=self.home_button_mouse_leave
        )
        self.transactions_txt = Label(
            text="Txs",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.transactions_button_mouse_enter,
            mouse_leave=self.transactions_button_mouse_leave
        )
        self.recieve_txt = Label(
            text="Recieve",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.recieve_button_mouse_enter,
            mouse_leave=self.recieve_button_mouse_leave
        )
        self.send_txt = Label(
            text="Send",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.send_button_mouse_enter,
            mouse_leave=self.send_button_mouse_leave
        )
        self.message_txt = Label(
            text="Messages",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.message_button_mouse_enter,
            mouse_leave=self.message_button_mouse_leave
        )
        self.mining_txt = Label(
            text="Mining",
            text_color=Color.WHITE,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL,
            style=FontStyle.BOLD,
            font=Font.SANSSERIF,
            mouse_enter=self.mining_button_mouse_enter,
            mouse_leave=self.mining_button_mouse_leave
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

    
    def home_button_mouse_enter(self):
        self.home_icon.image = "images/home_a.png"
        self.home_button.background_color = Color.YELLOW
        self.home_txt.text_color= Color.BLACK

    def home_button_mouse_leave(self):
        self.home_icon.image = "images/home_i.png"
        self.home_button.background_color = Color.rgb(30,33,36)
        self.home_txt.text_color= Color.WHITE

    def transactions_button_mouse_enter(self):
        self.transactions_icon.image = "images/txs_a.png"
        self.transactions_button.background_color = Color.YELLOW
        self.transactions_txt.text_color = Color.BLACK
    
    def transactions_button_mouse_leave(self):
        self.transactions_icon.image = "images/txs_i.png"
        self.transactions_button.background_color = Color.rgb(30,33,36)
        self.transactions_txt.text_color = Color.WHITE

    def recieve_button_mouse_enter(self):
        self.recieve_icon.image = "images/recieve_a.png"
        self.recieve_button.background_color = Color.YELLOW
        self.recieve_txt.text_color = Color.BLACK

    def recieve_button_mouse_leave(self):
        self.recieve_icon.image = "images/recieve_i.png"
        self.recieve_button.background_color = Color.rgb(30,33,36)
        self.recieve_txt.text_color = Color.WHITE

    def send_button_mouse_enter(self):
        self.send_icon.image = "images/send_a.png"
        self.send_button.background_color = Color.YELLOW
        self.send_txt.text_color = Color.BLACK

    def send_button_mouse_leave(self):
        self.send_icon.image = "images/send_i.png"
        self.send_button.background_color = Color.rgb(30,33,36)
        self.send_txt.text_color = Color.WHITE

    def message_button_mouse_enter(self):
        self.message_icon.image = "images/messages_a.png"
        self.message_button.background_color = Color.YELLOW
        self.message_txt.text_color = Color.BLACK

    def message_button_mouse_leave(self):
        self.message_icon.image = "images/messages_i.png"
        self.message_button.background_color = Color.rgb(30,33,36)
        self.message_txt.text_color = Color.WHITE

    def mining_button_mouse_enter(self):
        self.mining_icon.image = "images/mining_a.png"
        self.mining_button.background_color = Color.YELLOW
        self.mining_txt.text_color = Color.BLACK

    def mining_button_mouse_leave(self):
        self.mining_icon.image = "images/mining_i.png"
        self.mining_button.background_color = Color.rgb(30,33,36)
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