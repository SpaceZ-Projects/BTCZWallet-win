
from toga import App
from ..framework import Os


class Storage():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data


    def is_exists(self):
        data_file = 'messages.db'
        data_path = Os.Path.Combine(str(self.app_data), data_file)
        if not Os.File.Exists(data_path):
            return False
        return True