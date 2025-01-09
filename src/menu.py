
from framework import (
    App, Box, DockStyle, Color
)


class Menu(Box):
    def __init__(self):
        super().__init__()

        self.size = (800,600)
        self.autosize=True
        self.dockstyle = DockStyle.FILL
        self.background_color = Color.rgb(30,33,36)

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

    
    def on_resize_window(self, window):
        pass