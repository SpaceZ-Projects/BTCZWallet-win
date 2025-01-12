
import asyncio
import subprocess
import json
from datetime import datetime

from framework import (
    App, Box, Color, Label, Font, FontStyle,
    Os, Dialog, DialogIcon, DialogButton, ProgressStyle,
    DockStyle, AlignLabel
)

from .commands import Client
from .utils import Utils
from .menu import Menu


class BTCZSetup(Box):
    def __init__(self):
        super(BTCZSetup, self).__init__(
            size=(325,40),
            location=(5,300),
            background_color=Color.rgb(40,43,48)
        )

        self.app = App()
        self.commands = Client()
        self.utils = Utils()
        self.app_data = self.app.app_data

        self.node_status = None
        self.blockchaine_index = None

        self.status_label = Label(
            text="Verify binary files...",
            text_color=Color.WHITE,
            size=9,
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            aligne=AlignLabel.CENTER,
            dockstyle=DockStyle.FILL
        )

        self.insert([self.status_label])
        self.app.run_async(self.verify_binary_files())


    def update_info_box(self):
        self.app._main_window.progress_bar.style = ProgressStyle.BLOCKS
        self.clear()
        self.blocks_txt = Label(
            text="Blocks :",
            text_color=Color.GRAY,
            size=8,
            location=(10, 4),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            autosize=True
        )
        self.blocks_value = Label(
            text="",
            text_color=Color.WHITE,
            size=8,
            location=(60, 4),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            autosize=True
        )
        self.mediantime_text = Label(
            text="Date :",
            text_color=Color.GRAY,
            size=8,
            location=(10, 24),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            autosize=True
        )
        self.mediantime_value = Label(
            text="",
            text_color=Color.WHITE,
            size=8,
            location=(50, 24),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            width=200,
            autosize=True
        )
        self.sync_txt = Label(
            text="Sync :",
            text_color=Color.GRAY,
            size=8,
            location=(225, 24),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            autosize=True
        )
        self.sync_value = Label(
            text="",
            text_color=Color.WHITE,
            size=8,
            location=(260, 24),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            autosize=True
        )
        self.index_size_txt = Label(
            text="Size :",
            text_color=Color.GRAY,
            size=8,
            location=(225, 4),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            autosize=True
        )
        self.index_size_value = Label(
            text="",
            text_color=Color.WHITE,
            size=8,
            location=(260, 4),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD,
            autosize=True
        )
        self.insert(
            [
                self.blocks_value,
                self.blocks_txt,
                self.sync_value,
                self.sync_txt,
                self.index_size_value,
                self.index_size_txt,
                self.mediantime_value,
                self.mediantime_text
            ]
        )


    async def verify_binary_files(self):
        await asyncio.sleep(1)
        missing_files = self.utils.get_binary_files()
        if missing_files:
            self.status_label.text = "Downloading binary..."
            self.app._main_window.progress_bar.style = ProgressStyle.BLOCKS
            await self.utils.fetch_binary_files(
                self.status_label,
                self.app._main_window.progress_bar
            )
            await self.verify_params_files()
        else:
            await self.verify_params_files()

    async def verify_params_files(self):
        self.status_label.text = "Verify params..."
        self.app._main_window.progress_bar.style = ProgressStyle.MARQUEE
        await asyncio.sleep(1)
        missing_files, zk_params_path = self.utils.get_zk_params()
        if missing_files:
            self.status_label.text = "Downloading params..."
            self.app._main_window.progress_bar.style = ProgressStyle.BLOCKS
            await self.utils.fetch_params_files(
                missing_files, zk_params_path,
                self.status_label, self.app._main_window.progress_bar,
            )
            await self.verify_config_file()
        else:
            await self.verify_config_file()


    async def verify_config_file(self):
        self.status_label.text = "Verify bitcoinz.conf..."
        self.app._main_window.progress_bar.style = ProgressStyle.MARQUEE
        await asyncio.sleep(1)
        bitcoinz_path = self.utils.get_bitcoinz_path()
        config_file_path = self.utils.get_config_path()
        if not Os.Directory.Exists(bitcoinz_path):
            self.blockchaine_index = False
            Os.Directory.CreateDirectory(bitcoinz_path)
        if not Os.File.Exists(config_file_path):
            self.status_label.text = "Creating bitcoinz.conf..."
            self.utils.create_config_file(config_file_path)
            await asyncio.sleep(1)
            await self.execute_bitcoinz_node()
        else:
            self.blockchaine_index = True
            await self.verify_bockchaine_index()
        
    
    async def verify_bockchaine_index(self):
        if self.blockchaine_index:
            await self.execute_bitcoinz_node()
        else:
            Dialog(
                title="Download Bootstarp",
                message="Would you like to download the BitcoinZ bootstrap? This will help you sync faster. If you prefer to sync from block 0, Click NO.",
                icon=DialogIcon.QUESTION,
                buttons=DialogButton.YESNO,
                result=self.download_bootstrap_result
            )

    def download_bootstrap_result(self, result):
        if result == "Yes":
            self.app.run_async(self.download_bitcoinz_bootstrap())
        elif result == "No":
            self.app.run_async(self.execute_bitcoinz_node())


    async def download_bitcoinz_bootstrap(self):
        self.status_label.text = "Downloading bootstrap..."
        self.app._main_window.progress_bar.style = ProgressStyle.BLOCKS
        await self.utils.fetch_bootstrap_files(
            self.status_label,
            self.app._main_window.progress_bar)
        await self.extract_bootstrap_file()


    async def extract_bootstrap_file(self):
        self.status_label.text = "Extracting bootstrap..."
        self.app._main_window.progress_bar.style = ProgressStyle.MARQUEE
        await self.utils.extract_7z_files(
            self.status_label,
            self.app._main_window.progress_bar
        )
        await self.execute_bitcoinz_node()


    async def execute_bitcoinz_node(self):
        self.status_label.text = "Starting node..."
        bitcoinzd = "bitcoinzd.exe"
        node_file = Os.Path.Combine(self.app_data, bitcoinzd)
        command = [node_file]
        try:
            self.process = await asyncio.create_subprocess_exec(
                    *command,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
            )
            await self.waiting_node_status()
        except Exception as e:
            print(e)
        finally:
            if self.process:
                await self.process.wait()
                self.process.terminate()
                

    async def waiting_node_status(self):
        await asyncio.sleep(1)
        result, error_message = await self.commands.getInfo()
        if result:
            self.node_status = True
            await self.verify_sync_progress()
            return
        else:
            while True:
                result, error_message = await self.commands.getInfo()
                if result:
                    self.node_status = True
                    await self.verify_sync_progress()
                    return
                else:
                    if error_message:
                        self.status_label.text = error_message
                await asyncio.sleep(4)


    async def verify_sync_progress(self):
        await asyncio.sleep(1)
        blockchaininfo, error_message = await self.commands.getBlockchainInfo()
        if isinstance(blockchaininfo, str):
            info = json.loads(blockchaininfo)
        if info is not None:
            sync = info.get('verificationprogress')
            sync_percentage = sync * 100
            if sync_percentage <= 99:
                self.update_info_box()
                self.app.run_async(self.show_dialog())
                while True:
                    blockchaininfo, error_message = await self.commands.getBlockchainInfo()
                    if isinstance(blockchaininfo, str):
                        info = json.loads(blockchaininfo)
                    else:
                        self.node_status = False
                        self.app._main_window.exit()
                        return
                    if info is not None:
                        blocks = info.get('blocks')
                        sync = info.get('verificationprogress')
                        mediantime = info.get('mediantime')
                    else:
                        blocks = sync = mediantime = "N/A"
                    if isinstance(mediantime, int):
                        mediantime_date = datetime.fromtimestamp(mediantime).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        mediantime_date = "N/A"
                    bitcoinz_size = self.utils.get_bitcoinz_size()
                    sync_percentage = sync * 100
                    self.blocks_value.text = f"{blocks}"
                    self.mediantime_value.text = mediantime_date
                    self.index_size_value.text = f"{int(bitcoinz_size)} MB"
                    self.sync_value.text = f"%{float(sync_percentage):.2f}"
                    self.app._main_window.progress_bar.value = int(sync_percentage)
                    if sync_percentage > 99:
                        await self.update_main_window()
                        return
                    await asyncio.sleep(2)
            elif sync_percentage > 99:
                await self.update_main_window()

    async def show_dialog(self):
        Dialog(
            title="Disabled Wallet",
            message="The wallet is currently disabled as it is synchronizing. It will be accessible once the sync process is complete.",
            icon=DialogIcon.INFORMATION,
            buttons=DialogButton.OK
        )

    async def update_main_window(self):
        self.app._main_window.hide()
        await asyncio.sleep(0.5)
        self.app._main_window.clear()
        self.app._main_window.center_screen = False
        self.app._main_window.update_size((900,600))
        self.app._main_window.minimizable = True
        self.app._main_window.maxmizable = True
        self.app._main_window.resizable = True
        self.app.invoke(self.insert_main_menu)


    def insert_main_menu(self):
        self.main_menu = Menu()
        self.app._main_window.insert(
            [
                self.main_menu
            ]
        )
        self.app.run_async(self.invoke_main_window())

    async def invoke_main_window(self):
        await asyncio.sleep(0.5)
        self.app.invoke(self.show_main_menu)
    
    def show_main_menu(self):
        self.app._main_window.show()
        self.app._main_window.notify.show()