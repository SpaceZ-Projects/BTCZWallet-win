
import asyncio
import json
import subprocess
from datetime import datetime
from framework import (
    App, Box, Color, Label, Font, FontStyle,
    DockStyle, AlignLabel, ProgressStyle, Os,
    Dialog, DialogIcon, DialogButton
)

from .utils import Utils
from .commands import Client


class BTCZSetup(Box):
    def __init__(self, main):
        super(BTCZSetup, self).__init__(
            size=(325,40),
            location=(5,300),
            background_color=Color.rgb(40,43,48)
        )

        self.app = App()
        self.utils = Utils()
        self.commands = Client()
        self.main = main
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
        self.clear()
        self.blocks_txt = Label(
            text="Blocks :",
            text_color=Color.GRAY,
            size=8,
            location=(10, 2),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD
        )
        self.blocks_value = Label(
            text="",
            text_color=Color.WHITE,
            size=8,
            location=(60, 2),
            font=Font.SANSSERIF
        )
        self.mediantime_text = Label(
            text="Date :",
            text_color=Color.GRAY,
            size=8,
            location=(10, 20),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD
        )
        self.mediantime_value = Label(
            text="",
            text_color=Color.WHITE,
            size=8,
            location=(50, 20),
            font=Font.SANSSERIF,
            width=200
        )
        self.sync_txt = Label(
            text="Sync :",
            text_color=Color.GRAY,
            size=8,
            location=(225, 20),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD
        )
        self.sync_value = Label(
            text="",
            text_color=Color.WHITE,
            size=8,
            location=(260, 20),
            font=Font.SANSSERIF
        )
        self.index_size_txt = Label(
            text="Size :",
            text_color=Color.GRAY,
            size=8,
            location=(225, 2),
            font=Font.SANSSERIF,
            style=FontStyle.BOLD
        )
        self.index_size_value = Label(
            text="",
            text_color=Color.WHITE,
            size=8,
            location=(260, 2),
            font=Font.SANSSERIF
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
        await asyncio.sleep(2)
        missing_files = self.utils.get_binary_files()
        if missing_files:
            self.status_label.text = "Downloading binary..."
            self.main.progress_bar.style = ProgressStyle.BLOCKS
            await self.utils.fetch_binary_files(
                self.status_label,
                self.main.progress_bar
            )
            await self.verify_params_files()
        else:
            await self.verify_params_files()

    async def verify_params_files(self):
        self.status_label.text = "Verify params..."
        self.main.progress_bar.style = ProgressStyle.MARQUEE
        await asyncio.sleep(2)
        missing_files, zk_params_path = self.utils.get_zk_params()
        if missing_files:
            self.status_label.text = "Downloading params..."
            self.main.progress_bar.style = ProgressStyle.BLOCKS
            await self.utils.fetch_params_files(
                missing_files, zk_params_path,
                self.status_label, self.main.progress_bar,
            )
            await self.verify_config_file()
        else:
            await self.verify_config_file()


    async def verify_config_file(self):
        self.status_label.text = "Verify bitcoinz.conf..."
        self.main.progress_bar.style = ProgressStyle.MARQUEE
        await asyncio.sleep(2)
        bitcoinz_path = self.utils.get_bitcoinz_path()
        config_file_path = self.utils.get_config_path()
        if not Os.Directory.Exists(bitcoinz_path):
            self.blockchaine_index = False
            Os.Directory.CreateDirectory(bitcoinz_path)
        if not Os.File.Exists(config_file_path):
            self.status_label.text = "Creating bitcoinz.conf..."
            self.utils.create_config_file(config_file_path)
            await asyncio.sleep(2)
            await self.verify_bockchaine_index()
        else:
            self.blockchaine_index = True
            await self.verify_bockchaine_index()
        
    async def verify_bockchaine_index(self):
        #Optional: to download boostrap in fisrt use (if BitcoinZ dir not exists)
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
        self.main.progress_bar.style = ProgressStyle.BLOCKS
        await self.utils.fetch_bootstrap_files(
            self.status_label,
            self.main.progress_bar)
        await self.extract_bootstrap_file()


    async def extract_bootstrap_file(self):
        self.status_label.text = "Extracting bootstrap..."
        self.main.progress_bar.style = ProgressStyle.MARQUEE
        await self.utils.extract_7z_files(
            self.status_label,
            self.main.progress_bar
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
                self.main.progress_bar.style = ProgressStyle.BLOCKS
                self.update_info_box()
                self.app.run_async(self.show_dialog())
                while True:
                    blockchaininfo, error_message = await self.commands.getBlockchainInfo()
                    if isinstance(blockchaininfo, str):
                        info = json.loads(blockchaininfo)
                    else:
                        self.node_status = False
                        self.main.exit()
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
                    self.main.progress_bar.value = int(sync_percentage)
                    if sync_percentage > 99:
                        await self.open_wallet()
                        return
                    await asyncio.sleep(2)
            elif sync_percentage > 99:
                await self.open_wallet()

    async def show_dialog(self):
        Dialog(
            title="Disabled Wallet",
            message="The wallet is currently disabled as it is synchronizing. It will be accessible once the sync process is complete.",
            icon=DialogIcon.INFORMATION,
            buttons=DialogButton.OK
        )