
import asyncio
import subprocess
import json
from datetime import datetime
import re

from toga import (
    App, Box, Label, ProgressBar, Window
)
from ..framework import (
    ProgressStyle, Os, Forms, run_async, ToolTip,
    RightToLeft
)
from toga.colors import rgb, WHITE, GRAY
from toga.style.pack import Pack
from toga.constants import CENTER, COLUMN, ROW, BOTTOM, LEFT, RIGHT

from .menu import Menu
from .network import TorConfig


class BTCZSetup(Box):
    def __init__(self, app:App, main:Window, settings, utils, units, commands, tr, font):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(40,43,48),
                flex = 1.5,
                padding = 5
            )
        )

        self.node_status = None
        self.blockchaine_index = None
        self.tor_enabled = None
        self.tor_config = None

        self.app = app
        self.main = main
        self.app_data = self.app.paths.data

        self.utils = utils
        self.units = units
        self.commands = commands
        self.settings = settings
        self.tr = tr
        self.font = font

        self.tooltip = ToolTip()

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

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
        self.status_label._impl.native.Font = self.font.get(10)

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
        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE
        if self.rtl:
            self.progress_bar._impl.native.RightToLeft = RightToLeft.YES
            self.progress_bar._impl.native.RightToLeftLayout = True

        self.status_box.add(
            self.status_label
        )
        self.progress_box.add(
            self.progress_bar
        )
        self.add(
            self.status_box,
            self.progress_box
        )

        self.app.add_background_task(self.check_network)


    def update_info_box(self):
        if self.rtl:
            padding = 0
            left = RIGHT
            right = LEFT
        else:
            padding = 3
            left = LEFT
            right = RIGHT
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
                text_align = self.tr.align("blocks_txt"),
                background_color = rgb(40,43,48),
                color = GRAY,
                padding_top = padding
            )
        )
        self.blocks_txt._impl.native.Font = self.font.get(self.tr.size("blocks_txt"), True)

        self.blocks_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("blocks_value"),
                background_color = rgb(40,43,48),
                color = WHITE,
                padding_top = padding
            )
        )
        self.blocks_value._impl.native.Font = self.font.get(self.tr.size("blocks_value"), True)

        self.mediantime_text = Label(
            text=self.tr.text("mediantime_text"),
            style=Pack(
                text_align = self.tr.align("mediantime_text"),
                background_color = rgb(40,43,48),
                color = GRAY
            )
        )
        self.mediantime_text._impl.native.Font = self.font.get(self.tr.size("mediantime_text"), True)

        self.mediantime_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("mediantime_value"),
                background_color = rgb(40,43,48),
                color = WHITE
            )
        )
        self.mediantime_value._impl.native.Font = self.font.get(self.tr.size("mediantime_value"), True)

        self.sync_txt = Label(
            text=self.tr.text("sync_txt"),
            style=Pack(
                text_align = self.tr.align("sync_txt"),
                flex = 1,
                background_color = rgb(40,43,48),
                color = GRAY
            )
        )
        self.sync_txt._impl.native.Font = self.font.get(self.tr.size("sync_txt"), True)

        self.sync_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("sync_value"),
                background_color = rgb(40,43,48),
                color = WHITE
            )
        )
        self.sync_value._impl.native.Font = self.font.get(self.tr.size("sync_value"), True)

        self.index_size_txt = Label(
            text=self.tr.text("index_size_txt"),
            style=Pack(
                text_align = self.tr.align("index_size_txt"),
                flex = 1,
                background_color = rgb(40,43,48),
                color=GRAY,
                padding_top = padding
            )
        )
        self.index_size_txt._impl.native.Font = self.font.get(self.tr.size("index_size_txt"), True)

        self.index_size_value = Label(
            text="",
            style=Pack(
                text_align = self.tr.align("index_size_value"),
                background_color = rgb(40,43,48),
                color = WHITE,
                padding_top = padding
            )
        )
        self.index_size_value._impl.native.Font = self.font.get(self.tr.size("index_size_value"), True)

        self.status_box._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_status_box()))
        self.box1._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_box1()))
        self.box2._impl.native.Invoke(Forms.MethodInvoker(lambda:self.update_box2()))

    def update_status_box(self):
        self.status_box.add(
            self.box1,
            self.box2
        )

    def update_box1(self):
        if self.rtl:
            self.box1.add(
                self.index_size_value,
                self.index_size_txt,
                self.blocks_value,
                self.blocks_txt
            )
        else:
            self.box1.add(
                self.blocks_txt,
                self.blocks_value,
                self.index_size_txt,
                self.index_size_value
            )

    def update_box2(self):
        if self.rtl:
            self.box2.add(
                self.sync_value,
                self.sync_txt,
                self.mediantime_value,
                self.mediantime_text
            )
        else:
            self.box2.add(
                self.mediantime_text,
                self.mediantime_value,
                self.sync_txt,
                self.sync_value
            )

    
    async def check_network(self, widget):
        async def on_result(widget, result):
            if result is True:
                self.show_tor_config()
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
                title=self.tr.title("tornetwork_dialog"),
                message=self.tr.message("tornetwork_dialog"),
                on_result=on_result
            )
        else:
            if self.tor_enabled is True:
                self.main.tor_icon.image = "images/tor_on.png"
                self.main.network_status.style.color = rgb(114,137,218)
                self.main.network_status.text = self.tr.text("tor_enabled")
                tor_running = await self.utils.is_tor_alive()
                await asyncio.sleep(1)
                if self.node_status and tor_running:
                    await self.check_sync_progress()
                else:
                    await self.check_tor_files()
            elif self.tor_enabled is False:
                self.main.network_status.style.color = GRAY
                self.main.network_status.text = self.tr.text("tor_disabled")
                await asyncio.sleep(1)
                if self.node_status:
                    await self.check_sync_progress()
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
                self.show_tor_config()
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


    def show_tor_config(self):
        self.tor_config = TorConfig(
            self.settings, self.utils, self.commands, self.tr, self.font, main=self.main, startup=self
        )
        self.tor_config._impl.native.Show(self.main._impl.native)


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
                if self.rtl:
                    percent_ar = self.units.arabic_digits(str(percent))
                    self.status_label.text = f"%{percent_ar}{text}"
                else:
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
            socks_port = torrc.get("SocksPort", "")
            hs_dirs = torrc.get("HiddenServiceDir", [])
            hs_ports = torrc.get("HiddenServicePort", [])
            if not isinstance(hs_dirs, list):
                hs_dirs = [hs_dirs]
            if not isinstance(hs_ports, list):
                hs_ports = [hs_ports]
            service_port = ""
            found_tor_service = False
            for dir_path, port_line in zip(hs_dirs, hs_ports):
                if dir_path.endswith("tor_service"):
                    service_port = port_line.split()[0] if port_line else ""
                    found_tor_service = True
                    break
            if socks_port:
                command += [f'-proxy=127.0.0.1:{socks_port}']
            if self.settings.only_onion():
                command += ['-onlynet=onion']
            if found_tor_service and service_port:
                command += ['-listen=1', '-discover=1']
        try:
            self.process = await asyncio.create_subprocess_exec(
                *command,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            await self.waiting_node_status()
        except Exception as e:
            print(f"Error starting bitcoinzd: {e}")
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
                        message = self.tr.text("loading_wallet")
                    elif error_message == "Rescanning...":
                        message = self.tr.text("rescan_wallet")
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
                            if info is not None:
                                blocks = info.get('blocks')
                                sync = info.get('verificationprogress')
                                mediantime = info.get('mediantime')
                                if isinstance(mediantime, int):
                                    mediantime_date = datetime.fromtimestamp(mediantime).strftime('%Y-%m-%d %H:%M:%S')
                                else:
                                    mediantime_date = "N/A"
                            else:
                                self.app.exit()
                                return

                        peerinfo, _ = await self.commands.getPeerinfo()
                        if peerinfo:
                            peerinfo = json.loads(peerinfo)
                            for node in peerinfo:
                                address = node.get('addr')
                                bytesrecv = node.get('bytesrecv')
                                tooltip_text += f"\n{address} - {self.units.format_bytes(bytesrecv)}"
                                
                        bitcoinz_size = int(self.utils.get_bitcoinz_size())
                        sync_percentage = sync * 100
                        sync_percentage_str = f"%{float(sync_percentage):.2f}"
                        if self.rtl:
                            blocks = self.units.arabic_digits(str(blocks))
                            mediantime_date = self.units.arabic_digits(mediantime_date)
                            sync_percentage_str = self.units.arabic_digits(str(sync_percentage_str))
                            bitcoinz_size = self.units.arabic_digits(str(bitcoinz_size))
                        self.blocks_value.text = f"{blocks}"
                        self.mediantime_value.text = mediantime_date
                        self.index_size_value.text = f"{bitcoinz_size} MB"
                        self.sync_value.text = sync_percentage_str
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
        self.main_menu = Menu(
            self.tor_enabled, self.settings, self.utils, self.units, self.commands, self.tr, self.font
        )
        self.main_menu._impl.native.TopMost = True
        self.main_menu._impl.native.Shown += self.on_show
        self.main.hide()
        await asyncio.sleep(1)
        self.main_menu.show()
        self.main_menu.notify.show()

    
    def on_show(self, sender, event):
        self.main_menu._impl.native.TopMost = False
        self.main_menu._impl.native.Activate()