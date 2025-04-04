
import asyncio
import aiohttp
import zipfile
import py7zr
import qrcode
import winreg as reg
import sys
import urllib

from toga import App
from ..framework import (
    Os, Sys, ProgressStyle, Forms, run_async
)

from .units import Units

GITHUB_API_URL = "https://api.github.com/repos/SpaceZ-Projects/BTCZWallet-win"
RELEASES_URL = "https://github.com/SpaceZ-Projects/BTCZWallet-win/releases"


class Utils():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_path = self.app.paths.app
        self.app_data = self.app.paths.data
        self.app_cache = self.app.paths.cache
        if not Os.Directory.Exists(str(self.app_data)):
            Os.Directory.CreateDirectory(str(self.app_data))
        if not Os.Directory.Exists(str(self.app_cache)):
            Os.Directory.CreateDirectory(str(self.app_cache))

        self.units = Units(self.app)

    
    async def get_repo_info(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GITHUB_API_URL}/tags") as response:
                if response.status == 200:
                    tags = await response.json()
                    latest_tag = tags[0]['name'] if tags else None
                    if latest_tag and latest_tag.startswith("v"):
                        latest_tag = latest_tag[1:]
                    return latest_tag, RELEASES_URL
                else:
                    print(f"Failed to fetch tags: {response.status}")
                    return None, None

    def qr_generate(self, address):  
        qr_filename = f"qr_{address}.png"
        qr_path = Os.Path.Combine(str(self.app_cache), qr_filename)
        if Os.File.Exists(qr_path):
            return qr_path
        
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=7,
            border=1,
        )
        qr.add_data(address)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        with open(qr_path, 'wb') as f:
            qr_img.save(f)
        
        return qr_path
    

    def get_bitcoinz_path(self):
        bitcoinz_path = Os.Path.Combine(
            Sys.Environment.GetFolderPath(Sys.Environment.SpecialFolder.ApplicationData), 'BitcoinZ'
        )
        return bitcoinz_path
    
    def get_zk_path(self):
        zk_params_path = Os.Path.Combine(
            Sys.Environment.GetFolderPath(Sys.Environment.SpecialFolder.ApplicationData), 'ZcashParams'
        )
        return zk_params_path
    
    def get_config_path(self):
        config_file = "bitcoinz.conf"
        bitcoinz_path = self.get_bitcoinz_path()
        config_file_path = Os.Path.Combine(bitcoinz_path, config_file)
        return config_file_path
    
    def windows_screen_center(self, size):
        screen_size = self.app.screens[0].size
        screen_width, screen_height = screen_size
        window_width, window_height = size
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        return (x, y)
    
    def get_bitcoinz_size(self):
        bitcoinz_path = self.get_bitcoinz_path()
        dir_info = Os.DirectoryInfo(bitcoinz_path)
        if not dir_info.Exists:
            print("Directory does not exist.")
            return 0
        total_size = 0
        for file_info in dir_info.GetFiles("*", Os.SearchOption.AllDirectories):
            if file_info.Name.lower().startswith("bootstrap"):
                continue
            total_size += file_info.Length
        total_size_gb = total_size / (1024 ** 2)
        return total_size_gb

    def get_binary_files(self):
        required_files = [
            'bitcoinzd.exe',
            'bitcoinz-cli.exe',
            'bitcoinz-tx.exe'
        ]
        missing_files = []
        for file in required_files:
            file_path = Os.Path.Combine(str(self.app_data), file)
            if not Os.File.Exists(file_path):
                missing_files.append(file)
        return missing_files
    
    def get_zk_params(self):
        zk_params_path = self.get_zk_path()
        if not Os.Directory.Exists(zk_params_path):
            Os.Directory.CreateDirectory(zk_params_path)
        required_files = [
            'sprout-proving.key',
            'sprout-verifying.key',
            'sapling-spend.params',
            'sapling-output.params',
            'sprout-groth16.params'
        ]
        missing_files = []
        for file in required_files:
            file_path = Os.Path.Combine(zk_params_path, file)
            if not Os.File.Exists(file_path):
                missing_files.append(file)
        return missing_files, zk_params_path
    

    def get_miner_path(self, miner):
        miner_folder = miner
        if miner == "MiniZ":
            miner_file = "MiniZ.exe"
            url = "https://github.com/ezzygarmyz/miniZ/releases/download/v2.4e/"
            zip_file = "miniZ_v2.4e_win-x64.zip"
        elif miner == "Gminer":
            miner_file = "miner.exe"
            url = "https://github.com/develsoftware/GMinerRelease/releases/download/3.44/"
            zip_file = "gminer_3_44_windows64.zip"

        miner_dir = Os.Path.Combine(str(self.app_data), miner_folder)
        if not Os.Directory.Exists(miner_dir):
            Os.Directory.CreateDirectory(miner_dir)
        miner_path = Os.Path.Combine(miner_dir, miner_file)
        if Os.File.Exists(miner_path):
            return miner_path, url, zip_file
        return None, url, zip_file
    

    async def fetch_binary_files(self, label, progress_bar):
        file_name = "bitcoinz-c73d5cdb2b70-win64.zip"
        url = "https://github.com/btcz/bitcoinz/releases/download/2.1.0/"
        text = "Downloading binary...%"
        destination = Os.Path.Combine(str(self.app_data), file_name)
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
                            label._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_status_label(label, text, progress)))
                            progress_bar.value = progress
                        self.file_handle.close()
                        self.file_handle = None
                        await session.close()
                        with zipfile.ZipFile(destination, 'r') as zip_ref:
                            zip_ref.extractall(self.app_data)
                        extracted_folder = Os.Path.Combine(str(self.app_data), "bitcoinz-c73d5cdb2b70")
                        bin_folder = Os.Path.Combine(extracted_folder, "bin")
                        for exe_file in ["bitcoinzd.exe", "bitcoinz-cli.exe", "bitcoinz-tx.exe"]:
                            src = Os.Path.Combine(bin_folder, exe_file)
                            dest = Os.Path.Combine(str(self.app_data), exe_file)
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


    async def fetch_params_files(self, missing_files, zk_params_path, label, progress_bar):
        base_url = "https://d.btcz.rocks/"
        total_files = len(missing_files)
        text = "Downloading params...%"
        try:
            async with aiohttp.ClientSession() as session:
                for idx, file_name in enumerate(missing_files):
                    url = base_url + file_name
                    file_path = Os.Path.Combine(zk_params_path, file_name)
                    self.current_download_file = file_path
                    async with session.get(url, timeout=None) as response:
                        if response.status == 200:
                            total_size = int(response.headers.get('content-length', 0))
                            chunk_size = 512
                            downloaded_size = 0
                            self.file_handle = open(file_path, 'wb')
                            async for chunk in response.content.iter_chunked(chunk_size):
                                if not chunk:
                                    break
                                self.file_handle.write(chunk)
                                downloaded_size += len(chunk)
                                overall_progress = int(((idx + downloaded_size / total_size) / total_files) * 100)
                                label._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_status_label(label, text, overall_progress)))
                                progress_bar.value = overall_progress
                            self.file_handle.close()
                            self.file_handle = None
                    self.current_download_file = None
                await session.close()
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def fetch_bootstrap_files(self, label, progress_bar):
        base_url = "https://github.com/btcz/bootstrap/releases/download/2024-09-04/"
        bootstrap_files = [
            'bootstrap.dat.7z.001',
            'bootstrap.dat.7z.002',
            'bootstrap.dat.7z.003',
            'bootstrap.dat.7z.004'
        ]
        total_files = len(bootstrap_files)
        bitcoinz_path = self.get_bitcoinz_path()
        text = "Downloading bootstrap...%"
        try:
            async with aiohttp.ClientSession() as session:
                for idx, file_name in enumerate(bootstrap_files):
                    file_path = Os.Path.Combine(bitcoinz_path, file_name)
                    if Os.File.Exists(file_path):
                        continue
                    url = base_url + file_name
                    self.current_download_file = file_path
                    async with session.get(url, timeout=None) as response:
                        if response.status == 200:
                            total_size = int(response.headers.get('content-length', 0))
                            chunk_size = 512
                            downloaded_size = 0
                            self.file_handle = open(file_path, 'wb')
                            async for chunk in response.content.iter_chunked(chunk_size):
                                if not chunk:
                                    break
                                self.file_handle.write(chunk)
                                downloaded_size += len(chunk)
                                overall_progress = int(((idx + downloaded_size / total_size) / total_files) * 100)
                                label._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_status_label(label, text, overall_progress)))
                                progress_bar.value = overall_progress
                            self.file_handle.close()
                            self.file_handle = None
                    self.current_download_file = None
                await session.close()
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def fetch_miner(self, miner_selection, setup_miner_box, progress_bar, miner_folder, file_name, url):
        destination = Os.Path.Combine(str(self.app_data), file_name)
        miner_dir = Os.Path.Combine(str(self.app_data), miner_folder)
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
                            progress_bar._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_progress_bar(progress_bar, progress)))
                        self.file_handle.close()
                        self.file_handle = None
                        await session.close()
                        run_async(self.extract_miner(miner_selection, setup_miner_box, progress_bar, destination, miner_folder, miner_dir))
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def extract_miner(self, miner_selection, setup_miner_box, progress_bar, destination, miner_folder, miner_dir):
        if miner_folder == "MiniZ":
            miner_name = "miniZ.exe"
        elif miner_folder =="Gminer":
            miner_name = "miner.exe"
        with zipfile.ZipFile(destination, 'r') as zip_ref:
            zip_ref.extractall(miner_dir)
        for file in Os.Directory.GetFiles(miner_dir):
            file_name = Os.Path.GetFileName(file)
            if file_name != miner_name:
                Os.File.Delete(file)
        
        Os.File.Delete(destination)
        miner_selection.enabled = True
        setup_miner_box.remove(
            progress_bar
        )


    async def extract_7z_files(self, label, progress_bar):
        bitcoinz_path = self.get_bitcoinz_path()
        file_paths = [
            Os.Path.Combine(bitcoinz_path, 'bootstrap.dat.7z.001'),
            Os.Path.Combine(bitcoinz_path, 'bootstrap.dat.7z.002'),
            Os.Path.Combine(bitcoinz_path, 'bootstrap.dat.7z.003'),
            Os.Path.Combine(bitcoinz_path, 'bootstrap.dat.7z.004')
        ]
        combined_file = Os.Path.Combine(bitcoinz_path, "combined_bootstrap.7z")
        with open(combined_file, 'wb') as outfile:
                for file_path in file_paths:
                    with open(file_path, 'rb') as infile:
                        while chunk := infile.read(1024):
                            outfile.write(chunk)
        for file_path in file_paths:
            if Os.File.Exists(file_path):
                Os.File.Delete(file_path)
        self.extract_progress_status = True
        try:
            with py7zr.SevenZipFile(combined_file, mode='r') as archive:
                run_async(self.extract_progress(label, progress_bar, bitcoinz_path))
                archive.extractall(path=bitcoinz_path)
                self.extract_progress_status = False
        except Exception as e:
            print(f"Error extracting file: {e}")

        Os.File.Delete(combined_file)

    
    async def extract_progress(self, label, progress_bar, bitcoinz_path):
        style = ProgressStyle.BLOCKS
        progress_bar._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_progress_style(progress_bar, style)))
        total_size = 5495725462
        total_size_gb = total_size / (1024 ** 3)
        while True:
            if not self.extract_progress_status:
                style = ProgressStyle.MARQUEE
                progress_bar._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_progress_style(progress_bar, style)))
                return
            dat_file = Os.Path.Combine(bitcoinz_path, "bootstrap.dat")
            current_size = Os.FileInfo(dat_file).Length
            current_size_gb = current_size / (1024 ** 3)
            progress = int((current_size / total_size) * 100)
            text = f"Extracting... {current_size_gb:.2f} / {total_size_gb:.2f} GB"
            label._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_status_label(label, text, None)))
            progress_bar._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_progress_bar(progress_bar, progress)))
            await asyncio.sleep(3)

    def update_status_label(self, label, text, progress):
        if progress is None:
            label._impl.native.Text = text
        else:
            label._impl.native.Text = f"{text}{progress}"

    def update_progress_bar(self, progress_bar, progress):
        progress_bar.value = progress

    def update_progress_style(self, progress_bar, style):
        progress_bar._impl.native.Style = style


    def create_config_file(self, config_file_path):
        try:
            rpcuser = self.units.generate_random_string(16)
            rpcpassword = self.units.generate_random_string(32)
            with open(config_file_path, 'w') as config_file:
                config_content = f"""# BitcoinZ configuration file
# Add your configuration settings below

rpcuser={rpcuser}
rpcpassword={rpcpassword}
addnode=178.193.205.17:1989
addnode=51.222.50.26:1989
addnode=146.59.69.245:1989
addnode=37.187.76.80:1989
"""
                config_file.write(config_content)
        except Exception as e:
            print(f"Error creating config file: {e}")


    def add_to_startup(self):
        excutable_file = Os.Path.Combine(str(self.app_path.parents[1]), 'BTCZWallet.exe')
        if not Os.File.Exists(excutable_file):
            return None
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_WRITE)
            reg.SetValueEx(registry_key, "BTCZWallet", 0, reg.REG_SZ, excutable_file)
            reg.CloseKey(registry_key)
            return True
        except Exception as e:
            return None

    def remove_from_startup(self):
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_WRITE)
            reg.DeleteValue(registry_key, "BTCZWallet")
            reg.CloseKey(registry_key)
            return True
        except Exception as e:
            return None