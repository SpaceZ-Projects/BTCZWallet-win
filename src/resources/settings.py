
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


    def update_settings(self, setting_key, setting_value):
        with open(self.settings_path, 'r') as f:
                settings = json.load(f)
        settings[setting_key] = setting_value
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f, indent=4)


    def notification(self):
         with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'notifications' not in settings:
                return True
            else:
                return settings['notifications']
            
    
    def startup(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'startup' not in settings:
                return False
            else:
                return settings['startup']
            

    def currency(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'currency' not in settings:
                return "usd"
            else:
                return settings['currency']
            
    def symbol(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'symbol' not in settings:
                return "$"
            else:
                return settings['symbol']