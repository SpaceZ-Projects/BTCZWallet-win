
import asyncio
import json

from framework import (
    App, Box, DockStyle, Color, Label,
    Font, FontStyle, AlignLabel, Image, SizeMode
)

from .client import Client
from .utils import Utils

class Wallet(Box):
    def __init__(self):
        super().__init__()

        self.app = App()
        self.commands = Client()
        self.utils = Utils()

        self.dockstyle = DockStyle.FILL
        self.autosize = False
        self.background_color = Color.rgb(40,43,48)
        self.padding = (5,5,5,5)

        self.balances_box = Box(
            dockstyle=DockStyle.RIGHT,
            size=(1, 0),
            background_color=Color.rgb(30,33,36),
            autosize=False,
            padding = (5,5,5,5)
        )
        self.total_label = Label(
            text="Total Balances",
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            text_color=Color.rgb(40,43,48),
            dockstyle=DockStyle.TOP,
            aligne=AlignLabel.CENTER,
            size=10,
            visible=False
        )
        self.total_value = Label(
            text="",
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            text_color=Color.rgb(40,43,48),
            dockstyle=DockStyle.TOP,
            aligne=AlignLabel.CENTER,
            size=11
        )
        self.balances_type = Box(
            dockstyle=DockStyle.BOTTOM,
            autosize=False,
            background_color=Color.rgb(40,43,48),
            size=(0,20),
            visible=False
        )
        self.transparent_value = Label(
            text="",
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            text_color=Color.rgb(30,33,36),
            dockstyle=DockStyle.LEFT,
            aligne=AlignLabel.CENTER,
            size=9
        )
        self.private_value = Label(
            text="",
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            text_color=Color.rgb(30,33,36),
            dockstyle=DockStyle.RIGHT,
            aligne=AlignLabel.CENTER,
            size=9
        )
        self.bitcoinz_logo = Image(
            image="images/BitcoinZ.png",
            size=(75,75),
            size_mode=SizeMode.ZOOM,
            location=(-75, 5)
        )
        self.bitcoinz_title = Label(
            text="BitcoinZ Full Node Wallet",
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            text_color=Color.rgb(30,33,36),
            aligne=AlignLabel.CENTER,
            location=(100, 30),
            width=240,
            size=14
        )

    async def insert_widgets(self):
        await self.gradient((30,33,36), steps=25)
        self.insert(
            [
                self.bitcoinz_logo,
                self.bitcoinz_title,
                self.balances_box
            ]
        )
        self.balances_box.insert(
            [
                self.total_value,
                self.total_label,
                self.balances_type
            ]
        )
        self.balances_type.insert(
            [
                self.transparent_value,
                self.private_value
            ]
        )
        self.app.run_async(self.display_balances_widgets())
        self.app.run_async(self.display_bitcoinz_logo())

    async def display_balances_widgets(self):
        self.app.run_async(self.balances_box.resize((350,110), steps=60, duration=0.01))
        await self.balances_box.gradient((40,43,48), steps=25)
        self.total_label.visible = True
        await self.total_label.gradient_color((255,255,255), steps=50)
        self.app.run_async(self.update_balances())
        await self.total_value.gradient_color((255,255,255), steps=25)
        self.balances_type.visible = True
        await self.balances_type.gradient((30,33,36), steps=25)
        self.app.run_async(self.transparent_value.gradient_color((255,255,0), steps=25))
        await self.private_value.gradient_color((114,137,218), steps=25)

    async def display_bitcoinz_logo(self):
        await self.bitcoinz_logo.slide((5,5), steps=15, duration=0.01)
        self.bitcoinz_logo.dockstyle = DockStyle.LEFT
        await self.bitcoinz_title.gradient_color((255,255,255))

    async def update_balances(self):
        while True:
            totalbalances = await self.commands.z_getTotalBalance()
            if totalbalances is not None:
                balances = json.loads(totalbalances[0])
                totalbalance = self.utils.format_balance(float(balances.get('total')))
                transparentbalance = self.utils.format_balance(float(balances.get('transparent')))
                privatebalance = self.utils.format_balance(float(balances.get('private')))
                self.total_value.text = totalbalance
                self.transparent_value.text = transparentbalance
                self.private_value.text = privatebalance
            await asyncio.sleep(5)