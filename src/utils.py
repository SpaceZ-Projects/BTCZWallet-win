
from framework import Os, App

class Utils():
    def __init__(self):
        super().__init__()

        self.app = App()
        self.app_path = self.app.app_path
        self.app_data = self.app.app_data

    def get_icon(self):
        icon_path = Os.Path.Combine(self.app_path, "images/BitcoinZ.ico")
        return icon_path
    
    def get_lock_file(self):
        lock_file = Os.Path.Combine(self.app_data, ".lock")
        return lock_file
    
    def is_already_running(self):
        lock_file = self.get_lock_file()
        if Os.File.Exists(lock_file):
            try:
                Os.File.Delete(lock_file)
            except Os.IOException:
                return True
        return False

    def create_lock_file(self):
        lock_file = self.get_lock_file()
        try:
            self.lock_file_stream = Os.FileStream(
                lock_file,
                Os.FileMode.CreateNew,
                Os.FileAccess.ReadWrite,
                Os.FileShare(0)
            )
        except Os.IOException:
            return False
        return True

    def remove_lock_file(self):
        lock_file = self.get_lock_file()
        if self.lock_file_stream:
            self.lock_file_stream.Close()
            self.lock_file_stream = None
        if Os.File.Exists(lock_file):
            Os.File.Delete(lock_file)