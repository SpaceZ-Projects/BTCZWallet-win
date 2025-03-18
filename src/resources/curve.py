
import aiohttp
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from toga import App
from ..framework import Os

from .units import Units

COINGECKO_API = "https://api.coingecko.com/api/v3/coins/bitcoinz/market_chart"

class Curve():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_cache = self.app.paths.cache

        self.units = Units()


    async def fetch_marketchart(self):
        params = {
            'vs_currency': 'usd',
            'days': '1',
        }
        try:
            async with aiohttp.ClientSession() as session:
                headers={'User-Agent': 'Mozilla/5.0'}
                async with session.get(COINGECKO_API, params=params, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    prices = data.get('prices', [])
                    return prices
        except Exception as e:
            print(f"Error occurred during fetch: {e}")
            return None

    def create_curve(self, data):
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['formatted_price'] = df['price'].apply(lambda x: self.units.format_price(x))
        width, height = 2400, 600
        img = Image.new("RGB", (width, height), color="#1e2124")
        draw = ImageDraw.Draw(img)
        margin_left = 120
        margin_top = 50
        margin_bottom = 50
        margin_right = 50
        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom
        min_price = df['price'].min()
        max_price = df['price'].max()
        min_timestamp = df['timestamp'].min()
        max_timestamp = df['timestamp'].max()
        def scale_x(timestamp):
            return margin_left + (timestamp - min_timestamp) / (max_timestamp - min_timestamp) * plot_width
        def scale_y(price):
            return margin_top + (max_price - price) / (max_price - min_price) * plot_height
        draw.line([(margin_left, margin_top), (margin_left, height - margin_bottom)], fill="white", width=2)
        draw.line([(margin_left, height - margin_bottom), (width - margin_right, height - margin_bottom)], fill="white", width=2)
        for i in range(1, len(df)):
            x1 = scale_x(df['timestamp'].iloc[i-1])
            y1 = scale_y(df['price'].iloc[i-1])
            x2 = scale_x(df['timestamp'].iloc[i])
            y2 = scale_y(df['price'].iloc[i])
            draw.line([(x1, y1), (x2, y2)], fill="green", width=3)
        font = ImageFont.load_default(size=18)
        for i in range(0, len(df), len(df) // 10):
            timestamp = df['timestamp'].iloc[i]
            x = scale_x(timestamp)
            y = height - margin_bottom + 10
            draw.text((x, y), timestamp.strftime('%H:%M:%S'), font=font, fill="white")
        price_interval = (max_price - min_price) / 7
        for i in range(0, 8):
            price = min_price + i * price_interval
            y = scale_y(price)
            draw.text((margin_left - 100, y - 10), f"{self.units.format_price(price)}", font=font, fill="white")
        timestamp_str = df['timestamp'].iloc[0].strftime('%Y%m%d_%H%M%S')
        curve_image_path = Os.Path.Combine(str(self.app_cache), f'curve_{timestamp_str}.png')
        img.save(curve_image_path)

        return curve_image_path