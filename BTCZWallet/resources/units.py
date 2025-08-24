
import string
import secrets
from decimal import Decimal
from datetime import datetime, timedelta, timezone
import json
import base64

from toga import App

INITIAL_REWARD = 12500
HALVING_INTERVAL = 840000


class Units():
    def __init__(self, app:App, commands):
        super().__init__()

        self.app = app
        self.commands = commands

    def generate_id(self, length=32):
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        random_bytes = secrets.token_bytes(length)
        address_id = ''.join(alphabet[b % 62] for b in random_bytes)
        return address_id
    

    def generate_secret_key(self, length=256):
        key_bytes = secrets.token_bytes(length)
        secret_key = base64.urlsafe_b64encode(key_bytes).decode('utf-8')
        return secret_key
    

    def generate_random_string(self, length=16):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))
    

    def format_balance(self, value):
        value = Decimal(value)
        formatted_value = f"{value:.8f}"
        integer_part, decimal_part = formatted_value.split('.')
        if len(integer_part) > 4:
            digits_to_remove = len(integer_part) - 4
            formatted_decimal = decimal_part[:-digits_to_remove]
        else:
            formatted_decimal = decimal_part
        formatted_balance = f"{integer_part}.{formatted_decimal}"
        return formatted_balance
    

    def format_price(self, price):
        price = Decimal(price)

        if price > Decimal('0.00000001') and price < Decimal('0.0000001'):
            return f"{price:.10f}"
        elif price > Decimal('0.0000001') and price < Decimal('0.000001'):
            return f"{price:.9f}"
        elif price > Decimal('0.000001') and price < Decimal('0.00001'):
            return f"{price:.8f}"
        elif price > Decimal('0.00001') and price < Decimal('0.0001'):
            return f"{price:.7f}"
        elif price > Decimal('0.0001') and price < Decimal('0.001'):
            return f"{price:.6f}"
        elif price > Decimal('0.001') and price < Decimal('0.01'):
            return f"{price:.5f}"
        elif price > Decimal('0.01') and price < Decimal('0.1'):
            return f"{price:.4f}"
        elif price > Decimal('0.1') and price < Decimal('1'):
            return f"{price:.3f}"
        elif price > Decimal('1') and price < Decimal('10'):
            return f"{price:.2f}"
        elif price > Decimal('10') and price < Decimal('100'):
            return f"{price:.1f}"
        else:
            return f"{price:.0f}"
        

    def calculate_circulating(self, current_block):
        halvings = current_block // HALVING_INTERVAL
        total_supply = 0
        for i in range(halvings + 1):
            if i == halvings:
                blocks_in_period = current_block - i * HALVING_INTERVAL
            else:
                blocks_in_period = HALVING_INTERVAL
            total_supply += blocks_in_period * (INITIAL_REWARD / (2 ** i))
        return total_supply
    
    
    def remaining_blocks_until_halving(self, current_block):
        next_halving_block = (current_block // HALVING_INTERVAL + 1) * HALVING_INTERVAL
        remaining_blocks = next_halving_block - current_block
        return remaining_blocks
    

    def remaining_days_until_halving(self, current_block, block_time_minutes=2.5):
        next_halving_block = (current_block // HALVING_INTERVAL + 1) * HALVING_INTERVAL
        remaining_blocks = next_halving_block - current_block
        remaining_time_minutes = remaining_blocks * block_time_minutes
        remaining_time_delta = timedelta(minutes=remaining_time_minutes)
        remaining_days = remaining_time_delta.days
        return remaining_days
    
    
    def remaining_blocks_until_deprecation(self, deprecation, current_block):
        remaining_blocks = max(deprecation - current_block, 0)
        return remaining_blocks
    

    def remaining_days_until_deprecation(self, deprecation, current_block, block_time_minutes=2.5):
        remaining_blocks = max(deprecation - current_block, 0)
        remaining_minutes = remaining_blocks * block_time_minutes
        remaining_time = timedelta(minutes=remaining_minutes)
        return remaining_time.days
    
    
    async def estimated_earn(self, period, hashrate):
        blockchaininfo, _ = await self.commands.getBlockchainInfo()
        if blockchaininfo is not None:
            if isinstance(blockchaininfo, str):
                info = json.loads(blockchaininfo)
            if info is not None:
                blocks = info.get('blocks')
                difficulty = info.get('difficulty')
        networksol, _ = await self.commands.getNetworkSolps()
        if networksol is not None:
            if isinstance(networksol, str):
                info = json.loads(networksol)
            if info is not None:
                netsol = info
                net_hashrate = self.solution_to_hash(netsol)

            period_seconds = period * 3600
            block_time_seconds = difficulty * 2**32 / net_hashrate
                
            user_block_fraction = hashrate / net_hashrate
            estimated_blocks = period_seconds / block_time_seconds * user_block_fraction
                
            reward = INITIAL_REWARD / 2 ** (blocks // HALVING_INTERVAL)
            estimated_earnings = estimated_blocks * reward
            return estimated_earnings

    
    def hash_to_solutions(self, hashrate):
        mh_s = hashrate / 500_000
        return mh_s
    
    def solution_to_hash(self, solutions):
        mh_s = solutions * 500_000
        return mh_s
    
    def format_bytes(self, bytes_size):
        if bytes_size == 0:
            return "0 Bytes"
        units = ["Bit", "KB", "MB", "GB"]
        i = 0
        size = bytes_size
        while size >= 1024 and i < len(units) - 1:
            size /= 1024
            i += 1

        return f"{size:.2f} {units[i]}"
    

    def create_timer(self, value, countdown = None):
        now = datetime.now(timezone.utc)
        if isinstance(value, (int, float)):
            duration = timedelta(seconds=value)
        elif isinstance(value, timedelta):
            duration = value
        elif isinstance(value, datetime):
            if countdown:
                duration = value - now
            else:
                duration = now - value

        if duration.total_seconds() < 0:
            duration = timedelta(seconds=0)
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days > 0:
            timer = f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            timer = f"{hours}h {minutes}m"
        elif minutes > 0:
            timer = f"{minutes}m {seconds}s" if countdown else f"{minutes}m"
        else:
            timer = f"{seconds}s" if countdown else "0m"

        return timer
    

    def arabic_digits(self, value):
        latin_to_arabic = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
        return value.translate(latin_to_arabic)