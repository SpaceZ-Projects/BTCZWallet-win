
import asyncio
import aiohttp
import zipfile
import tarfile
from datetime import datetime, timezone
import psutil
import hashlib
import hmac
import json
import py7zr
import qrcode
import winreg as reg
from aiohttp.client_exceptions import ClientConnectionError, ServerDisconnectedError, ClientError
from aiohttp_socks import ProxyConnector, ProxyConnectionError, ProxyError
import ipaddress
import ctypes
import io
from PIL import Image, ImageFilter

from toga import App
from ..framework import (
    Os, Sys, ProgressStyle, Forms, run_async, Win32, Drawing
)


class Utils():
    def __init__(self, app:App, settings, units, tr):
        super().__init__()

        self.app = app
        self.app_path = self.app.paths.app
        self.app_data = self.app.paths.data
        self.app_cache = self.app.paths.cache
        self.app_logs = self.app.paths.logs

        self.settings = settings
        self.units = units
        self.tr = tr

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        if not Os.Directory.Exists(str(self.app_data)):
            Os.Directory.CreateDirectory(str(self.app_data))
        if not Os.Directory.Exists(str(self.app_cache)):
            Os.Directory.CreateDirectory(str(self.app_cache))
        if not Os.Directory.Exists(str(self.app_logs)):
            Os.Directory.CreateDirectory(str(self.app_logs))

    
    async def get_repo_info(self, tor_enabled):
        if tor_enabled:
            torrc = self.read_torrc()
            socks_port = torrc.get("SocksPort")
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
        else:
            connector = None
        github_url = "https://api.github.com/repos/SpaceZ-Projects/BTCZWallet-win"
        releases_url = "https://github.com/SpaceZ-Projects/BTCZWallet-win/releases"
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(f"{github_url}/tags", timeout=10) as response:
                    if response.status == 200:
                        tags = await response.json()
                        latest_tag = tags[0]['name'] if tags else None
                        if latest_tag and latest_tag.startswith("v"):
                            latest_tag = latest_tag[1:]
                        return latest_tag, releases_url
                    else:
                        self.app.console.error_log(f"Failed to fetch tags: {response.status}")
                        return None, None
        except ProxyConnectionError:
            self.app.console.error_log("Proxy connection failed")
            return None, None
        except RuntimeError as e:
            self.app.console.error_log(f"RuntimeError caught: {e}")
            return None, None
        except aiohttp.ClientError as e:
            self.app.console.error_log(f"HTTP Error: {e}")
            return None, None
        except Exception as e:
            self.app.console.error_log(f"{e}")
            return None, None


    async def is_tor_alive(self):
        torrc = self.read_torrc()
        if not torrc:
            return None
        socks_port = torrc.get("SocksPort")
        try:
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get('http://check.torproject.org', timeout=10) as response:
                    await response.text()
                    return True
        except ProxyConnectionError:
            self.app.console.error_log("Proxy connection failed")
            return None
        except ClientConnectionError as e:
            self.app.console.warning_log(f"Connection to server failed: {e}")
            return None
        except ServerDisconnectedError as e:
            self.app.console.error_log(f"Server disconnected: {e}")
            return None
        except Exception as e:
            self.app.console.error_log(f"{e}")
            return None
        

    def stop_tor(self):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "tor.exe":
                    proc.kill()
        except Exception as e:
            self.app.console.error_log(f"{e}")
            pass
        

    async def make_request(self, key, secret, url, params = None, return_bytes = None):
        if params is None:
            params = {}
        torrc = self.read_torrc()
        socks_port = torrc.get("SocksPort")
        connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
        timestamp = datetime.now(timezone.utc).isoformat()
        message = f"{timestamp}.{json.dumps(params, separators=(',', ':'), sort_keys=True)}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha512
        ).hexdigest()
        headers = {
            'Authorization': key,
            'X-Timestamp': timestamp,
            'X-Signature': signature
        }
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if return_bytes:
                        data = await response.read()
                    else:
                        data = await response.json()
                    await session.close()
                    return data
        except ProxyConnectionError:
            self.app.console.error_log("Proxy connection failed")
            return None
        except ClientConnectionError as e:
            self.app.console.error_log(f"Client socket errors: {e}")
            return None
        except (ProxyError, ClientError) as e:
            self.app.console.error_log(f"{e}")
            return None
        except Exception as e:
            self.app.console.error_log(f"{e}")
            return None
        

    async def fetch_marketcap(self):
        api = "https://api.coingecko.com/api/v3/coins/bitcoinz"
        tor_enabled = self.settings.tor_network()
        if tor_enabled:
            torrc = self.read_torrc()
            socks_port = torrc.get("SocksPort")
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                headers={'User-Agent': 'Mozilla/5.0'}
                async with session.get(api, headers=headers, timeout=10) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except ProxyConnectionError:
            self.app.console.error_log("Proxy connection failed")
            return None
        except asyncio.TimeoutError:
            self.app.console.error_log(f"Request timed out {api}")
            return None
        except Exception as e:
            self.app.console.error_log(f"{e}")
            return None
        

    def get_onion_hostname(self, service):
        if service == "node":
            tor_service = Os.Path.Combine(str(self.app_data), "tor_service")
            if Os.Directory.Exists(tor_service):
                hostname_file = Os.Path.Combine(tor_service, "hostname")
                with open(hostname_file, 'r') as file:
                    hostname = file.read().strip()
                    return hostname
                
        elif service == "market":
            market_service = Os.Path.Combine(str(self.app_data), "market_service")
            if Os.Directory.Exists(market_service):
                hostname_file = Os.Path.Combine(market_service, "hostname")
                with open(hostname_file, 'r') as file:
                    hostname = file.read().strip()
                    return hostname
                
        elif service == "mobile":
            mobile_service = Os.Path.Combine(str(self.app_data), "mobile_service")
            if Os.Directory.Exists(mobile_service):
                hostname_file = Os.Path.Combine(mobile_service, "hostname")
                with open(hostname_file, 'r') as file:
                    hostname = file.read().strip()
                    return hostname
        return None
    
    def is_ipv6_address(self, address: str):
        try:
            if address.startswith("[") and "]" in address:
                address = address[1:].split("]")[0]
            ipaddress.IPv6Address(address)
            return True
        except ValueError:
            return False
    

    def shorten_address(self, address: str) -> str:
        if not address:
            return "N/A"
        if '.onion' in address:
            return address[:12] + "...onion"
        elif self.is_ipv6_address(address):
            return address[:8] + "...IPv6"
        else:
            return address
        

    def capture_screenshot(self, size, left, top, path):
        try:
            bmp = Drawing.Bitmap(size.Width, size.Height)
            g = Drawing.Graphics.FromImage(bmp)
            g.CopyFromScreen(Drawing.Point(left, top), Drawing.Point(1, 1), bmp.Size)
            stream = Os.MemoryStream()
            bmp.Save(stream, Drawing.Imaging.ImageFormat.Png)
            data = stream.ToArray()
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            shadow_offset = (18, 18)
            shadow = Image.new("RGBA", (img.width + shadow_offset[0]*2, img.height + shadow_offset[1]*2), (0, 0, 0, 0))
            base = Image.new("RGBA", img.size, (0, 0, 0, 210))
            shadow.paste(base, shadow_offset)
            shadow = shadow.filter(ImageFilter.GaussianBlur(11))
            final_img = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
            final_img.alpha_composite(shadow, (0, 0))
            final_img.alpha_composite(img, (shadow_offset[0], shadow_offset[1]))
            final_img.save(path, "PNG")
        finally:
            g.Dispose()
            bmp.Dispose()
            stream.Dispose()


    def record_screen(self, size, left, top):
        bmp = Drawing.Bitmap(size.Width, size.Height)
        g = Drawing.Graphics.FromImage(bmp)
        g.CopyFromScreen(Drawing.Point(left, top), Drawing.Point(1, 1), bmp.Size)
        cursor_pos = Forms.Cursor.Position
        rel_x = cursor_pos.X - (left + 7)
        rel_y = cursor_pos.Y - top

        if 0 <= rel_x < bmp.Width and 0 <= rel_y < bmp.Height:
            Forms.Cursors.Default.Draw(
                g,
                Drawing.Rectangle(
                    rel_x, rel_y,
                    Forms.Cursors.Default.Size.Width,
                    Forms.Cursors.Default.Size.Height
                )
            )
        try:
            stream = Os.MemoryStream()
            bmp.Save(stream, Drawing.Imaging.ImageFormat.Png)
            data = stream.ToArray()
            py_stream = io.BytesIO(data)
            img = Image.open(py_stream).copy()
            return img
        finally:
            g.Dispose()
            bmp.Dispose()
            stream.Dispose()
            

    def qr_generate(self, address, secret = None):
        if secret:
            safe_part = address[:40]
            qr_filename = f"qr_{safe_part}.png"
        else:
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
    

    def get_rpc_config(self):
        config_path = self.get_config_path()
        rpcuser, rpcpassword, rpcport = None, None, None
        if Os.File.Exists(config_path):
            with open(config_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("rpcuser="):
                        rpcuser = line.split("=", 1)[1].strip()
                    elif line.startswith("rpcpassword="):
                        rpcpassword = line.split("=", 1)[1].strip()
                    elif line.startswith("rpcport="):
                        rpcport = line.split("=", 1)[1].strip()
        if not rpcport:
            rpcport = 1979

        return rpcuser, rpcpassword, rpcport

    
    
    def verify_export_dir(self):
        config_file_path = self.get_config_path()
        with open(config_file_path, 'r') as config:
            lines = config.readlines()
            for line in lines:
                if line.startswith("exportdir"):
                    return True
            return None
            
    def update_config(self, path):
        config_file_path = self.get_config_path()
        updated_lines = []
        with open(config_file_path, 'r') as config:
            lines = config.readlines()
        key_found = False
        for line in lines:
            stripped_line = line.strip()
            if "=" in stripped_line:
                current_key, _ = map(str.strip, stripped_line.split('=', 1))
                if current_key == "exportdir":
                    key_found = True
                    if path is not None and path != "":
                        updated_lines.append(f"exportdir={path}\n")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        if not key_found and path is not None and path != "":
            updated_lines.append(f"exportdir={path}\n")
        with open(config_file_path, 'w') as file:
            file.writelines(updated_lines)
    
    def windows_screen_center(self, main, window):
        screen = Forms.Screen.FromControl(main._impl.native)
        left = screen.Bounds.Left + (screen.Bounds.Width - window._impl.native.Width) // 2
        top = screen.Bounds.Top + (screen.Bounds.Height - window._impl.native.Height) // 2

        return left, top
    

    def get_app_theme(self):
        key = Win32.Registry.CurrentUser.OpenSubKey(
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value = key.GetValue("AppsUseLightTheme", 1)
        return "light" if value == 1 else "dark"

    
    def apply_title_bar_mode(self, window, ui_mode:int): 
        try:
            hwnd = window._impl.native.Handle.ToInt32()
            value = ctypes.c_int(ui_mode)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.wintypes.HWND(hwnd),
                ctypes.c_int(20),
                ctypes.byref(value),
                ctypes.sizeof(value)
            )
        except Exception as e:
            print(f"Failed to apply title bar mode: {e}")
    
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
    
    def get_tor_files(self):
        required_files = [
            'tor.exe',
            'geoip',
            'geoip6'
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
        elif miner == "lolMiner":
            miner_file = "lolMiner.exe"
            url = "https://github.com/Lolliedieb/lolMiner-releases/releases/download/1.95/"
            zip_file = "lolMiner_v1.95_Win64.zip"

        miner_dir = Os.Path.Combine(str(self.app_data), miner_folder)
        if not Os.Directory.Exists(miner_dir):
            Os.Directory.CreateDirectory(miner_dir)
        miner_path = Os.Path.Combine(miner_dir, miner_file)
        if Os.File.Exists(miner_path):
            return miner_path, url, zip_file
        return None, url, zip_file
    

    async def fetch_tor_files(self, label, progress_bar):
        file_name = "tor-expert-bundle-windows-x86_64-14.5.6.tar.gz"
        url = "https://archive.torproject.org/tor-package-archive/torbrowser/14.5.6/"
        self.app.console.info_log(f"Downloading tor bundle... {url}")
        destination = Os.Path.Combine(str(self.app_data), file_name)
        text = self.tr.text("download_tor")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url + file_name, timeout=None) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        self.app.console.info_log(f"File size : {self.units.format_bytes(total_size)}")
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
                        self.app.console.info_log(f"Download complete")
                        with tarfile.open(destination, "r:gz") as tar:
                            tar.extractall(path=self.app_data)

                        tor_dir = Os.Path.Combine(str(self.app_data), "tor")
                        tor_exe = Os.Path.Combine(tor_dir, "tor.exe")
                        dest_tor_exe = Os.Path.Combine(str(self.app_data), "tor.exe")
                        if Os.File.Exists(dest_tor_exe):
                            Os.File.Delete(dest_tor_exe)
                        Os.File.Move(tor_exe, dest_tor_exe)

                        data_dir = Os.Path.Combine(str(self.app_data), "data")

                        geoip_file = Os.Path.Combine(data_dir, "geoip")
                        dest_geoip = Os.Path.Combine(str(self.app_data), "geoip")
                        if Os.File.Exists(dest_geoip):
                            Os.File.Delete(dest_geoip)
                        Os.File.Move(geoip_file, dest_geoip)

                        geoip6_file = Os.Path.Combine(data_dir, "geoip6")
                        dest_geoip6 = Os.Path.Combine(str(self.app_data), "geoip6")
                        if Os.File.Exists(dest_geoip6):
                            Os.File.Delete(dest_geoip6)
                        Os.File.Move(geoip6_file, dest_geoip6)

                        docs_dir = Os.Path.Combine(str(self.app_data), "docs")
                        for path in [tor_dir, data_dir, docs_dir]:
                            if Os.Directory.Exists(path):
                                Os.Directory.Delete(path, True)
                        if Os.File.Exists(destination):
                            Os.File.Delete(destination)
        except RuntimeError as e:
            self.app.console.error_log(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            self.app.console.error_log(f"HTTP Error: {e}")
        except Exception as e:
            self.app.console.error_log(f"{e}")

    

    async def fetch_binary_files(self, label, progress_bar, tor_enabled):
        file_name = "bitcoinz-45802c9f29b4-win64.zip"
        url = "https://github.com/btcz/bitcoinz/releases/download/2.1.1/"
        self.app.console.info_log(f"Downloading BitcoinZ... {url}")
        text = self.tr.text("download_binary")
        destination = Os.Path.Combine(str(self.app_data), file_name)
        if tor_enabled:
            torrc = self.read_torrc()
            socks_port = torrc.get("SocksPort")
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url + file_name, timeout=None) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        self.app.console.info_log(f"File size : {self.units.format_bytes(total_size)}")
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
                        self.app.console.info_log(f"Download complete")
                        with zipfile.ZipFile(destination, 'r') as zip_ref:
                            zip_ref.extractall(self.app_data)
                        extracted_folder = Os.Path.Combine(str(self.app_data), "bitcoinz-45802c9f29b4")
                        bin_folder = Os.Path.Combine(extracted_folder, "bin")
                        for exe_file in ["bitcoinzd.exe", "bitcoinz-cli.exe", "bitcoinz-tx.exe"]:
                            src = Os.Path.Combine(bin_folder, exe_file)
                            dest = Os.Path.Combine(str(self.app_data), exe_file)
                            if Os.File.Exists(src):
                                if not Os.File.Exists(dest):
                                    Os.File.Move(src, dest)
                        Os.Directory.Delete(extracted_folder, True)
                        Os.File.Delete(destination)
        except ProxyConnectionError:
            self.app.console.error_log("Proxy connection failed")
        except RuntimeError as e:
            self.app.console.error_log(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            self.app.console.error_log(f"HTTP Error: {e}")
        except Exception as e:
            self.app.console.error_log(f"{e}")


    async def fetch_params_files(self, missing_files, zk_params_path, label, progress_bar, tor_enabled):
        base_url = "https://d.btcz.rocks/"
        self.app.console.info_log(f"Downloading Zk params... {base_url}")
        total_files = len(missing_files)
        text = self.tr.text("download_params")
        if tor_enabled:
            torrc = self.read_torrc()
            socks_port = torrc.get("SocksPort")
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                for idx, file_name in enumerate(missing_files):
                    url = base_url + file_name
                    file_path = Os.Path.Combine(zk_params_path, file_name)
                    self.current_download_file = file_path
                    async with session.get(url, timeout=None) as response:
                        if response.status == 200:
                            total_size = int(response.headers.get('content-length', 0))
                            self.app.console.info_log(f"File name : {file_name} | File size : {self.units.format_bytes(total_size)}")
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
                self.app.console.info_log(f"Download complete")
        except ProxyConnectionError:
            self.app.console.error_log("Proxy connection failed")
        except RuntimeError as e:
            self.app.console.error_log(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            self.app.console.error_log(f"HTTP Error: {e}")
        except Exception as e:
            self.app.console.error_log(f"{e}")


    async def fetch_bootstrap_files(self, label, progress_bar, tor_enabled):
        base_url = "https://github.com/btcz/bootstrap/releases/download/2024-09-04/"
        self.app.console.info_log(f"Downloading BitcoinZ bootstrap... {base_url}")
        bootstrap_files = [
            'bootstrap.dat.7z.001',
            'bootstrap.dat.7z.002',
            'bootstrap.dat.7z.003',
            'bootstrap.dat.7z.004'
        ]
        total_files = len(bootstrap_files)
        bitcoinz_path = self.get_bitcoinz_path()
        text = self.tr.text("download_bootstrap")
        if tor_enabled:
            torrc = self.read_torrc()
            socks_port = torrc.get("SocksPort")
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                for idx, file_name in enumerate(bootstrap_files):
                    file_path = Os.Path.Combine(bitcoinz_path, file_name)
                    if Os.File.Exists(file_path):
                        continue
                    url = base_url + file_name
                    self.current_download_file = file_path
                    async with session.get(url, timeout=None) as response:
                        if response.status == 200:
                            total_size = int(response.headers.get('content-length', 0))
                            self.app.console.info_log(f"File name : {file_name} | File size : {self.units.format_bytes(total_size)}")
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
                self.app.console.info_log(f"Download complete")
        except ProxyConnectionError:
            self.app.console.error_log("Proxy connection failed")
        except RuntimeError as e:
            self.app.console.error_log(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            self.app.console.error_log(f"HTTP Error: {e}")
        except Exception as e:
            self.app.console.error_log(f"{e}")


    async def fetch_miner(self, miner_selection, setup_miner_box, progress_bar, miner_folder, file_name, url, tor_enabled):
        self.app.console.info_log(f"Downloading {miner_folder}... {url}")
        destination = Os.Path.Combine(str(self.app_data), file_name)
        miner_dir = Os.Path.Combine(str(self.app_data), miner_folder)
        if tor_enabled:
            torrc = self.read_torrc()
            socks_port = torrc.get("SocksPort")
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url + file_name, timeout=None) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        self.app.console.info_log(f"File size : {self.units.format_bytes(total_size)}")
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
                        self.app.console.info_log(f"Download complete")
                        if miner_folder == "MiniZ":
                            miner_name = "miniZ.exe"
                        elif miner_folder =="Gminer":
                            miner_name = "miner.exe"
                        elif miner_folder == "lolMiner":
                            miner_name = "lolMiner.exe"

                        with zipfile.ZipFile(destination, 'r') as zip_ref:
                            zip_ref.extractall(miner_dir)

                        if miner_folder == "lolMiner":
                            subdirs = [d for d in Os.Directory.GetDirectories(miner_dir)]
                            if len(subdirs) == 1:
                                subdir = subdirs[0]
                                for file in Os.Directory.GetFiles(subdir):
                                    dest_path = Os.Path.Combine(miner_dir, Os.Path.GetFileName(file))
                                    Os.File.Move(file, dest_path)
                                Os.Directory.Delete(subdir, True)

                        for file in Os.Directory.GetFiles(miner_dir):
                            file_name = Os.Path.GetFileName(file)
                            if file_name != miner_name:
                                if Os.File.Exists(file):
                                    Os.File.Delete(file)

                        if Os.File.Exists(destination):
                            Os.File.Delete(destination)
                            miner_selection.enabled = True
                            setup_miner_box.remove(
                                progress_bar
                            )
        except ProxyConnectionError:
            self.app.console.error_log("Proxy connection failed")
        except RuntimeError as e:
            self.app.console.error_log(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            self.app.console.error_log(f"HTTP Error: {e}")
        except Exception as e:
            self.app.console.error_log(f"{e}")
        


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
            self.app.console.error_log(e)

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
            text = self.tr.text("extract_bootstarp")
            progress_text = f"{text}{current_size_gb:.2f} / {total_size_gb:.2f} GB"
            label._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_status_label(label, progress_text, None)))
            progress_bar._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_progress_bar(progress_bar, progress)))
            await asyncio.sleep(3)

    def update_status_label(self, label, text, progress= None):
        if progress is None:
            label._impl.native.Text = text
        else:
            if self.rtl:
                progress_ar = self.units.arabic_digits(str(progress))
                label._impl.native.Text = f"%{progress_ar}{text}"
            else:
                label._impl.native.Text = f"{text}{progress}%"

    def update_progress_bar(self, progress_bar, progress):
        progress_bar.value = progress

    def update_progress_style(self, progress_bar, style):
        progress_bar._impl.native.Style = style
        progress_bar.value = 0


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

#Send change back to from t address if possible
sendchangeback=1
"""
                config_file.write(config_content)
        except Exception as e:
            self.app.console.error_log(f"{e}")


    def create_torrc(
            self, 
            socks_port=None,
            tor_service=None,
            service_port=None,
            market_service=None,
            market_port=None,
            mobile_service =None,
            mobile_port = None
        ):
        if not socks_port:
            socks_port = "9050"
        geoip = Os.Path.Combine(str(self.app_data), "geoip")
        geoip6 = Os.Path.Combine(str(self.app_data), "geoip6")
        tor_data = Os.Path.Combine(str(self.app_data), "tor_data")
        torrc_content = f""""""
        torrc_content += f"SocksPort {socks_port}\n"
        torrc_content += f"CookieAuthentication 1\n"
        torrc_content += f"GeoIPFile {geoip}\n"
        torrc_content += f"GeoIPv6File {geoip6}\n"
        torrc_content += f"DataDirectory {tor_data}\n"
        if tor_service:
            torrc_content += f"HiddenServiceDir {tor_service}\n"
            torrc_content += f"HiddenServicePort {service_port} 127.0.0.1:{service_port}\n"
        
        if market_service:
            torrc_content += f"HiddenServiceDir {market_service}\n"
            torrc_content += f"HiddenServicePort 80 127.0.0.1:{market_port}\n"
        
        if mobile_service:
            torrc_content += f"HiddenServiceDir {mobile_service}\n"
            torrc_content += f"HiddenServicePort 80 127.0.0.1:{mobile_port}\n"

        torrc_path = Os.Path.Combine(str(self.app_data), "torrc")
        with open(torrc_path, "w") as f:
            f.write(torrc_content)


    def read_torrc(self):
        torrc_path = Os.Path.Combine(str(self.app_data), "torrc")
        if not Os.File.Exists(torrc_path):
            return None
        config = {}
        with open(torrc_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    key, value = parts
                    if key in config:
                        if isinstance(config[key], list):
                            config[key].append(value)
                        else:
                            config[key] = [config[key], value]
                    else:
                        config[key] = value
        return config


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
            self.app.console.error_log(f"{e}")
            return None

    def remove_from_startup(self):
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_WRITE)
            reg.DeleteValue(registry_key, "BTCZWallet")
            reg.CloseKey(registry_key)
            return True
        except Exception as e:
            self.app.console.error_log(f"{e}")
            return None
        

    def restart_app(self):
        excutable_file = Os.Path.Combine(str(self.app_path.parents[1]), 'BTCZWallet.exe')
        if not Os.File.Exists(excutable_file):
            self.app.console.warning_log("Restart is not available in development mode")
            return None
        batch_script = f"""
@echo off
timeout /t 5 /nobreak > NUL
start "" "{excutable_file}"
del "%~f0"
"""
        batch_path = Os.Path.Combine(str(self.app.paths.cache), 'restart_app.bat')
        with open(batch_path, "w") as file:
            file.write(batch_script)

        psi = Sys.Diagnostics.ProcessStartInfo()
        psi.FileName = batch_path
        psi.UseShellExecute = True
        psi.WindowStyle = Sys.Diagnostics.ProcessWindowStyle.Hidden
        
        Sys.Diagnostics.Process.Start(psi)
        return True