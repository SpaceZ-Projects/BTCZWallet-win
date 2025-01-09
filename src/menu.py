
from framework import (
    App, Box, DockStyle, Color, Label,
    AlignLabel, FontStyle, Image, SizeMode,
    Font
)


class Menu(Box):
    def __init__(self):
        super().__init__()

        self.size = (800,600)
        self.autosize=True
        self.dockstyle = DockStyle.FILL
        self.background_color = Color.rgb(30,33,36)
        self.on_resize=self.on_resize_menu

        self.app = App()
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