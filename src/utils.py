
import aiohttp
import zipfile
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

    def get_binary_files(self):
        required_files = [
            'bitcoinzd.exe',
            'bitcoinz-cli.exe',
            'bitcoinz-tx.exe'
        ]
        missing_files = []
        for file in required_files:
            file_path = Os.Path.Combine(self.app_data, file)
            if not Os.File.Exists(file_path):
                missing_files.append(file)
        return missing_files


    async def fetch_binary_files(self, label, progress_bar):
        file_name = "bitcoinz-c73d5cdb2b70-win64.zip"
        url = "https://github.com/btcz/bitcoinz/releases/download/2.1.0/"
        destination = Os.Path.Combine(self.app_data, file_name)
        self.current_download_file = destination
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url + file_name, timeout=None) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        chunk_size = 512
                        downloaded_size = 0
                        self.file_handle = open(destination, 'wb')
                        async for chunk in response.content.iter_chunked(chunk_size):
                            if not chunk:
                                break
                            self.file_handle.write(chunk)
                            downloaded_size += len(chunk)
                            progress = int(downloaded_size / total_size * 100)
                            label.text = f"Downloading binary...%{progress}"
                            progress_bar.value = progress
                        self.file_handle.close()
                        self.file_handle = None
                        await session.close()
                        with zipfile.ZipFile(destination, 'r') as zip_ref:
                            zip_ref.extractall(self.app_data)
                        extracted_folder = Os.Path.Combine(self.app_data, "bitcoinz-c73d5cdb2b70")
                        bin_folder = Os.Path.Combine(extracted_folder, "bin")
                        for exe_file in ["bitcoinzd.exe", "bitcoinz-cli.exe", "bitcoinz-tx.exe"]:
                            src = Os.Path.Combine(bin_folder, exe_file)
                            dest = Os.Path.Combine(self.app_data, exe_file)
                            if Os.File.Exists(src):
                                Os.File.Move(src, dest)
                        Os.Directory.Delete(extracted_folder, True)
                        Os.File.Delete(destination)
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")