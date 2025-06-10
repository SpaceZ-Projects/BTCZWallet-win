
import asyncio
import subprocess
import json
from datetime import datetime
import re

from toga import (
    App, Box, Label, ProgressBar, Window
)
from ..framework import (
    ProgressStyle, Os, Forms, run_async, ToolTip, CustomFont
)
from toga.colors import rgb, WHITE, GRAY
from toga.style.pack import Pack
from toga.constants import CENTER, BOLD, COLUMN, ROW, BOTTOM, LEFT, RIGHT

from .utils import Utils
from .client import Client
from .menu import Menu
from .network import TorConfig
from .units import Units
from .settings import Settings
from ..translations import Translations


class BTCZSetup(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(40,43,48),
                flex = 1.5,
                padding = 5
            )
        )

        self.app = app
        self.main = main
        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.commands = Client(self.app)
        self.settings = Settings(self.app)
        self.tr = Translations(self.settings)
        self.tooltip = ToolTip()
        self.app_data = self.app.paths.data

        self.monda_font = CustomFont()

        self.node_status = None
        self.blockchaine_index = None
        self.tor_enabled = None
        self.tor_config = None

        self.status_label = Label(
            text=self.tr.text("check_network"),
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                alignment = CENTER,
                padding_top = 5,
                flex = 1
            )
        )
        self.status_label._impl.native.Font = self.monda_font.get(10)

        self.status_box = Box(
            style=Pack(
                direction=ROW,
                flex = 7,
                background_color = rgb(40,43,48)
            )
        )
        self.progress_bar = ProgressBar(
            style=Pack(height= 12, flex = 1),
            max=100
        )
        self.progress_box = Box(
            style=Pack(
                direction=ROW,
                flex = 3,
                alignment = BOTTOM,
                background_color = rgb(40,43,48)
            )
        )
        self.status_box.add(self.status_label)
        self.progress_box.add(self.progress_bar)
        self.add(self.status_box, self.progress_box)
        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE
        self.app.add_background_task(self.check_network)


    def update_info_box(self):
        self.progress_bar._impl.native.Style = ProgressStyle.BLOCKS
        self.status_box.remove(self.status_label)
        self.status_box.style.direction = COLUMN
        self.box1 = Box(
            style=Pack(
                direction = ROW,
                flex=1,
                background_color = rgb(40,43,48)
            )
        )
        self.box2 = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                background_color = rgb(40,43,48)
            )
        )
        self.blocks_txt = Label(
            text=self.tr.text("blocks_txt"),
            style=Pack(
                text_align = LEFT,
                background_color = rgb(40,43,48),
                color = GRAY,
                font_weight = BOLD,
                padding_top = 3
            )
        )
        self.blocks_value = Label(
            text="",
            style=Pack(
                text_align = LEFT,
                background_color = rgb(40,43,48),
                color = WHITE,
                font_weight = BOLD,
                padding_top = 3
            )
        )
        self.mediantime_text = Label(
            text=self.tr.text("mediantime_text"),
            style=Pack(
                text_align = LEFT,
                background_color = rgb(40,43,48),
                color = GRAY,
                font_weight = BOLD
            )
        )
        self.mediantime_value = Label(
            text="",
            style=Pack(
                text_align = LEFT,
                background_color = rgb(40,43,48),
                color = WHITE,
                font_weight = BOLD
            )
        )
        self.sync_txt = Label(
            text=self.tr.text("sync_txt"),
            style=Pack(
                text_align = RIGHT,
                flex = 1,
                background_color = rgb(40,43,48),
                color = GRAY,
                font_weight = BOLD
            )
        )
        self.sync_value = Label(
            text="",
            style=Pack(
                text_align = RIGHT,
                background_color = rgb(40,43,48),
                color = WHITE,
                font_weight = BOLD
            )
        )
        self.index_size_txt = Label(
            text=self.tr.text("index_size_txt"),
            style=Pack(
                text_align = RIGHT,
                flex = 1,
                background_color = rgb(40,43,48),
                color=GRAY,
                font_weight = BOLD,
                padding_top = 3
            )
        )
        self.index_size_value = Label(
            text="",
            style=Pack(
                text_align = RIGHT,
                background_color = rgb(40,43,48),
                color = WHITE,
                font_weight = BOLD,
                padding_top = 3
            )
        )
        self.status_box._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_status_box()))
        self.box1._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_box1()))
        self.box2._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_box2()))

    def update_status_box(self):
        self.status_box.add(
            self.box1,
            self.box2
        )

    def update_box1(self):
        self.box1.add(
            self.blocks_txt,
            self.blocks_value,
            self.index_size_txt,
            self.index_size_value
        )

    def update_box2(self):
        self.box2.add(
            self.mediantime_text,
            self.mediantime_value,
            self.sync_txt,
            self.sync_value
        )

    
    async def check_network(self, widget):
        async def on_result(widget, result):
            if result is True:
                self.tor_config = TorConfig(startup=self.main)
                self.tor_config._impl.native.Show(self.main._impl.native)
            if result is False:
                self.settings.update_settings("tor_network", False)
                if self.node_status:
                    await self.open_main_menu()
                else:
                    await self.check_binary_files()
            
        await asyncio.sleep(1)
        self.node_status = await self.is_bitcoinz_running()
        self.tor_enabled = self.settings.tor_network()
        if self.tor_enabled is None:
            self.main.network_status.style.color = GRAY
            self.main.network_status.text = self.tr.text("tor_disabled")
            self.main.question_dialog(
                title=self.tr.title("checknetwork_dialog"),
                message=self.tr.message("checknetwork_dialog"),
                on_result=on_result
            )
        else:
            if self.tor_enabled is True:
                self.main.tor_icon.image = "images/tor_on.png"
                self.main.network_status.style.color = rgb(114,137,218)
                self.main.network_status.text = self.tr.text("tor_enbaled")
                tor_running = await self.utils.is_tor_alive()
                await asyncio.sleep(1)
                if self.node_status and tor_running:
                    await self.open_main_menu()
                else:
                    await self.check_tor_files()
            elif self.tor_enabled is False:
                self.main.network_status.style.color = GRAY
                self.main.network_status.text = self.tr.text("tor_disabled")
                await asyncio.sleep(1)
                if self.node_status:
                    await self.open_main_menu()
                else:
                    await self.check_binary_files()


    async def is_bitcoinz_running(self):
        result,_ = await self.commands.getInfo()
        if result:
            return True
        return None
            

    async def check_tor_files(self):
        self.status_label.text = self.tr.text("checktor_files")
        await asyncio.sleep(1)
        missing_files = self.utils.get_tor_files()
        if missing_files:
            self.status_label.text = self.tr.text("download_tor")
            self.progress_bar._impl.native.Style = ProgressStyle.BLOCKS
            await self.utils.fetch_tor_files(
                self.status_label,
                self.progress_bar
            )
        self.app.add_background_task(self.execute_tor)


    async def execute_tor(self, widget):
        async def on_result(widget, result):
            if result is True:
                self.tor_config = TorConfig(startup=self.main)
                self.tor_config._impl.native.Show(self.main._impl.native)
            if result is False:
                self.settings.update_settings("tor_network", False)
                if self.node_status:
                    await self.open_main_menu()
                else:
                    await self.check_binary_files()

        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE
        tor_exe = Os.Path.Combine(str(self.app_data), "tor.exe")
        torrc_path = Os.Path.Combine(str(self.app_data), "torrc")
        if not Os.File.Exists(torrc_path):
            self.main.question_dialog(
                title=self.tr.title("missingtorrc_dialog"),
                message=self.tr.message("missingtorrc_dialog"),
                on_result=on_result
            )
            return
        try:
            tor_running = await self.utils.is_tor_alive()
            if not tor_running:
                self.status_label.text = self.tr.text("execute_tor")
                await asyncio.sleep(1)
                command = [tor_exe, '-f', torrc_path]
                self.tor_process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.status_label.text = self.tr.text("initialize_tor")
                await asyncio.sleep(1)
                try:
                    result = await self.wait_tor_bootstrap()
                    if result:
                        tor_running = await self.utils.is_tor_alive()
                        if tor_running:
                            self.status_label.text = self.tr.text("tor_success")
                            await asyncio.sleep(1)
                            await self.check_binary_files()
                        else:
                            self.status_label.text = self.tr.text("tor_failed")
                except asyncio.TimeoutError:
                    self.status_label.text = self.tr.text("tor_timeout")
            else:
                await self.check_binary_files()

        except Exception as e:
            self.status_label.text = self.tr.text("tor_failed")


    async def wait_tor_bootstrap(self):
        self.progress_bar._impl.native.Style = ProgressStyle.BLOCKS
        self.progress_bar.value = 0
        percentage_pattern = re.compile(r'Bootstrapped (\d+)%')
        while True:
            line = await self.tor_process.stdout.readline()
            if not line:
                break
            decoded = line.decode().strip()
            match = percentage_pattern.search(decoded)
            if match:
                percent = int(match.group(1))
                text = self.tr.text("tor_bootstrap")
                self.status_label.text = f"{text}{percent}%"
                self.progress_bar.value = percent
                if percent == 100:
                    return True


    async def check_binary_files(self):
        self.status_label.text = self.tr.text("checkbinary_files")
        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE
        await asyncio.sleep(1)
        missing_files = self.utils.get_binary_files()
        if missing_files:
            self.status_label.text = self.tr.text("download_binary")
            self.progress_bar._impl.native.Style = ProgressStyle.BLOCKS
            self.progress_bar.value = 0
            await self.utils.fetch_binary_files(
                self.status_label,
                self.progress_bar,
                self.tor_enabled
            )
        await self.check_params_files()


    async def check_params_files(self):
        self.status_label.text = self.tr.text("checkparams_files")
        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE
        await asyncio.sleep(1)
        missing_files, zk_params_path = self.utils.get_zk_params()
        if missing_files:
            self.status_label.text = self.tr.text("download_params")
            self.progress_bar._impl.native.Style = ProgressStyle.BLOCKS
            self.progress_bar.value = 0
            await self.utils.fetch_params_files(
                missing_files, zk_params_path,
                self.status_label, self.progress_bar,
                self.tor_enabled
            )
        await self.check_config_file()


    async def check_config_file(self):
        self.status_label.text = self.tr.text("checkconf_file")
        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE
        await asyncio.sleep(1)
        bitcoinz_path = self.utils.get_bitcoinz_path()
        config_file_path = self.utils.get_config_path()
        if not Os.Directory.Exists(bitcoinz_path) or not Os.Directory.GetFiles(bitcoinz_path):
            self.blockchaine_index = False
            Os.Directory.CreateDirectory(bitcoinz_path)
        else:
            self.blockchaine_index = True
        if not Os.File.Exists(config_file_path):
            self.status_label.text = self.tr.text("createconf_file")
            self.utils.create_config_file(config_file_path)
            await asyncio.sleep(1)
        await self.check_bockchaine_index()
        
    
    async def check_bockchaine_index(self):
        if self.blockchaine_index:
            self.app.add_background_task(self.execute_bitcoinz_node)
        else:
            self.main.question_dialog(
                title=self.tr.title("bootstarp_dialog"),
                message=self.tr.message("bootstarp_dialog"),
                on_result=self.download_bootstrap_dialog
            )

    def download_bootstrap_dialog(self, widget, result):
        if result is True:
            self.app.add_background_task(self.download_bitcoinz_bootstrap)
        elif result is False:
            self.app.add_background_task(self.execute_bitcoinz_node)


    async def download_bitcoinz_bootstrap(self, widget):
        self.status_label.text = self.tr.text("download_bootstrap")
        self.progress_bar._impl.native.Style = ProgressStyle.BLOCKS
        self.progress_bar.value = 0
        await self.utils.fetch_bootstrap_files(
            self.status_label,
            self.progress_bar,
            self.tor_enabled
        )
        run_async(self.extract_bootstrap_file())


    async def extract_bootstrap_file(self):
        self.status_label.text = self.tr.text("extract_bootstarp")
        style = ProgressStyle.MARQUEE
        self.progress_bar._impl.native.Invoke(Forms.MethodInvoker(lambda:self.utils.update_progress_style(self.progress_bar, style)))
        await self.utils.extract_7z_files(
            self.status_label,
            self.progress_bar
        )
        self.app.add_background_task(self.execute_bitcoinz_node)


    async def execute_bitcoinz_node(self, widget):
        self.status_label.text = self.tr.text("start_node")
        bitcoinzd = "bitcoinzd.exe"
        node_file = Os.Path.Combine(str(self.app_data), bitcoinzd)
        command = [node_file]
        if self.settings.tor_network():
            torrc = self.utils.read_torrc()
            socks_port = torrc.get("SocksPort")
            tor_service = torrc.get("HiddenServiceDir", "")
            service_port = torrc.get("HiddenServicePort", "")
            command += [f'-proxy=127.0.0.1:{socks_port}']
            if self.settings.only_onion():
                command += ['-onlynet=onion']
            if tor_service and service_port:
                command += ['-listen=1', '-discover=1']
        try:
            self.process = await asyncio.create_subprocess_exec(
                *command,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            await self.waiting_node_status()
        except Exception as e:
            print(e)
        finally:
            if self.process:
                await self.process.wait()
                self.process = None
                

    async def waiting_node_status(self):
        await asyncio.sleep(1)
        result, error_message = await self.commands.getInfo()
        if result:
            self.node_status = True
            await self.check_sync_progress()
            return
        else:
            while True:
                result, error_message = await self.commands.getInfo()
                if result and error_message is None:
                    self.node_status = True
                    await self.check_sync_progress()
                    return
                elif error_message and result is None:
                    if error_message == "Loading block index...":
                        message = self.tr.text("loading_blocks")
                    elif error_message == "Activating best chain...":
                        message = self.tr.text("activebest_chain")
                    elif error_message == "Rewinding blocks if needed...":
                        message = self.tr.text("rewind_blocks")
                    elif error_message == "Loading wallet...":
                        self.tr.text("loading_wallet")
                    elif error_message == "Rescanning...":
                        self.tr.text("rescan_wallet")
                    else:
                        message = error_message
                    self.status_label.text = message
                elif error_message is None and result is None:
                    self.app.add_background_task(self.execute_bitcoinz_node)
                    return
                await asyncio.sleep(3)


    async def check_sync_progress(self):
        tooltip_text = f"Seeds :"
        await asyncio.sleep(1)
        blockchaininfo, _ = await self.commands.getBlockchainInfo()
        if isinstance(blockchaininfo, str):
            info = json.loads(blockchaininfo)
        if info is not None:
            sync = info.get('verificationprogress')
            sync_percentage = sync * 100
            if sync_percentage <= 99.95:
                self.update_info_box()
                while True:
                    blockchaininfo, _ = await self.commands.getBlockchainInfo()
                    if blockchaininfo:
                        info = json.loads(blockchaininfo)
                    else:
                        self.node_status = False
                        self.app.exit()
                        return
                    if info:
                        blocks = info.get('blocks')
                        sync = info.get('verificationprogress')
                        mediantime = info.get('mediantime')
                    else:
                        blocks = sync = mediantime = "N/A"
                    if isinstance(mediantime, int):
                        mediantime_date = datetime.fromtimestamp(mediantime).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        mediantime_date = "N/A"

                    peerinfo, _ = await self.commands.getPeerinfo()
                    if peerinfo:
                        peerinfo = json.loads(peerinfo)
                        for node in peerinfo:
                            address = node.get('addr')
                            bytesrecv = node.get('bytesrecv')
                            tooltip_text += f"\n{address} - {self.units.format_bytes(bytesrecv)}"
                            
                    bitcoinz_size = self.utils.get_bitcoinz_size()
                    sync_percentage = sync * 100
                    self.blocks_value.text = f"{blocks}"
                    self.mediantime_value.text = mediantime_date
                    self.index_size_value.text = f"{int(bitcoinz_size)} MB"
                    self.sync_value.text = f"%{float(sync_percentage):.2f}"
                    self.progress_bar.value = int(sync_percentage)
                    self.tooltip.insert(self.progress_bar._impl.native, tooltip_text)
                    tooltip_text = f"Seeds :"
                    if sync_percentage > 99.95:
                        await self.open_main_menu()
                        return
                    await asyncio.sleep(2)
            elif sync_percentage > 99.95:
                await self.open_main_menu()


    async def open_main_menu(self):
        self.main_menu = Menu(self.tor_enabled)
        self.main_menu._impl.native.TopMost = True
        self.main_menu._impl.native.Shown += self.on_show
        self.main.hide()
        await asyncio.sleep(1)
        self.main_menu.show()
        self.main_menu.notify.show()

    
    def on_show(self, sender, event):
        self.main_menu._impl.native.TopMost = False
        self.main_menu._impl.native.Activate()