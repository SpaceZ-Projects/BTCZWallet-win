
import asyncio
from framework import (
    App, Box, Color, Label, Font, FontStyle,
    DockStyle, AlignLabel, ProgressStyle
)

from .utils import Utils


class BTCZSetup(Box):
    def __init__(self, main):
        super(BTCZSetup, self).__init__(
            size=(325,40),
            location=(5,300),
            background_color=Color.rgb(40,43,48)
        )

        self.app = App()
        self.utils = Utils()
        self.main = main
        self.app_data = self.app.app_data

        self.node_status = None
        self.blockchaine_index = None

        self.status_label = Label(
            text="Verify binary files...",
            text_color=Color.WHITE,
            size=9,
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL
        )

        self.insert([self.status_label])
        self.app.run_async(self.verify_binary_files())


    async def verify_binary_files(self):
        await asyncio.sleep(2)
        missing_files = self.utils.get_binary_files()
        if missing_files:
            self.status_label.text = "Downloading binary..."
            self.main.progress_bar.style = ProgressStyle.BLOCKS
            await self.utils.fetch_binary_files(
                self.status_label,
                self.main.progress_bar
            )