
import asyncio

from toga import App, Box
from toga.style.pack import Pack
from toga.constants import COLUMN
from toga.colors import rgb


class Messages(Box):
    def __init__(self, app:App):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5)
            )
        )
        self.app = app


    async def insert_widgets(self):
        await asyncio.sleep(0.2)