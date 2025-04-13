
import asyncio
import json
import psutil
import subprocess
import re
import aiohttp

from toga import (
    App, Box, Label, Selection, TextInput,
    ProgressBar, Window, ScrollContainer,
    Button, ImageView
)
from ..framework import FlatStyle, Os, ToolTip
from toga.style.pack import Pack
from toga.constants import COLUMN, CENTER, BOLD, ROW
from toga.colors import rgb, GRAY, WHITE, GREENYELLOW, BLACK, RED

from .utils import Utils
from .units import Units
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
        self.units = Units(self.app)
        self.commands = Client(self.app)
        self.tooltip = ToolTip()

        self.mining_toggle = None
        self.selected_miner = None
        self.selected_address = None
        self.selected_pool = None
        self.selected_server = None
        self.worker_name = None
        self.mining_status = None
        self.pool_api = None
        self.miner_command = None

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
        self.miner_selection._impl.native.FlatStyle = FlatStyle.FLAT

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
        self.address_selection._impl.native.FlatStyle = FlatStyle.FLAT
        self.address_selection._impl.native.DropDownHeight = 150

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
                {"pool": "Select Pool"}
            ],
            accessor="pool",
            on_change=self.update_server_selection
        )
        self.pool_selection._impl.native.FlatStyle = FlatStyle.FLAT

        self.pool_region_selection = Selection(
            enabled=False,
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
        self.pool_region_selection._impl.native.FlatStyle = FlatStyle.FLAT

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
            placeholder="Worker Name",
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
                flex = 1,
                padding_right = 6
            )
        )

        self.totalshares_icon = ImageView(
            image="images/shares.png",
            style=Pack(
                background_color = rgb(30,33,36),
                padding_left = 20
            )
        )
        self.tooltip.insert(self.totalshares_icon._impl.native, "Total shares")

        self.totalshares_value = Label(
            text="0.00",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                padding_left = 5
            )
        )

        self.balance_icon = ImageView(
            image="images/balance.png",
            style=Pack(
                background_color = rgb(30,33,36),
                padding_left = 20
            )
        )
        self.tooltip.insert(self.balance_icon._impl.native, "Balance")

        self.balance_value = Label(
            text="0.00",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                padding_left = 5
            )
        )

        self.immature_icon = ImageView(
            image="images/immature.png",
            style=Pack(
                background_color = rgb(30,33,36),
                padding_left = 20
            )
        )
        self.tooltip.insert(self.immature_icon._impl.native, "Immature balance")

        self.immature_value = Label(
            text="0.00",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                padding_left = 2
            )
        )

        self.paid_icon = ImageView(
            image="images/paid.png",
            style=Pack(
                background_color = rgb(30,33,36),
                padding = (2,0,0,20)
            )
        )
        self.tooltip.insert(self.paid_icon._impl.native, "Total paid")

        self.paid_value = Label(
            text="0.00",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                padding_left = 6
            )
        )

        self.solutions_icon = ImageView(
            image="images/hash_speed.png",
            style=Pack(
                background_color = rgb(30,33,36),
                padding_left = 20
            )
        )
        self.tooltip.insert(self.solutions_icon._impl.native, "Solutions speed")

        self.solutions_value = Label(
            text="0.00 Sol/s",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                padding_left = 6
            )
        )

        self.estimated_icon = ImageView(
            image="images/estimated.png",
            style=Pack(
                background_color = rgb(30,33,36),
                padding_left = 20
            )
        )
        self.tooltip.insert(self.estimated_icon._impl.native, "Estimated reward")

        self.estimated_value = Label(
            text="0.00 /Day",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                padding_left = 6
            )
        )

        self.mining_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment= CENTER,
                flex = 1
            )
        )

        self.start_mining_button = Button(
            text="Start Mining",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                width = 150,
                alignment= CENTER,
                padding_right = 10
            ),
            on_press=self.start_mining_button_click
        )
        self.start_mining_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.start_mining_button._impl.native.MouseEnter += self.start_mining_button_mouse_enter
        self.start_mining_button._impl.native.MouseLeave += self.start_mining_button_mouse_leave

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
            self.mining_box.add(
                self.totalshares_icon,
                self.totalshares_value,
                self.balance_icon,
                self.balance_value,
                self.immature_icon,
                self.immature_value,
                self.paid_icon,
                self.paid_value,
                self.solutions_icon,
                self.solutions_value,
                self.estimated_icon,
                self.estimated_value
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
            format_balance = self.units.format_balance(float(balance))
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
    

    def update_server_selection(self, selection):
        self.selected_pool = self.pool_selection.value.pool
        if not self.selected_pool:
            return
        
        pools_data = self.get_pools_data()
        if self.selected_pool in pools_data:
            self.pool_api = pools_data[self.selected_pool]["api"]
            pool_rergion_items = pools_data[self.selected_pool]["regions"]
            self.pool_region_selection.items = pool_rergion_items
            self.pool_region_selection.enabled = True
        else:
            self.pool_region_selection.items.clear()
            self.pool_region_selection.enabled = False


    def get_pools_data(self):
        try:
            pools_json = Os.Path.Combine(str(self.app.paths.app), 'resources', 'pools.json')
            with open(pools_json, 'r') as f:
                pools_data = json.load(f)
                return pools_data
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        

    def get_pools_list(self):
        pools_data = self.get_pools_data()
        if pools_data:
            pool_items = [{"pool": pool} for pool in pools_data.keys()]
            return pool_items


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


    def start_mining_button_click(self, button):
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
        self.prepare_mining()


    def prepare_mining(self):
        miner_path,_,_ = self.utils.get_miner_path(self.selected_miner)
        if miner_path:
            if self.selected_miner == "MiniZ":
                if self.selected_pool == "Zpool":
                    self.miner_command = [f'{miner_path} --url {self.selected_address}.{self.worker_name}@{self.selected_server} --pass c=BTCZ,zap=BTCZ --pers auto']
                else:
                    self.miner_command = [f'{miner_path} --url {self.selected_address}.{self.worker_name}@{self.selected_server} --pass x --par 144,5 --pers BitcoinZ']
            elif self.selected_miner == "Gminer":
                if self.selected_pool == "Zpool":
                    self.miner_command = [f'{miner_path} --server {self.selected_server} --user {self.selected_address}.{self.worker_name} --pass c=BTCZ,zap=BTCZ --algo 144_5 --pers auto']
                else:
                    self.miner_command = [f'{miner_path} --server {self.selected_server} --user {self.selected_address}.{self.worker_name} --pass x --algo 144_5 --pers BitcoinZ']
            self.disable_mining_inputs()
            self.app.add_background_task(self.start_mining_command)
            self.mining_status = True
            self.app.add_background_task(self.fetch_miner_stats)


    async def start_mining_command(self, widget):
        self.update_mining_button("stop")
        self.ouputs_box.clear()
        try:
            self.process = await asyncio.create_subprocess_shell(
                *self.miner_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
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
            self.update_mining_button("start")
            self.enable_mining_inputs()
            self.mining_status = False
            self.miner_command = None


    def print_outputs(self, line):
        output_value = Label(
            text=line,
            style=Pack(
                color = WHITE,
                background_color = rgb(60,62,64),
                font_size = 10,
                padding = 2
            )
        )
        self.ouputs_box.add(
            output_value
        )
        if self.ouputs_scroll.vertical_position == self.ouputs_scroll.max_vertical_position:
            return
        self.ouputs_scroll.vertical_position = self.ouputs_scroll.max_vertical_position


    async def fetch_miner_stats(self, widget):
        api = self.pool_api + self.selected_address
        async with aiohttp.ClientSession() as session:
            while True:
                if not self.mining_status:
                    return
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    async with session.get(api, headers=headers) as response:
                        response.raise_for_status()
                        mining_data = await response.json()
                        total_share = mining_data.get("totalShares") or sum(miner.get("accepted", 0) for miner in mining_data.get("miners", []))
                        balance = mining_data.get("balance", 0)
                        immature_bal = mining_data.get("immature", mining_data.get("unpaid", 0))
                        paid = mining_data.get("paid", mining_data.get("paidtotal", 0))
                        workers_data = mining_data.get("workers", {})
                        if workers_data:
                            for worker_name, worker_info in workers_data.items():
                                worker_name_parts = worker_name.split(".")
                                if len(worker_name_parts) > 1:
                                    name = worker_name_parts[1]
                                else:
                                    name = worker_name
                                if name == self.worker_name:
                                    hashrate = worker_info.get("hashrate", None)
                                    if hashrate:
                                        rate = self.units.hash_to_solutions(hashrate)
                                        self.solutions_value.text = f"{rate:.2f} Sol/s"
                                        estimated_24h = await self.units.estimated_earn(24, hashrate)
                                        self.estimated_value.text = f"{int(estimated_24h)} /Day"
                        else:
                            total_hashrates = mining_data.get("total_hashrates", [])
                            if total_hashrates:
                                for hashrate in total_hashrates:
                                    for algo, rate in hashrate.items():
                                        self.solutions_value.text = f"{rate:.2f} Sol/s"

                        self.totalshares_value.text = f"{total_share:.2f}"
                        self.balance_value.text = self.units.format_balance(balance)
                        self.immature_value.text = self.units.format_balance(immature_bal)
                        self.paid_value.text = self.units.format_balance(paid)

                except aiohttp.ClientError as e:
                    print(f"Error while fetching data: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

                await asyncio.sleep(150)


    def ouputs_box_on_resize(self, sender, event):
        if self.mining_toggle:
            if self.ouputs_scroll.vertical_position == self.ouputs_scroll.max_vertical_position:
                return
            self.ouputs_scroll.vertical_position = self.ouputs_scroll.max_vertical_position

        
    async def update_mining_options(self, widget):
        transparent_addresses = await self.get_transparent_addresses()
        self.address_selection.items.clear()
        self.address_selection.items = transparent_addresses
        pools_list = self.get_pools_list()
        for pool in pools_list:
            self.pool_selection.items.insert(1, pool)


    async def stop_mining_button_click(self, button):
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
            self.print_outputs("Miner Stopped !")
            self.totalshares_value.text = "0.00"
            self.balance_value.text = "0.00"
            self.immature_value.text = "0.00"
            self.paid_value.text = "0.00"
            self.solutions_value.text = "0.00 Sol/s"
            self.estimated_value.text = "0.00 /Day"
        except Exception as e:
            print(f"Exception occurred while killing process: {e}")


    def update_mining_button(self, option):
        if option == "stop":
            self.start_mining_button.text = "Stop"
            self.start_mining_button.style.background_color = RED
            self.start_mining_button._impl.native.MouseEnter -= self.start_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave -= self.start_mining_button_mouse_leave
            self.start_mining_button.on_press = None

            self.start_mining_button._impl.native.MouseEnter += self.stop_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave += self.stop_mining_button_mouse_leave
            self.start_mining_button.on_press = self.stop_mining_button_click

        elif option == "start":
            self.start_mining_button.text = "Start Mining"
            self.start_mining_button.style.background_color = GREENYELLOW
            self.start_mining_button._impl.native.MouseEnter -= self.stop_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave -= self.stop_mining_button_mouse_leave
            self.start_mining_button.on_press = None

            self.start_mining_button._impl.native.MouseEnter += self.start_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave += self.start_mining_button_mouse_leave
            self.start_mining_button.on_press = self.start_mining_button_click


    def disable_mining_inputs(self):
        self.start_mining_button.style.color = BLACK
        self.start_mining_button.style.background_color = RED
        self.miner_selection.enabled = False
        self.address_selection.enabled = False
        self.pool_selection.enabled = False
        self.pool_region_selection.enabled = False
        self.worker_input.readonly = True

    def enable_mining_inputs(self):
        self.start_mining_button.style.color = BLACK
        self.start_mining_button.style.background_color = GREENYELLOW
        self.miner_selection.enabled = True
        self.address_selection.enabled = True
        self.pool_selection.enabled = True
        self.pool_region_selection.enabled = True
        self.worker_input.readonly = False


    def start_mining_button_mouse_enter(self, sender, event):
        self.start_mining_button.style.color = BLACK
        self.start_mining_button.style.background_color = GREENYELLOW


    def start_mining_button_mouse_leave(self, sender, event):
        self.start_mining_button.style.color = GRAY
        self.start_mining_button.style.background_color = rgb(30,33,36)

    def stop_mining_button_mouse_enter(self, sender, event):
        self.start_mining_button.style.color = BLACK
        self.start_mining_button.style.background_color = RED


    def stop_mining_button_mouse_leave(self, sender, event):
        self.start_mining_button.style.color = GRAY
        self.start_mining_button.style.background_color = rgb(30,33,36)