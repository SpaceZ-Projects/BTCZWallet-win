
import asyncio
import json
import psutil
import subprocess
import re

from toga import (
    App, Box, Label, Selection, TextInput,
    ProgressBar, Window, ScrollContainer
)
from ..framework import ComboStyle
from toga.style.pack import Pack
from toga.constants import COLUMN, CENTER, BOLD, ROW
from toga.colors import rgb, GRAY, WHITE, GREENYELLOW, BLACK, RED

from .utils import Utils
from .client import Client


class Mining(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5)
            )
        )

        self.app = app
        self.main = main
        self.utils = Utils(self.app)
        self.commands = Client(self.app)

        self.mining_toggle = None
        self.selected_miner = None
        self.selected_address = None
        self.selected_pool = None
        self.selected_server = None
        self.worker_name = None
        self.mining_status = None

        self.miner_label = Label(
            text="Miner :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )
        self.miner_selection = Selection(
            items=[
                {"miner": "Select Miner"},
                {"miner": "MiniZ"},
                {"miner": "Gminer"}
            ],
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 2,
                padding_top = 10
            ),
            accessor="miner",
            on_change=self.verify_miners_apps
        )
        self.miner_selection._impl.native.FlatStyle = ComboStyle.FLAT

        self.progress_bar = ProgressBar(
            max = 100,
            style=Pack(
                height = 5,
                width = 100,
                padding_left = 20
            )
        )

        self.setup_miner_box = Box(
            style=Pack(
                direction = ROW,
                alignment = CENTER,
                background_color = rgb(30,33,36),
                flex = 1 
            )
        )

        self.selection_miner_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding=(10,5,0,5),
                height = 55
            )
        )

        self.address_label = Label(
            text="Address :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )
        self.address_selection = Selection(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 2,
                padding_top = 10
            ),
            accessor="select_address",
            on_change=self.display_address_balance
        )
        self.address_selection._impl.native.FlatStyle = ComboStyle.FLAT

        self.address_balance = Label(
            text="0.00000000",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )

        self.selection_address_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding=(5,5,0,5),
                height = 55
            )
        )

        self.pool_label = Label(
            text="Pool :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )
        self.pool_selection = Selection(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 2,
                padding_top = 10
            ),
            items=[
                {"pool": "Select Pool"},
                {"pool": "2Mars"},
                {"pool": "Swgroupe"},
                {"pool": "Zeropool"},
                {"pool": "PCmining"},
                {"pool": "Darkfibersmines"},
                {"pool": "Zergpool"}
            ],
            accessor="pool",
            on_change=self.update_server_selection
        )
        self.pool_selection._impl.native.FlatStyle = ComboStyle.FLAT

        self.pool_region_selection = Selection(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1,
                padding = (10,10,0,15)
            ),
            accessor="region",
            on_change=self.update_region_server
        )
        self.pool_region_selection._impl.native.FlatStyle = ComboStyle.FLAT

        self.selection_pool_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding=(5,5,0,5),
                height = 55
            )
        )

        self.worker_label = Label(
            text="Worker :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                text_align = CENTER,
                flex = 2,
                padding_top = 12
            )
        )
        self.worker_input = TextInput(
            placeholder="Wroker Name",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 2,
                padding_top = 10
            ),
            on_change=self.update_worker_name
        )
        self.empty_box = Box(
            style=Pack(
                background_color = rgb(30,33,36),
                flex = 4
            )
        )
        self.worker_box = Box(
           style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding = (5,5,0,5),
                height = 50
            ) 
        )

        self.ouputs_box = Box(
           style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1,
                padding = (5,10,0,10)
            ) 
        )
        self.ouputs_box._impl.native.Resize += self.ouputs_box_on_resize

        self.ouputs_scroll = ScrollContainer(
            content=self.ouputs_box,
            style=Pack(
                background_color = rgb(40,43,48),
                flex = 1
            )
        )

        self.mining_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.start_mining_label = Label(
            text="Start Mining",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )

        self.start_mining_button = Box(
            style=Pack(
                background_color = rgb(40,43,48),
                alignment = CENTER,
                padding = 7,
                width = 200,
                height = 40
            )
        )
        self.start_mining_button._impl.native.MouseEnter += self.start_mining_button_mouse_enter
        self.start_mining_button._impl.native.MouseLeave += self.start_mining_button_mouse_leave
        self.start_mining_label._impl.native.MouseEnter += self.start_mining_button_mouse_enter
        self.start_mining_label._impl.native.MouseLeave += self.start_mining_button_mouse_leave
        self.start_mining_button._impl.native.Click += self.start_mining_button_click
        self.start_mining_label._impl.native.Click += self.start_mining_button_click

        self.start_mining_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = 5,
                alignment = CENTER,
                height = 55
            )
        )


    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.mining_toggle:
            self.add(
                self.selection_miner_box,
                self.selection_address_box,
                self.selection_pool_box,
                self.worker_box,
                self.ouputs_scroll,
                self.start_mining_box
            )
            self.selection_miner_box.add(
                self.miner_label,
                self.miner_selection,
                self.setup_miner_box
            )
            self.selection_address_box.add(
                self.address_label,
                self.address_selection,
                self.address_balance
            )
            self.selection_pool_box.add(
                self.pool_label,
                self.pool_selection,
                self.pool_region_selection
            )
            self.worker_box.add(
                self.worker_label,
                self.worker_input,
                self.empty_box
            )
            self.start_mining_box.add(
                self.mining_box,
                self.start_mining_button
            )
            self.start_mining_button.add(
                self.start_mining_label
            )
            self.mining_toggle = True
            self.app.add_background_task(self.update_mining_options)




    async def verify_miners_apps(self, selection):
        self.selected_miner = self.miner_selection.value.miner
        if not self.selected_miner:
            return
        if self.selected_miner == "Select Miner":
            return
        miner_path, url, zip_file = self.utils.get_miner_path(self.selected_miner)
        if not miner_path:
            self.miner_selection.enabled = False
            self.setup_miner_box.add(
                self.progress_bar
            )
            await self.utils.fetch_miner(
                self.miner_selection, self.setup_miner_box, self.progress_bar, self.selected_miner, zip_file, url
            )


    async def display_address_balance(self, selection):
        self.selected_address = self.address_selection.value.select_address
        balance, _ = await self.commands.z_getBalance(self.selected_address)
        if balance:
            if float(balance) <= 0:
                self.address_balance.style.color = GRAY
            else:
                self.address_balance.style.color = WHITE
            format_balance = self.utils.format_balance(float(balance))
            self.address_balance.text = format_balance

    
    async def get_transparent_addresses(self):
        addresses_data, _ = await self.commands.ListAddresses()
        if addresses_data:
            addresses_data = json.loads(addresses_data)
        else:
            addresses_data = []
        if addresses_data is not None:
            address_items = [(address_info, address_info) for address_info in addresses_data]

        return address_items
    

    async def update_server_selection(self, selection):
        self.selected_pool = self.pool_selection.value.pool
        if not self.selected_pool:
            return
        if self.selected_pool == "2Mars":
            pool_rergion_items = [
                {"region": "Canada", "server": "btcz.ca.2mars.biz:1234"},
                {"region": "USA", "server": "btcz.us.2mars.biz:1234"},
                {"region": "Netherlands", "server": "btcz.eu.2mars.biz:1234"},
                {"region": "Singapore", "server": "btcz.sg.2mars.biz:1234"}
            ]
        elif self.selected_pool == "Swgroupe":
            pool_rergion_items = [
                {"region": "France", "server": "swgroupe.fr:2001"}
            ]
        elif self.selected_pool == "Zeropool":
            pool_rergion_items = [
                {"region": "USA", "server": "zeropool.io:1235"}
            ]
        elif self.selected_pool == "PCmining":
            pool_rergion_items = [
                {"region": "Germany", "server": "btcz.pcmining.xyz:3333"}
            ]
        elif self.selected_pool == "Darkfibersmines":
            pool_rergion_items = [
                {"region": "USA", "server": "142.4.211.28:4000"},
            ]
        elif self.selected_pool == "Zergpool":
            pool_rergion_items = [
                {"region": "North America", "server": "equihash144.na.mine.zergpool.com:2146"},
                {"region": "Europe", "server": "equihash144.eu.mine.zergpool.com:2146"},
                {"region": "Asia", "server": "equihash144.asia.mine.zergpool.com:2146"}
            ]
        else:
            self.pool_region_selection.items.clear()
            self.pool_region_selection.enabled = False
            return
        
        self.pool_region_selection.items = pool_rergion_items
        self.pool_region_selection.enabled = True


    async def update_region_server(self, selection):
        if self.selected_pool == "Select Pool":
            return
        self.selected_server = self.pool_region_selection.value.server
        if not self.selected_server:
            return


    async def update_worker_name(self, input):
        self.worker_name = self.worker_input.value
        if not self.worker_name:
            return


    def start_mining_button_click(self, sender, event):
        if not self.selected_miner or self.selected_miner == "Select Miner":
            self.main.error_dialog(
                "Missing Selection",
                "Please select the miner software"
            )
            return
        elif not self.selected_pool or self.selected_pool == "Select Pool":
            self.main.error_dialog(
                "Missing Selection",
                "Please select the mining pool"
            )
            return
        elif not self.worker_name:
            self.main.error_dialog(
                "Missing Name",
                "Please set a worker name."
            )
            return
        self.disable_mining_button()
        self.app.add_background_task(self.prepare_mining)


    async def prepare_mining(self, widegt):
        miner_path,_,_ = self.utils.get_miner_path(self.selected_miner)
        if miner_path:
            if self.selected_miner == "MiniZ":
                command = [f'{miner_path} --url {self.selected_address}.{self.worker_name}@{self.selected_server} --pass x --par 144,5 --pers BitcoinZ']
            elif self.selected_miner == "Gminer":
                command = [f'{miner_path} --server {self.selected_server} --user {self.selected_address}.{self.worker_name} --pass x --algo 144_5 --pers BitcoinZ']
            self.disable_mining_inputs()
            await self.start_mining_command(command)


    async def start_mining_command(self, command):
        try:
            self.process = await asyncio.create_subprocess_shell(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.mining_status = True
            self.update_mining_button("stop")
            self.enable_mining_button()
            self.ouputs_box.clear()
            clean_regex = re.compile(r'\x1b\[[0-9;]*[mGK]|[^a-zA-Z0-9\s\[\]=><.%()/,`\'":]')
            while True:
                stdout_line = await self.process.stdout.readline()
                if stdout_line:
                    decoded_line = stdout_line.decode().strip()
                    cleaned_line = clean_regex.sub('', decoded_line)
                    self.print_outputs(cleaned_line)
                else:
                    break
            await self.process.wait()
            remaining_stdout = await self.process.stdout.read()
            remaining_stderr = await self.process.stderr.read()
            if remaining_stdout:
                print(remaining_stdout.decode().strip())
            if remaining_stderr:
                print(remaining_stderr.decode().strip())

        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            self.disable_mining_button()
            self.update_mining_button("start")
            self.enable_mining_inputs()
            self.enable_mining_button()


    def print_outputs(self, line):
        output_value = Label(
            text=line,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size = 10
            )
        )
        self.ouputs_box.add(
            output_value
        )
        if self.ouputs_scroll.vertical_position == self.ouputs_scroll.max_vertical_position:
            return
        self.ouputs_scroll.vertical_position = self.ouputs_scroll.max_vertical_position


    def ouputs_box_on_resize(self, sender, event):
        if self.mining_toggle:
            if self.ouputs_scroll.vertical_position == self.ouputs_scroll.max_vertical_position:
                return
            self.ouputs_scroll.vertical_position = self.ouputs_scroll.max_vertical_position

        
    async def update_mining_options(self, widget):
        transparent_addresses = await self.get_transparent_addresses()
        self.address_selection.items.clear()
        self.address_selection.items = transparent_addresses


    def stop_mining_button_click(self, sender, event):
        self.app.add_background_task(self.stop_mining)


    async def stop_mining(self, widget):
        if self.selected_miner == "MiniZ":
            process_name =  "miniZ.exe"
        elif self.selected_miner == "Gminer":
            process_name = "miner.exe"
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == process_name:
                    proc.kill()
            self.process.terminate()
            self.ouputs_box.clear()
            self.mining_status = False
            self.print_outputs("Miner Stopped !")
        except Exception as e:
            print(f"Exception occurred while killing process: {e}")


    def update_mining_button(self, option):
        if option == "stop":
            self.start_mining_label.text = "Stop"
            self.start_mining_label.style.color = WHITE
            self.start_mining_label.style.background_color = RED
            self.start_mining_button.style.background_color = RED
            self.start_mining_button._impl.native.MouseEnter -= self.start_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave -= self.start_mining_button_mouse_leave
            self.start_mining_label._impl.native.MouseEnter -= self.start_mining_button_mouse_enter
            self.start_mining_label._impl.native.MouseLeave -= self.start_mining_button_mouse_leave
            self.start_mining_button._impl.native.Click -= self.start_mining_button_click
            self.start_mining_label._impl.native.Click -= self.start_mining_button_click

            self.start_mining_button._impl.native.MouseEnter += self.stop_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave += self.stop_mining_button_mouse_leave
            self.start_mining_label._impl.native.MouseEnter += self.stop_mining_button_mouse_enter
            self.start_mining_label._impl.native.MouseLeave += self.stop_mining_button_mouse_leave
            self.start_mining_button._impl.native.Click += self.stop_mining_button_click
            self.start_mining_label._impl.native.Click += self.stop_mining_button_click

        elif option == "start":
            self.start_mining_label.text = "Start Mining"
            self.start_mining_label.style.color = BLACK
            self.start_mining_label.style.background_color = GREENYELLOW
            self.start_mining_button.style.background_color = GREENYELLOW
            self.start_mining_button._impl.native.MouseEnter -= self.stop_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave -= self.stop_mining_button_mouse_leave
            self.start_mining_label._impl.native.MouseEnter -= self.stop_mining_button_mouse_enter
            self.start_mining_label._impl.native.MouseLeave -= self.stop_mining_button_mouse_leave
            self.start_mining_button._impl.native.Click -= self.stop_mining_button_click
            self.start_mining_label._impl.native.Click -= self.stop_mining_button_click

            self.start_mining_button._impl.native.MouseEnter += self.start_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave += self.start_mining_button_mouse_leave
            self.start_mining_label._impl.native.MouseEnter += self.start_mining_button_mouse_enter
            self.start_mining_label._impl.native.MouseLeave += self.start_mining_button_mouse_leave
            self.start_mining_button._impl.native.Click += self.start_mining_button_click
            self.start_mining_label._impl.native.Click += self.start_mining_button_click

    
    def disable_mining_button(self):
        self.start_mining_button._impl.native.Enabled = False
        self.start_mining_label._impl.native.Enabled = False

    def disable_mining_inputs(self):
        self.miner_selection.enabled = False
        self.address_selection.enabled = False
        self.pool_selection.enabled = False
        self.pool_region_selection.enabled = False
        self.worker_input.readonly = True

    def enable_mining_inputs(self):
        self.miner_selection.enabled = True
        self.address_selection.enabled = True
        self.pool_selection.enabled = True
        self.pool_region_selection.enabled = True
        self.worker_input.readonly = False


    def enable_mining_button(self):
        self.start_mining_button._impl.native.Enabled = True
        self.start_mining_label._impl.native.Enabled = True


    def start_mining_button_mouse_enter(self, sender, event):
        self.start_mining_label.style.color = BLACK
        self.start_mining_label.style.background_color = GREENYELLOW
        self.start_mining_button.style.background_color = GREENYELLOW


    def start_mining_button_mouse_leave(self, sender, event):
        self.start_mining_label.style.color = GRAY
        self.start_mining_label.style.background_color = rgb(40,43,48)
        self.start_mining_button.style.background_color = rgb(40,43,48)

    def stop_mining_button_mouse_enter(self, sender, event):
        self.start_mining_label.style.color = WHITE
        self.start_mining_label.style.background_color = RED
        self.start_mining_button.style.background_color = RED


    def stop_mining_button_mouse_leave(self, sender, event):
        self.start_mining_label.style.color = GRAY
        self.start_mining_label.style.background_color = rgb(40,43,48)
        self.start_mining_button.style.background_color = rgb(40,43,48)