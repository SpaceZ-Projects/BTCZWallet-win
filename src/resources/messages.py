
from framework import (
    App, Box, DockStyle, Color
)

class Messages(Box):
    def __init__(self):
        super().__init__()

        self.app = App()

        self.dockstyle = DockStyle.FILL
        self.background_color = Color.rgb(30,33,36)
        self.visible = False


    async def insert_widgets(self):
        pass