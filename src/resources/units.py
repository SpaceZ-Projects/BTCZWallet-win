
import string
import secrets
from decimal import Decimal
from datetime import timedelta

INITIAL_REWARD = 12500
HALVING_INTERVAL = 840000


class Units():
    def __init__(self):
        super().__init__()

    def generate_id(self, length=32):
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        random_bytes = secrets.token_bytes(length)
        address_id = ''.join(alphabet[b % 62] for b in random_bytes)
        return address_id
    

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
    
    def hash_to_solutions(self, hashrate):
        mh_s = hashrate / 500_000
        return mh_s