
import asyncio
from datetime import datetime
import json

from toga import App, Box, Window
from ..framework import (
    StatusBar, StatusLabel, Separator,
    DockStyle, Color, Font, FontStyle, AlignContent
)
from toga.style.pack import Pack
from toga.constants import ROW, BOTTOM

from .client import Client
from .utils import Utils


class AppStatusBar(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                alignment = BOTTOM,
                height = 24
            )
        )

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.utils = Utils(self.app)

        self.node_status = None

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
            text_align=AlignContent.LEFT,
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
            text_align=AlignContent.LEFT,
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
            text_align=AlignContent.LEFT,
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
            text_align=AlignContent.LEFT,
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
            text_align=AlignContent.LEFT,
            autotooltip=True
        )
        self.connections_status = StatusLabel(
            text="Conns :",
            color=Color.GRAY,
            font=Font.SERIF,
            style=FontStyle.BOLD
        )
        self.connections_value = StatusLabel(
            text="",
            color=Color.WHITE,
            font=Font.SERIF,
            style=FontStyle.BOLD,
            text_align=AlignContent.LEFT,
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
            text_align=AlignContent.LEFT,
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
                self.connections_status,
                self.connections_value,
                Separator(),
                self.deprecation_status,
                self.deprecation_value,
                Separator(),
                self.size_status,
                self.size_value
            ]
        )
        self._impl.native.Controls.Add(self.statusbar)

    
    def run_statusbar_tasks(self):
        self.app.add_background_task(self.update_blockchaininfo)
        self.app.add_background_task(self.update_deprecationinfo)
        self.app.add_background_task(self.update_networkhash)
        self.app.add_background_task(self.update_connections_count)


    async def update_blockchaininfo(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            blockchaininfo,_ = await self.commands.getBlockchainInfo()
            if blockchaininfo is not None:
                self.node_status = True

                info = json.loads(blockchaininfo)
                blocks = info.get('blocks')
                sync = info.get('verificationprogress')
                sync_percentage = float(sync) * 100
                sync_text = f"{sync_percentage:.2f}%"
                mediantime = info.get('mediantime')
                mediantime_date = datetime.fromtimestamp(mediantime).strftime('%Y-%m-%d %H:%M:%S')
                status_icon = "images/on.png"
                
            else:
                self.node_status = None
                blocks = "N/A"
                sync_text = "N/A"
                mediantime_date = "N/A"
                status_icon = "images/off.png"

            bitcoinz_size = self.utils.get_bitcoinz_size()

            await self.update_statusbar(status_icon, blocks, sync_text, mediantime_date, bitcoinz_size)
            await asyncio.sleep(5)


    async def update_statusbar(self, status_icon, blocks, sync, mediantime, bitcoinz_size):
        self.status_icon.image = status_icon
        self.blocks_value.text = str(blocks)
        self.date_value.text = mediantime
        self.sync_value.text = sync
        self.size_value.text = f"{int(bitcoinz_size)} MB"
        if not self.node_status:
            await asyncio.sleep(1)
            restart = self.utils.restart_app()
            if restart:
                self.main.notify.hide()
                self.app.exit()
                return


    async def update_networkhash(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
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

    
    async def update_connections_count(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            connection_count,_ = await self.commands.getConnectionCount()
            if connection_count is not None:
                self.connections_value.text = connection_count


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