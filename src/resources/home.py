
import asyncio
import aiohttp
from datetime import datetime

from toga import App, Box, Label
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, TOP, LEFT, BOLD, RIGHT
from toga.colors import rgb, GRAY, WHITE

from .utils import Utils


class Home(Box):
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
        self.utils = Utils(self.app)

        self.home_toggle = None
        self.cap_toggle = None
        self.volume_toggle = None

        self.market_label = Label(
            text="MarketCap :",
            style=Pack(
                font_size = 12,
                text_align = LEFT,
                background_color = rgb(40,43,48),
                color = GRAY,
                font_weight = BOLD,
                padding = (10,0,0,10)
            )
        )
        self.market_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = TOP,
                height = 45,
                padding = (5,10,0,5)
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

        self.last_updated_label = Label(
            "",
            style=Pack(
                font_size = 9,
                text_align = RIGHT,
                background_color = rgb(40,43,48),
                color = GRAY,
                font_weight = BOLD,
                padding = (5,10,0,0),
                flex = 1
            )
        )


    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.home_toggle:
            self.add(
                self.market_label, 
                self.market_box,
                self.last_updated_label
            )
            self.market_box.add(
                self.price_label,
                self.price_value,
                self.percentage_24_label,
                self.percentage_24_value,
                self.percentage_7_label,
                self.percentage_7_value
            )

            self.home_toggle = True

            self.app.add_background_task(self.update_marketcap)


    async def update_marketcap(self, widget):
        api_url = "https://api.coingecko.com/api/v3/coins/bitcoinz"
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.update_marketcap_values(data)
                        else:
                            print("Failed to fetch data. Status code:", response.status)
                            return None
            except Exception as e:
                print(f"Error occurred during fetch: {e}")
                return None
            await asyncio.sleep(601)


    def update_marketcap_values(self, data):
        market_price = data["market_data"]["current_price"]["usd"]
        market_cap = data["market_data"]["market_cap"]["usd"]
        market_volume = data["market_data"]["total_volume"]["usd"]
        price_percentage_24 = data["market_data"]["price_change_percentage_24h"]
        price_percentage_7d = data["market_data"]["price_change_percentage_7d"]
        last_updated = data["market_data"]["last_updated"]

        last_updated_datetime = datetime.fromisoformat(last_updated.replace("Z", ""))
        formatted_last_updated = last_updated_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
        btcz_price = self.utils.format_price(market_price)
        self.price_value.text = f"${btcz_price}"
        self.percentage_24_value.text = f"%{price_percentage_24}"
        self.percentage_7_value.text = f"%{price_percentage_7d}"
        self.cap_value.text = f"${market_cap}"
        self.volume_value.text = f"${market_volume}"
        self.last_updated_label.text = formatted_last_updated

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