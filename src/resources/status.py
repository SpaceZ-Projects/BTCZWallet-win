
import asyncio
from datetime import datetime
import json

from toga import App, Box
from ..framework import (
    StatusBar, StatusLabel, Separator,
    DockStyle, Color, Font, FontStyle, AlignLabel
)
from toga.style.pack import Pack
from toga.constants import ROW, BOTTOM

from .client import Client
from .utils import Utils


class AppStatusBar(Box):
    def __init__(self, app:App):
        super().__init__(
            style=Pack(
                direction = ROW,
                alignment = BOTTOM,
                height = 24
            )
        )

        self.app = app
        self.commands = Client(self.app)
        self.utils = Utils(self.app)

        self.statusbar = StatusBar(
            background_color=Color.rgb(40,43,48),
            dockstyle=DockStyle.BOTTOM
        )

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
            text_align=AlignLabel.LEFT,
            autotooltip=True
        )
        self.deprecation_status = StatusLabel(
            text="Deps :",
            color=Color.GRAY,
            font=Font.SERIF,
            style=FontStyle.BOLD
        )
        self.deprecation_value = StatusLabel(
            text="",
            color=Color.WHITE,
            font=Font.SERIF,
            style=FontStyle.BOLD,
            text_align=AlignLabel.LEFT,
            autotooltip=True
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
            text_align=AlignLabel.LEFT,
            autotooltip=True
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
            text_align=AlignLabel.LEFT,
            autotooltip=True
        )
        self.network_status = StatusLabel(
            text="NetHash :",
            color=Color.GRAY,
            font=Font.SERIF,
            style=FontStyle.BOLD
        )
        self.network_value = StatusLabel(
            text="",
            color=Color.WHITE,
            font=Font.SERIF,
            style=FontStyle.BOLD,
            text_align=AlignLabel.LEFT,
            autotooltip=True
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
            text_align=AlignLabel.LEFT,
            autotooltip=True
        )
        self.statusbar.add_items(
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
                self.network_status,
                self.network_value,
                Separator(),
                self.deprecation_status,
                self.deprecation_value,
                Separator(),
                self.size_status,
                self.size_value
            ]
        )
        self._impl.native.Controls.Add(self.statusbar)

    
    def update_statusbar(self):
        self.app.add_background_task(self.update_blockchaininfo)
        self.app.add_background_task(self.update_deprecationinfo)
        self.app.add_background_task(self.update_networkhash)


    async def update_blockchaininfo(self, widget):
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
                await self.update_statusbar_icon(node_status)
                last_node_status = node_status

            self.blocks_value.text = str(blocks)
            self.date_value.text = mediantime_date
            self.sync_value.text = f"%{float(sync_percentage):.2f}"
            self.size_value.text = f"{int(bitcoinz_size)} MB"
            await asyncio.sleep(5)


    async def update_statusbar_icon(self, status):
        if status:
            status_icon = "images/on.png"
        else:
            status_icon = "images/off.png"
        self.status_icon.image = status_icon


    async def update_networkhash(self, widget):
        while True:
            networksol, _ = await self.commands.getNetworkSolps()
            if networksol is not None:
                if isinstance(networksol, str):
                    info = json.loads(networksol)
                if info is not None:
                    netsol = info
                else:
                    netsol = "N/A"
            self.network_value.text = f"{netsol} Sol/s"
            await asyncio.sleep(5)


    async def update_deprecationinfo(self, widget):
        deprecationinfo, _ = await self.commands.getDeprecationInfo()
        if deprecationinfo is not None:
            if isinstance(deprecationinfo, str):
                info = json.loads(deprecationinfo)
            if info is not None:
                deprecation = info.get('deprecationheight')
            else:
                deprecation = "N/A"

        self.deprecation_value.text = str(deprecation)