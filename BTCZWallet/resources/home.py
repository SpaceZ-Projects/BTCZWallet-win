
import asyncio
import json
from pathlib import Path

from toga import (
    App, Box, Window, Button, Selection
)
from ..framework import (
    Os, FlatStyle, ToolTip, RightToLeft, WebView,
    Color
)
from toga.style.pack import Pack
from toga.constants import COLUMN, BOLD, CENTER
from toga.colors import rgb, WHITE, RED, BLACK


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
        position_center = self.utils.window_center_to_parent(self.main, self)
        self.position = position_center
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

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
            "Arabic": "العربية"
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
        position_center = self.utils.window_center_to_parent(self.main, self)
        self.position = position_center
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

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
    def __init__(self, app:App, main:Window, settings, utils, units, tr, font):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                alignment = CENTER
            )
        )

        self.app = app
        self.main = main

        self.utils = utils
        self.units = units
        self.settings = settings
        self.tr = tr
        self.font = font
        
        self.tooltip = ToolTip()

        self.home_toggle = None
        self.cap_toggle = None
        self.volume_toggle = None
        self.circulating_toggle = None
        self.circulating = None
        self.current_blocks = None
        self.deprecation = None
        self.market_retrieved = None

        html_path = Path(__file__).parent / "html" / "home.html"
        self.market_output = WebView(
            app=self.app,
            content=html_path,
            background_color = Color.rgb(40,43,48)
        )
        self._impl.native.Controls.Add(self.market_output.control)


    def insert_widgets(self):
        if not self.home_toggle:
            self.home_toggle = True
            self.app.loop.create_task(self.update_marketcap())
            self.app.loop.create_task(self.update_marketchart())
            self.app.loop.create_task(self.update_circulating_supply())
            self.app.loop.create_task(self.update_remaining_deprecation())
        
        

    async def update_circulating_supply(self):
        self.app.console.event_log(f"✔: Circulating supply")
        while True:
            self.circulating = self.units.calculate_circulating(int(self.current_blocks))
            remaining_blocks = self.units.remaining_blocks_until_halving(int(self.current_blocks))
            remaining_days = self.units.remaining_days_until_halving(int(self.current_blocks))
            circulating = int(self.circulating)

            self.market_output.control.CoreWebView2.ExecuteScriptAsync(f"setCirculating('{circulating}');")
            blocks_text = self.tr.text("blocks_label")
            days_text = self.tr.text("days_label")
            circulating_percentage = f"{(self.circulating / 21_000_000_000) * 100:.1f} %"
            self.market_output.control.CoreWebView2.ExecuteScriptAsync(f"setCirculatingTooltip('{circulating_percentage}');")
            self.market_output.control.CoreWebView2.ExecuteScriptAsync(
                f"setNextHalving('{remaining_blocks} {blocks_text} / {remaining_days} {days_text}');"
            )
            await asyncio.sleep(10)


    async def update_remaining_deprecation(self):
        self.app.console.event_log(f"✔: Remaining deprecation")
        while True:
            remaining_blocks = self.units.remaining_blocks_until_deprecation(int(self.deprecation), int(self.current_blocks))
            remaining_days = self.units.remaining_days_until_deprecation(int(self.deprecation), int(self.current_blocks))
            self.market_output.control.CoreWebView2.ExecuteScriptAsync(
                f"setDeprecation('{remaining_blocks} Blocks / {remaining_days} Days');"
            )
            await asyncio.sleep(10)


    async def update_marketcap(self):
        self.app.console.event_log(f"✔: Market cap")
        while True:
            data = await self.utils.fetch_marketcap()
            if data:
                market_price = data["market_data"]["current_price"][self.settings.currency()]
                market_cap = data["market_data"]["market_cap"][self.settings.currency()]
                market_volume = data["market_data"]["total_volume"][self.settings.currency()]
                price_percentage_24 = data["market_data"]["price_change_percentage_24h"]
                price_percentage_7d = data["market_data"]["price_change_percentage_7d"]
                
                btcz_price = self.units.format_price(market_price)
                self.settings.update_settings("btcz_price", btcz_price)

                self.market_output.control.CoreWebView2.ExecuteScriptAsync(f"setBTCZPrice('{self.settings.symbol()} {btcz_price}');")
                self.market_output.control.CoreWebView2.ExecuteScriptAsync(f"setChange24h('{price_percentage_24} %');")
                self.market_output.control.CoreWebView2.ExecuteScriptAsync(f"setChange7d('{price_percentage_7d} %');")
                self.market_output.control.CoreWebView2.ExecuteScriptAsync(f"setMarketCap('{self.settings.symbol()} {market_cap}');")
                self.market_output.control.CoreWebView2.ExecuteScriptAsync(f"setVolume('{self.settings.symbol()} {market_volume}');")

            await asyncio.sleep(601)


    async def update_marketchart(self):
        self.app.console.event_log(f"✔: Market curve")
        while True:
            data = await self.utils.fetch_marketchart()
            currency = self.settings.currency().upper()
            if not data:
                if not self.market_retrieved:
                    js_data = f'generateData([], "{currency}");'
            else:
                self.market_retrieved = True
                js_data = f'generateData({json.dumps(data)}, "{currency}");'

            self.market_output.control.CoreWebView2.ExecuteScriptAsync(js_data)

            await asyncio.sleep(602)