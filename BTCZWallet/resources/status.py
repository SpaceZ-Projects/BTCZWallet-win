
import asyncio
from datetime import datetime
import json

from toga import App, Box, Window
from ..framework import (
    StatusBar, StatusLabel, Separator,
    DockStyle, Color, AlignContent
)
from toga.style.pack import Pack
from toga.constants import ROW, BOTTOM


class AppStatusBar(Box):
    def __init__(self, app:App, main:Window, settings, utils, units, commands, tr, font):
        super().__init__(
            style=Pack(
                direction = ROW,
                alignment = BOTTOM
            )
        )

        self.node_status = None
        self.app = app
        self.main = main

        self.commands = commands
        self.utils = utils
        self.settings = settings
        self.units = units
        self.tr = tr
        self.font = font

        self.style.height = self.tr.size("appstatusbar")

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.statusbar = StatusBar(
            background_color=Color.rgb(40,43,48),
            dockstyle=DockStyle.BOTTOM,
            rtl=self.rtl
        )

        self.status_label = StatusLabel(
            text=self.tr.text("status_label"),
            color=Color.GRAY,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.status_icon = StatusLabel(
            image="images/off.png"
        )
        self.blocks_status = StatusLabel(
            text=self.tr.text("blocks_status"),
            color=Color.GRAY,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.blocks_value = StatusLabel(
            text="",
            color=Color.WHITE,
            text_align=AlignContent.LEFT,
            autotooltip=True,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.deprecation_status = StatusLabel(
            text=self.tr.text("deprecation_status"),
            color=Color.GRAY,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.deprecation_value = StatusLabel(
            text="",
            color=Color.WHITE,
            text_align=AlignContent.LEFT,
            autotooltip=True,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.date_status = StatusLabel(
            text=self.tr.text("date_status"),
            color=Color.GRAY,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.date_value = StatusLabel(
            text="",
            color=Color.WHITE,
            spring=True,
            text_align=AlignContent.LEFT,
            autotooltip=True,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.sync_status = StatusLabel(
            text=self.tr.text("sync_status"),
            color=Color.GRAY,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.sync_value = StatusLabel(
            text="",
            color=Color.WHITE,
            text_align=AlignContent.LEFT,
            autotooltip=True,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.network_status = StatusLabel(
            text=self.tr.text("network_status"),
            color=Color.GRAY,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.network_value = StatusLabel(
            text="",
            color=Color.WHITE,
            text_align=AlignContent.LEFT,
            autotooltip=True,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.connections_status = StatusLabel(
            text=self.tr.text("connections_status"),
            color=Color.GRAY,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.connections_value = StatusLabel(
            text="",
            color=Color.WHITE,
            text_align=AlignContent.LEFT,
            autotooltip=True,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.size_status = StatusLabel(
            text=self.tr.text("size_status"),
            color=Color.GRAY,
            font=self.font.get(8),
            rtl=self.rtl
        )
        self.size_value = StatusLabel(
            text="",
            color=Color.WHITE,
            text_align=AlignContent.LEFT,
            autotooltip=True,
            font=self.font.get(8),
            rtl=self.rtl
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
                sync_str = f"{sync_percentage:.2f}"
                mediantime = info.get('mediantime')
                mediantime_date = datetime.fromtimestamp(mediantime).strftime('%Y-%m-%d %H:%M:%S')
                status_icon = "images/on.png"
                
            else:
                self.node_status = None
                status_icon = "images/off.png"

            bitcoinz_size = int(self.utils.get_bitcoinz_size())

            await self.update_statusbar(status_icon, blocks, sync_str, mediantime_date, bitcoinz_size)
            await asyncio.sleep(5)


    async def update_statusbar(self, status_icon, blocks, sync, mediantime, bitcoinz_size):
        if self.rtl:
            blocks = self.units.arabic_digits(str(blocks))
            mediantime = self.units.arabic_digits(mediantime)
            sync = self.units.arabic_digits(sync)
            bitcoinz_size = self.units.arabic_digits(str(bitcoinz_size))
            size_text = f"{bitcoinz_size} ميجا"
        else:
            blocks = str(blocks)
            size_text = f"{bitcoinz_size} MB"
        self.status_icon.image = status_icon
        self.blocks_value.text = blocks
        self.date_value.text = mediantime
        self.sync_value.text = f"{sync}%"
        self.size_value.text = size_text
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
                    if self.rtl:
                        netsol = self.units.arabic_digits(str(netsol))
                        netsol_text = f"{netsol} سول/ث"
                    else:
                        netsol_text = f"{netsol} Sol/s"
                    self.network_value.text = netsol_text
            await asyncio.sleep(5)

    
    async def update_connections_count(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            connection_count,_ = await self.commands.getConnectionCount()
            if connection_count is not None:
                if self.rtl:
                    connection_count = self.units.arabic_digits(connection_count)
                self.connections_value.text = connection_count


    async def update_deprecationinfo(self, widget):
        deprecationinfo, _ = await self.commands.getDeprecationInfo()
        if deprecationinfo is not None:
            if isinstance(deprecationinfo, str):
                info = json.loads(deprecationinfo)
            if info is not None:
                deprecation = info.get('deprecationheight')
                if self.rtl:
                    deprecation = self.units.arabic_digits(str(deprecation))
                else:
                    deprecation = str(deprecation)
                self.deprecation_value.text = deprecation