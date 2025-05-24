
import asyncio
import aiohttp
from datetime import datetime
import json
from aiohttp_socks import ProxyConnector, ProxyConnectionError

from toga import (
    App, Box, Label, ImageView, Window, Button,
    Selection, Divider
)
from ..framework import Os, FlatStyle, ToolTip, Forms
from toga.style.pack import Pack
from toga.constants import (
    COLUMN, ROW, TOP, LEFT, BOLD, RIGHT,
    CENTER, Direction
)
from toga.colors import rgb, GRAY, WHITE, RED, BLACK, YELLOW

from .units import Units
from .client import Client
from .curve import Curve
from .settings import Settings
from .utils import Utils


class Currency(Window):
    def __init__(self):
        super().__init__(
            size= (200,100),
            resizable=False,
            minimizable=False,
            closable=False
        )

        self.utils = Utils(self.app)
        self.settings = Settings(self.app)

        self.title = "Change Currency"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.currencies_selection = Selection(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                padding = (20,10,10,10)
            ),
            items=[
                {"currency": ""}
            ],
            accessor="currency"
        )
        self.currencies_selection._impl.native.FlatStyle = FlatStyle.STANDARD
        self.currencies_selection._impl.native.DropDownHeight = 150

        self.close_button = Button(
            text="Close",
            style=Pack(
                color = RED,
                font_size=10,
                font_weight = BOLD,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_currency_window
        )
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.currencies_selection,
            self.close_button
        )

        self.load_currencies()

    
    def load_currencies(self):
        current_currency = self.settings.currency()
        currencies_data = self.get_currencies_list()
        self.currencies_selection.items.clear()
        for currency in currencies_data:
            self.currencies_selection.items.append(currency)
        self.currencies_selection.value = self.currencies_selection.items.find(current_currency.upper())
        self.currencies_selection.on_change = self.update_currency

    def update_currency(self, selection):
        def on_result(widget, result):
            if result is None:
                self.close()
        selected_currency = self.currencies_selection.value.currency
        if not selected_currency:
            return
        currencies_data = self.get_currencies_data()
        self.settings.update_settings("currency", selected_currency.lower())
        if selected_currency in currencies_data:
            symbol = currencies_data[selected_currency]["symbol"]
            self.settings.update_settings("symbol", symbol)
        self.info_dialog(
            title="Currency Changed",
            message="currency setting has been updated, change will take effect in a few minutes.",
            on_result=on_result
        )

    def get_currencies_data(self):
        try:
            currencies_json = Os.Path.Combine(str(self.app.paths.app), 'resources', 'currencies.json')
            with open(currencies_json, 'r') as f:
                currencies_data = json.load(f)
                return currencies_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return None
        
    def get_currencies_list(self):
        currencies_data = self.get_currencies_data()
        if currencies_data:
            currencies_items = [{"currency": currency} for currency in currencies_data.keys()]
            return currencies_items

    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)


    def close_currency_window(self, button):
        self.close()


class Home(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )

        self.app = app
        self.main = main

        self.units = Units(self.app)
        self.commands = Client(self.app)
        self.curve = Curve(self.app)
        self.settings = Settings(self.app)
        self.tooltip = ToolTip()

        self.home_toggle = None
        self.cap_toggle = None
        self.volume_toggle = None
        self.circulating_toggle = None
        self.curve_image = None
        self.circulating = None

        self.coingecko_icon = ImageView(
            image="images/coingecko.png",
            style=Pack(
                background_color = rgb(40,43,48),
                padding = (5,0,0,10),
            )
        )
        self.coingecko_label = Label(
            text="coingecko",
            style=Pack(
                font_size = 12,
                text_align = LEFT,
                background_color = rgb(40,43,48),
                color = WHITE,
                font_weight = BOLD,
                padding = (5,0,0,5)
            )
        )
        self.last_updated_label = Label(
            "",
            style=Pack(
                font_size = 9,
                text_align = LEFT,
                background_color = rgb(40,43,48),
                color = GRAY,
                font_weight = BOLD,
                padding = (10,0,0,5),
                flex = 1
            )
        )
        self.coingecko_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48)
            )
        )
        self.market_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = TOP,
                height = 45,
                padding = (5,5,0,5)
            )
        )
        self.market_box._impl.native.Resize += self._add_cap_on_resize
        self.market_box._impl.native.Resize += self._add_volume_on_resize

        self.price_label = Label(
            text="Price :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.price_value = Label(
            text="",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = WHITE,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )
        self.percentage_24_label = Label(
            "Change 24h :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.percentage_24_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = WHITE,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )
        self.percentage_7_label = Label(
            "Change 7d :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.percentage_7_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = WHITE,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )

        self.cap_label = Label(
            "Cap :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.cap_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = WHITE,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )

        self.volume_label = Label(
            "Volume :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.volume_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = WHITE,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )

        self.circulating_label = Label(
            "Circulating :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.circulating_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = WHITE,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )
        self.circulating_value._impl.native.Click += self.circulating_value_click

        self.max_emissions_value = Label(
            "21000000000",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = YELLOW,
                font_weight = BOLD
            )
        )

        self.circulating_divider = Divider(
            direction=Direction.HORIZONTAL,
            style=Pack(
                background_color = WHITE,
                width = 100,
                flex = 1
            )
        )

        self.circulating_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = LEFT,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.bitcoinz_curve = ImageView(
            style=Pack(
                alignment = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )

        self.halving_label = Label(
            text="",
            style=Pack(
                font_size = 14,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                color = WHITE,
                font_weight = BOLD,
                padding_top = 10
            )
        )

        self.remaining_label = Label(
            text="",
            style=Pack(
                font_size = 14,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                color = WHITE,
                font_weight = BOLD,
                padding_bottom = 10
            )
        )


    async def insert_widgets(self, widget):
        if not self.home_toggle:
            self.add(
                self.coingecko_box, 
                self.market_box,
                self.bitcoinz_curve,
                self.halving_label,
                self.remaining_label
            )
            self.coingecko_box.add(
                self.coingecko_icon,
                self.coingecko_label,
                self.last_updated_label
            )
            self.market_box.add(
                self.price_label,
                self.price_value,
                self.percentage_24_label,
                self.percentage_24_value,
                self.percentage_7_label,
                self.percentage_7_value,
                self.circulating_label,
                self.circulating_box
            )
            self.circulating_box.add(
                self.circulating_value
            )

            self.home_toggle = True

            self.app.add_background_task(self.update_marketchart)
            self.app.add_background_task(self.update_marketcap)
            self.app.add_background_task(self.update_circulating_supply)


    async def fetch_marketcap(self):
        api = "https://api.coingecko.com/api/v3/coins/bitcoinz"
        tor_enabled = self.settings.tor_network()
        if tor_enabled:
            connector = ProxyConnector.from_url('socks5://127.0.0.1:9050')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                headers={'User-Agent': 'Mozilla/5.0'}
                async with session.get(api, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except ProxyConnectionError:
            return None
        except Exception:
            return None

    async def update_circulating_supply(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            current_block,_ = await self.commands.getBlockCount()
            if not current_block:
                return
            self.circulating = self.units.calculate_circulating(int(current_block))
            remaiming_blocks = self.units.remaining_blocks_until_halving(int(current_block))
            remaining_days = self.units.remaining_days_until_halving(int(current_block))
            if not self.circulating_toggle:
                self.circulating_value.text = int(self.circulating)
            self.halving_label.text = f"Next Halving in {remaiming_blocks} Blocks"
            self.remaining_label.text = f"Remaining {remaining_days} Days"
            await asyncio.sleep(10)


    async def update_marketcap(self, widget):
        while True:
            data = await self.fetch_marketcap()
            if data:
                market_price = data["market_data"]["current_price"][self.settings.currency()]
                market_cap = data["market_data"]["market_cap"][self.settings.currency()]
                market_volume = data["market_data"]["total_volume"][self.settings.currency()]
                price_percentage_24 = data["market_data"]["price_change_percentage_24h"]
                price_percentage_7d = data["market_data"]["price_change_percentage_7d"]
                last_updated = data["market_data"]["last_updated"]

                last_updated_datetime = datetime.fromisoformat(last_updated.replace("Z", ""))
                formatted_last_updated = last_updated_datetime.strftime("%Y-%m-%d %H:%M:%S")
                btcz_price = self.units.format_price(market_price)
                self.settings.update_settings("btcz_price", btcz_price)
                self.price_value.text = f"{btcz_price} {self.settings.symbol()}"
                self.percentage_24_value.text = f"{price_percentage_24} %"
                self.percentage_7_value.text = f"{price_percentage_7d} %"
                self.cap_value.text = f"{market_cap} {self.settings.symbol()}"
                self.volume_value.text = f"{market_volume} {self.settings.symbol()}"
                self.last_updated_label.text = formatted_last_updated

            await asyncio.sleep(601)


    async def update_marketchart(self, widget):
        while True:
            data = await self.curve.fetch_marketchart()
            if not data:
                self.main.error_dialog(
                    title="Request Error",
                    message="Too many requests. The market cap will be updated in the next 10 minutes."
                )
            else:
                curve_image = self.curve.create_curve(data)
                if curve_image:
                    self.bitcoinz_curve.image = curve_image
                    if self.curve_image:
                        Os.File.Delete(self.curve_image)
                    self.curve_image = curve_image

            await asyncio.sleep(602)


    def clear_cache(self):
        if self.curve_image:
            Os.File.Delete(self.curve_image)

    def _add_cap_on_resize(self, sender, event):
        box_width = self.market_box._impl.native.Width
        if not self.cap_toggle:
            if box_width >= 1000:
                self.market_box.add(
                    self.cap_label,
                    self.cap_value
                )
                self.cap_toggle = True
        elif self.cap_toggle:
            if box_width < 1000:
                self.market_box.remove(
                    self.cap_label,
                    self.cap_value
                )
                self.cap_toggle = None

    def _add_volume_on_resize(self, sender, event):
        box_width = self.market_box._impl.native.Width
        if not self.volume_toggle:
            if box_width >= 1200:
                self.market_box.add(
                    self.volume_label,
                    self.volume_value
                )
                self.volume_toggle = True
        elif self.volume_toggle:
            if box_width < 1200:
                self.market_box.remove(
                    self.volume_label,
                    self.volume_value
                )
                self.volume_toggle = None


    def circulating_value_click(self, sender, event):
        if event.Button == Forms.MouseButtons.Right:
            return
        if not self.circulating_toggle:
            self.circulating_toggle = True
            self.app.add_background_task(self.show_max_emissions)

    async def show_max_emissions(self, task):
        self.circulating_box.add(
            self.circulating_divider,
            self.max_emissions_value
        )
        self.circulating_value.style.padding = (2,0,2,0)
        circulating_percentage = f"{(self.circulating / 21_000_000_000) * 100:.1f}%"
        self.tooltip.insert(self.circulating_value._impl.native, circulating_percentage)
        self.tooltip.insert(self.max_emissions_value._impl.native, circulating_percentage)
        await asyncio.sleep(5)
        self.circulating_box.remove(
            self.circulating_divider,
            self.max_emissions_value
        )
        self.circulating_value.style.padding = (11,0,10,0)
        self.tooltip.insert(self.circulating_value._impl.native, "")
        self.circulating_toggle = None