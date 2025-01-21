
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
                padding = (5, 10,0,5)
            )
        )

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

        self.percentage_14_label = Label(
            "Change 14d :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.percentage_14_value = Label(
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
                self.percentage_7_value,
                self.percentage_14_label,
                self.percentage_14_value
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
        price_percentage_14d = data["market_data"]["price_change_percentage_14d"]
        total_supply = data["market_data"]["total_supply"]
        max_supply = data["market_data"]["max_supply"]
        circulating_supply = data["market_data"]["circulating_supply"]
        sentiment = data["sentiment_votes_up_percentage"]
        last_updated = data["market_data"]["last_updated"]
        print(last_updated)

        last_updated_datetime = datetime.fromisoformat(last_updated.replace("Z", ""))
        formatted_last_updated = last_updated_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
        btcz_price = self.utils.format_price(market_price)
        self.price_value.text = f"${btcz_price}"
        self.percentage_24_value.text = f"%{price_percentage_24}"
        self.percentage_7_value.text = f"%{price_percentage_7d}"
        self.percentage_14_value.text = f"%{price_percentage_14d}"
        self.last_updated_label.text = formatted_last_updated