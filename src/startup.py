
import asyncio
from framework import (
    App, Box, Color, Label, Font, FontStyle,
    DockStyle, AlignLabel, ProgressStyle, Os,
    Dialog, DialogIcon, DialogButton
)

from .utils import Utils


class BTCZSetup(Box):
    def __init__(self, main):
        super(BTCZSetup, self).__init__(
            size=(325,40),
            location=(5,300),
            background_color=Color.rgb(40,43,48)
        )

        self.app = App()
        self.utils = Utils()
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