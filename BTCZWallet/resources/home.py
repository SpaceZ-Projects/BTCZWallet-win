
import asyncio
import aiohttp
from datetime import datetime
import json
from aiohttp_socks import ProxyConnector, ProxyConnectionError

from toga import (
    App, Box, Label, ImageView, Window, Button,
    Selection, Divider
)
from ..framework import Os, FlatStyle, ToolTip, Forms, RightToLeft
from toga.style.pack import Pack
from toga.constants import (
    COLUMN, ROW, TOP, LEFT, BOLD,
    CENTER, Direction, RIGHT
)
from toga.colors import rgb, GRAY, WHITE, RED, BLACK, YELLOW

from .curve import Curve


class Languages(Window):
    def __init__(self, main:Window, settings, utils, tr, font):
        super().__init__(
            size= (200,100),
            resizable=False
        )

        self.main = main

        self.utils = utils
        self.settings = settings
        self.tr = tr
        self.font = font

        self.title = self.tr.title("language_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.languages_selection = Selection(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                padding = (20,10,10,10)
            ),
            items=[
                {"language": "English"},
                {"language": "Français"},
                {"language": "العربية"},
                {"language": "русский"}
            ],
            accessor="language"
        )
        self.languages_selection._impl.native.Font = self.font.get(self.tr.size("languages_selection"), True)
        self.languages_selection._impl.native.FlatStyle = FlatStyle.STANDARD
        self.languages_selection._impl.native.DropDownHeight = 150
        if self.rtl:
            self.languages_selection._impl.native.RightToLeft = RightToLeft.YES

        self.close_button = Button(
            text=self.tr.text("close_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_languages_window
        )
        self.close_button._impl.native.Font = self.font.get(self.tr.size("close_button"), True)
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.languages_selection,
            self.close_button
        )

        self.load_languages()


    def load_languages(self):
        lang = self.settings.language()
        language_map = {
            "French": "Français",
            "Arabic": "العربية",
            "Russian": "русский"
        }
        language = language_map.get(lang, "English")
        self.languages_selection.value = self.languages_selection.items.find(language)
        self.languages_selection.on_change = self.update_language


    def update_language(self, selection):
        def on_result(widget, result):
            if result is None:
                self.close()
                self.app.current_window = self.main
        value = self.languages_selection.value.language
        if value == "Français":
            value = "French"
        elif value == "العربية":
            value = "Arabic"
        elif value == "русский":
            value = "Russian"
        self.settings.update_settings("lang", value)
        self.info_dialog(
            title=self.tr.title("language_dialog"),
            message=self.tr.message("language_dialog"),
            on_result=on_result
        )


    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)


    def close_languages_window(self, button):
        self.close()


class Currency(Window):
    def __init__(self, main:Window, settings, utils, tr, font):
        super().__init__(
            size= (200,100),
            resizable=False
        )

        self.main = main

        self.utils = utils
        self.settings = settings
        self.tr = tr
        self.font = font

        self.title = self.tr.title("currency_window")
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

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
                padding = (20,10,10,10)
            ),
            items=[
                {"currency": ""}
            ],
            accessor="currency"
        )
        self.currencies_selection._impl.native.Font = self.font.get(self.tr.size("currencies_selection"), True)
        self.currencies_selection._impl.native.FlatStyle = FlatStyle.STANDARD
        self.currencies_selection._impl.native.DropDownHeight = 150
        if self.rtl:
            self.currencies_selection._impl.native.RightToLeft = RightToLeft.YES

        self.close_button = Button(
            text=self.tr.text("close_button"),
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
        self.close_button._impl.native.Font = self.font.get(self.tr.size("close_button"), True)
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
                self.app.current_window = self.main
        selected_currency = self.currencies_selection.value.currency
        if not selected_currency:
            return
        currencies_data = self.get_currencies_data()
        self.settings.update_settings("currency", selected_currency.lower())
        if selected_currency in currencies_data:
            symbol = currencies_data[selected_currency]["symbol"]
            self.settings.update_settings("symbol", symbol)
        self.info_dialog(
            title=self.tr.title("currency_dialog"),
            message=self.tr.message("currency_dialog"),
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
    def __init__(self, app:App, main:Window, settings, utils, units, commands, tr, font):
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

        self.utils = utils
        self.units = units
        self.commands = commands
        self.settings = settings
        self.tr = tr
        self.font = font
        
        self.curve = Curve(self.app, settings, utils, units)
        self.tooltip = ToolTip()

        self.home_toggle = None
        self.cap_toggle = None
        self.volume_toggle = None
        self.circulating_toggle = None
        self.curve_image = None
        self.circulating = None
        self.current_block = None
        self.deprecation = None

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.coingecko_icon = ImageView(
            image="images/coingecko.png",
            style=Pack(
                background_color = rgb(40,43,48),
                padding = self.tr.padding("coingecko_icon"),
            )
        )
        self.coingecko_label = Label(
            text="coingecko",
            style=Pack(
                text_align = RIGHT,
                background_color = rgb(40,43,48),
                color = WHITE,
                padding = self.tr.padding("coingecko_label")
            )
        )
        self.coingecko_label._impl.native.Font = self.font.get(12, True)

        self.last_updated_label = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("last_updated_label"),
                background_color = rgb(40,43,48),
                color = GRAY,
                padding = (9,0,0,5),
                flex = 1
            )
        )
        self.last_updated_label._impl.native.Font = self.font.get(9)

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
            text=self.tr.text("price_label"),
            style=Pack(
                text_align = self.tr.align("price_label"),
                background_color = rgb(30,33,36),
                color = GRAY,
                padding = 10
            )
        )
        self.price_label._impl.native.Font = self.font.get(self.tr.size("price_label"))

        self.price_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("price_value"),
                background_color = rgb(30,33,36),
                color = WHITE,
                padding_top = 13,
                flex = 1
            )
        )
        self.price_value._impl.native.Font = self.font.get(self.tr.size("price_value"), True)

        self.percentage_24_label = Label(
            text=self.tr.text("percentage_24_label"),
            style=Pack(
                text_align = self.tr.align("percentage_24_label"),
                background_color = rgb(30,33,36),
                color = GRAY,
                padding = 10
            )
        )
        self.percentage_24_label._impl.native.Font = self.font.get(self.tr.size("percentage_24_label"))

        self.percentage_24_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("percentage_24_value"),
                background_color = rgb(30,33,36),
                color = WHITE,
                padding_top = 13,
                flex = 1
            )
        )
        self.percentage_24_value._impl.native.Font = self.font.get(self.tr.size("percentage_24_value"), True)

        self.percentage_7_label = Label(
            text=self.tr.text("percentage_7_label"),
            style=Pack(
                text_align = self.tr.align("percentage_7_label"),
                background_color = rgb(30,33,36),
                color = GRAY,
                padding = 10
            )
        )
        self.percentage_7_label._impl.native.Font = self.font.get(self.tr.size("percentage_7_label"))

        self.percentage_7_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("percentage_7_value"),
                background_color = rgb(30,33,36),
                color = WHITE,
                padding_top = 13,
                flex = 1
            )
        )
        self.percentage_7_value._impl.native.Font = self.font.get(self.tr.size("percentage_7_value"), True)

        self.cap_label = Label(
            text=self.tr.text("cap_label"),
            style=Pack(
                text_align = self.tr.align("cap_label"),
                background_color = rgb(30,33,36),
                color = GRAY,
                padding = 10
            )
        )
        self.cap_label._impl.native.Font = self.font.get(self.tr.size("cap_label"))

        self.cap_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("cap_value"),
                background_color = rgb(30,33,36),
                color = WHITE,
                padding_top = 13,
                flex = 1
            )
        )
        self.cap_value._impl.native.Font = self.font.get(self.tr.size("cap_value"), True)

        self.volume_label = Label(
            text=self.tr.text("volume_label"),
            style=Pack(
                text_align = self.tr.align("volume_label"),
                background_color = rgb(30,33,36),
                color = GRAY,
                padding = 10
            )
        )
        self.volume_label._impl.native.Font = self.font.get(self.tr.size("volume_label"))

        self.volume_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("volume_value"),
                background_color = rgb(30,33,36),
                color = WHITE,
                padding_top = 13,
                flex = 1
            )
        )
        self.volume_value._impl.native.Font = self.font.get(self.tr.size("volume_value"), True)

        self.circulating_label = Label(
            text=self.tr.text("circulating_label"),
            style=Pack(
                text_align = LEFT,
                background_color = rgb(30,33,36),
                color = GRAY,
                padding = 10
            )
        )
        self.circulating_label._impl.native.Font = self.font.get(self.tr.size("circulating_label"))

        self.circulating_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("circulating_value"),
                background_color = rgb(30,33,36),
                color = WHITE,
                padding_top = 13,
                flex = 1
            )
        )
        self.circulating_value._impl.native.Font = self.font.get(self.tr.size("circulating_value"), True)
        self.circulating_value._impl.native.Click += self.circulating_value_click

        self.max_emissions_value = Label(
            text=self.tr.text("max_emissions_value"),
            style=Pack(
                text_align = self.tr.align("max_emissions_value"),
                background_color = rgb(30,33,36),
                color = YELLOW,
            )
        )
        self.max_emissions_value._impl.native.Font = self.font.get(self.tr.size("max_emissions_value"), True)

        self.circulating_divider = Divider(
            direction=Direction.HORIZONTAL,
            style=Pack(
                background_color = WHITE,
                width = self.tr.size("circulating_divider"),
                flex = 1
            )
        )

        self.circulating_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = self.tr.align("circulating_box"),
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
                text_align = CENTER,
                background_color = rgb(40,43,48),
                color = WHITE,
                flex = 1,
                padding = (0,0,15,0)
            )
        )
        self.halving_label._impl.native.Font = self.font.get(self.tr.size("halving_label"), True)

        self.deprecation_label = Label(
            text="",
            style=Pack(
                text_align = CENTER,
                background_color = rgb(40,43,48),
                color = WHITE,
                flex = 1,
                padding_bottom = 15
            )
        )
        self.deprecation_label._impl.native.Font = self.font.get(self.tr.size("halving_label"), True)


        self.info_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER
            )
        )


    async def insert_widgets(self, widget):
        if not self.home_toggle:
            self.add(
                self.coingecko_box, 
                self.market_box,
                self.bitcoinz_curve,
                self.info_box
            )
            self.info_box.add(
                self.halving_label,
                self.deprecation_label
            )
            if self.rtl:
                self.coingecko_box.add(
                    self.last_updated_label,
                    self.coingecko_label,
                    self.coingecko_icon
                )
            else:
                self.coingecko_box.add(
                    self.coingecko_icon,
                    self.coingecko_label,
                    self.last_updated_label
                )
            if self.rtl:
                self.market_box.add(
                    self.circulating_box,
                    self.circulating_label,
                    self.percentage_7_value,
                    self.percentage_7_label,
                    self.percentage_24_value,
                    self.percentage_24_label,
                    self.price_value,
                    self.price_label
                )
            else:
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
            self.app.add_background_task(self.update_remaining_deprecation)


    async def fetch_marketcap(self):
        api = "https://api.coingecko.com/api/v3/coins/bitcoinz"
        tor_enabled = self.settings.tor_network()
        if tor_enabled:
            torrc = self.utils.read_torrc()
            socks_port = torrc.get("SocksPort")
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                headers={'User-Agent': 'Mozilla/5.0'}
                async with session.get(api, headers=headers, timeout=10) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except ProxyConnectionError as e:
            return None
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None
        

    async def update_circulating_supply(self, widget):
        while True:
            self.circulating = self.units.calculate_circulating(int(self.current_block))
            remaining_blocks = self.units.remaining_blocks_until_halving(int(self.current_block))
            remaining_days = self.units.remaining_days_until_halving(int(self.current_block))
            circulating = int(self.circulating)
            if self.rtl:
                circulating = self.units.arabic_digits(str(circulating))
                remaining_blocks = self.units.arabic_digits(str(remaining_blocks))
                remaining_days = self.units.arabic_digits(str(remaining_days))
            if not self.circulating_toggle:
                self.circulating_value.text = circulating
            halving_text = self.tr.text("halving_label")
            remaining_text = self.tr.text("remaining_label")
            blocks_text = self.tr.text("blocks_label")
            days_text = self.tr.text("days_label")
            self.halving_label.text = f"{halving_text} {remaining_blocks} {blocks_text}\n{remaining_text} {remaining_days} {days_text}"
            await asyncio.sleep(10)


    async def update_remaining_deprecation(self, widget):
        while True:
            remaining_blocks = self.units.remaining_blocks_until_deprecation(int(self.deprecation), int(self.current_block))
            remaining_days = self.units.remaining_days_until_deprecation(int(self.deprecation), int(self.current_block))
            if self.rtl:
                remaining_blocks = self.units.arabic_digits(str(remaining_blocks))
                remaining_days = self.units.arabic_digits(str(remaining_days))
            self.deprecation_label.text = f"Deprecation in {remaining_blocks} blocks\nRemaining {remaining_days} days"
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

                if self.rtl:
                    formatted_last_updated = self.units.arabic_digits(formatted_last_updated)
                    btcz_price = self.units.arabic_digits(btcz_price)
                    price_percentage_24 = self.units.arabic_digits(str(price_percentage_24))
                    price_percentage_7d = self.units.arabic_digits(str(price_percentage_7d))
                    market_cap = self.units.arabic_digits(str(market_cap))
                    market_volume = self.units.arabic_digits(str(market_volume))
                    self.price_value.text = f"{self.settings.symbol()} {btcz_price}"
                    self.percentage_24_value.text = f"% {price_percentage_24}"
                    self.percentage_7_value.text = f"% {price_percentage_7d}"
                    self.cap_value.text = f"{self.settings.symbol()} {market_cap}"
                    self.volume_value.text = f"{self.settings.symbol()} {market_volume}"
                    self.last_updated_label.text = f"UTC {formatted_last_updated}"
                else:
                    self.price_value.text = f"{btcz_price} {self.settings.symbol()}"
                    self.percentage_24_value.text = f"{price_percentage_24} %"
                    self.percentage_7_value.text = f"{price_percentage_7d} %"
                    self.cap_value.text = f"{market_cap} {self.settings.symbol()}"
                    self.volume_value.text = f"{market_volume} {self.settings.symbol()}"
                    self.last_updated_label.text = f"{formatted_last_updated} UTC"

            await asyncio.sleep(601)


    async def update_marketchart(self, widget):
        while True:
            data = await self.curve.fetch_marketchart()
            if data:
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
                if self.rtl:
                    self.market_box.insert(
                        0, self.cap_label
                    )
                    self.market_box.insert(
                        0, self.cap_value
                    )
                else:
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
                if self.rtl:
                    self.market_box.insert(
                        0, self.volume_label
                    )
                    self.market_box.insert(
                        0, self.volume_value
                    )
                else:
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
        self.circulating_value.style.padding_top = 2
        circulating_percentage = f"{(self.circulating / 21_000_000_000) * 100:.1f}%"
        self.tooltip.insert(self.circulating_value._impl.native, circulating_percentage)
        self.tooltip.insert(self.max_emissions_value._impl.native, circulating_percentage)
        await asyncio.sleep(5)
        self.circulating_box.remove(
            self.circulating_divider,
            self.max_emissions_value
        )
        self.circulating_value.style.padding_top = 13
        self.tooltip.insert(self.circulating_value._impl.native, "")
        self.circulating_toggle = None