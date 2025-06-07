
import json

from toga import App
from ..framework import Os


class Settings():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_config = self.app.paths.config

        if not Os.Directory.Exists(str(self.app_config)):
            Os.Directory.CreateDirectory(str(self.app_config))

        self.settings_path = Os.Path.Combine(str(self.app_config), 'settings.json')
        if not Os.File.Exists(self.settings_path):
            with open(self.settings_path, 'w') as file:
                json.dump({}, file)

        
        self.miningoptions_path = Os.Path.Combine(str(self.app_config), 'mining.json')
        if not Os.File.Exists(self.miningoptions_path):
            with open(self.miningoptions_path, 'w') as file:
                json.dump({}, file)


    def update_settings(self, setting_key, setting_value):
        with open(self.settings_path, 'r') as f:
                settings = json.load(f)
        settings[setting_key] = setting_value
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f, indent=4)


    def notification_txs(self):
         with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'notifications_txs' not in settings:
                return True
            else:
                return settings['notifications_txs']
            
    def notification_messages(self):
         with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'notifications_messages' not in settings:
                return True
            else:
                return settings['notifications_messages']
            
    
    def startup(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'startup' not in settings:
                return False
            else:
                return settings['startup']
            

    def price(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'btcz_price' not in settings:
                return None
            else:
                return settings['btcz_price']
            

    def currency(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'currency' not in settings:
                return "usd"
            else:
                return settings['currency']
            
    def opacity(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'opacity' not in settings:
                return None
            else:
                return settings['opacity']
            
            
    def symbol(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'symbol' not in settings:
                return "$"
            else:
                return settings['symbol']
            
            
    def minimize_to_tray(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'minimize' not in settings:
                return False
            else:
                return settings['minimize']
            

    def tor_network(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'tor_network' not in settings:
                return None
            else:
                return settings['tor_network']
            

    def only_onion(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'only_onion' not in settings:
                return None
            else:
                return settings['only_onion']
            

    def save_mining_options(self, miner, address, pool_server, pool_region, ssl, worker):
        options = {
            "miner": miner,
            "address": address,
            "pool_server": pool_server,
            "pool_region": pool_region,
            "ssl": ssl,
            "worker": worker
        }
        with open(self.miningoptions_path, 'w') as f:
            json.dump(options, f, indent=4)

    
    def load_mining_options(self):
        with open(self.miningoptions_path, 'r') as f:
            data = json.load(f)
        if data:
            return (
                data.get("miner"),
                data.get("address"),
                data.get("pool_server"),
                data.get("pool_region"),
                data.get("ssl"),
                data.get("worker")
            )
        return None, None, None, None, None, None