
import asyncio
import psutil
import subprocess
import re
import aiohttp
from aiohttp_socks import ProxyConnector, ProxyConnectionError
from pathlib import Path

from toga import (
    App, Box, Label, Selection, TextInput,
    ProgressBar, Window, Button, Switch
)
from ..framework import (
    FlatStyle, Os, ToolTip, RightToLeft, WebView,
    Color
)
from toga.style.pack import Pack
from toga.constants import COLUMN, CENTER, ROW
from toga.colors import rgb, GRAY, WHITE, GREENYELLOW, BLACK, RED

from .storage import StorageMessages, StorageAddresses, StorageMobile


class Mining(Box):
    def __init__(self, app:App, main:Window, settings, utils, units, commands, tr, font):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5)
            )
        )

        self.mining_toggle = None
        self.selected_miner = None
        self.selected_address = None
        self.selected_pool = None
        self.selected_server = None
        self.worker_name = None
        self.mining_status = None
        self.pool_api = None
        self.pool_port = None
        self.pool_ssl = None
        self.miner_command = None

        self.app = app
        self.main = main

        self.utils = utils
        self.units = units
        self.commands = commands
        self.settings = settings
        self.tr = tr
        self.font = font

        self.storage = StorageMessages(self.app)
        self.addresses_storage = StorageAddresses(self.app)
        self.mobile_storage = StorageMobile(self.app)
        self.tooltip = ToolTip()

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.tor_enabled = self.settings.tor_network()

        self.miner_label = Label(
            text=self.tr.text("miner_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )
        self.miner_label._impl.native.Font = self.font.get(11, True)

        self.miner_selection = Selection(
            items=[
                {"miner": self.tr.text("miner_selection")},
                {"miner": "MiniZ"},
                {"miner": "Gminer"},
                {"miner": "lolMiner"}
            ],
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 2,
                padding_top = 10
            ),
            accessor="miner",
            on_change=self.verify_miners_apps
        )
        self.miner_selection._impl.native.Font = self.font.get(11, True)
        self.miner_selection._impl.native.FlatStyle = FlatStyle.FLAT

        self.progress_bar = ProgressBar(
            max = 100,
            style=Pack(
                height = 5,
                width = 100,
                padding = self.tr.padding("progress_bar")
            )
        )
        if self.rtl:
            self.progress_bar._impl.native.RightToLeft = RightToLeft.YES
            self.progress_bar._impl.native.RightToLeftLayout = True

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
            text=self.tr.text("address_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )
        self.address_label._impl.native.Font = self.font.get(11, True)
        
        self.address_selection = Selection(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 2,
                padding_top = 10
            ),
            accessor="select_address",
            on_change=self.display_address_balance
        )
        self.address_selection._impl.native.Font = self.font.get(11, True)
        self.address_selection._impl.native.FlatStyle = FlatStyle.FLAT
        self.address_selection._impl.native.DropDownHeight = 150

        self.address_balance = Label(
            text="0.00000000",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )
        self.address_balance._impl.native.Font = self.font.get(11, True)

        self.selection_address_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding=(5,5,0,5),
                height = 55
            )
        )

        self.pool_label = Label(
            text=self.tr.text("pool_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )
        self.pool_label._impl.native.Font = self.font.get(11, True)

        self.pool_selection = Selection(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 1.5,
                padding_top = 10
            ),
            items=[
                {"pool": self.tr.text("pool_selection")}
            ],
            accessor="pool",
            on_change=self.update_server_selection
        )
        self.pool_selection._impl.native.Font = self.font.get(11, True)
        self.pool_selection._impl.native.FlatStyle = FlatStyle.FLAT

        self.pool_region_selection = Selection(
            enabled=False,
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (10,10,0,15)
            ),
            accessor="region",
            on_change=self.update_region_server
        )
        self.pool_region_selection._impl.native.Font = self.font.get(11, True)
        self.pool_region_selection._impl.native.FlatStyle = FlatStyle.FLAT

        self.ssl_switch = Switch(
            text=" SSL",
            value=False,
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 0.5,
                padding = (13,10,0,15)
            ),
            enabled=False
        )
        self.ssl_switch._impl.native.Font = self.font.get(11, True)
        self.tooltip.insert(self.ssl_switch._impl.native, self.tr.tooltip("ssl_switch"))
        if self.rtl:
            self.ssl_switch._impl.native.RightToLeft = RightToLeft.YES

        self.selection_pool_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding=(5,5,0,5),
                height = 55
            )
        )

        self.worker_label = Label(
            text=self.tr.text("worker_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 2,
                padding_top = 12
            )
        )
        self.worker_label._impl.native.Font = self.font.get(11, True)

        self.worker_input = TextInput(
            placeholder=self.tr.text("worker_input"),
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                flex = 2,
                padding_top = 10
            ),
            on_change=self.update_worker_name
        )
        self.worker_input._impl.native.Font = self.font.get(11, True)
        if self.rtl:
            self.worker_input._impl.native.RightToLeft = RightToLeft.YES

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

        html_path = Path(__file__).parent / "html" / "mining.html"
        self.miner_stats = WebView(
            app=self.app,
            content=html_path,
            background_color = Color.rgb(40,43,48)
        )

        self.stats_box = Box(
           style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1
            ) 
        )
        self.stats_box._impl.native.Controls.Add(self.miner_stats.control)

        self.mining_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                alignment= self.tr.align("mining_box"),
                flex = 1
            )
        )

        self.start_mining_button = Button(
            text=self.tr.text("start_mining_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 150,
                alignment= CENTER,
                padding = self.tr.padding("start_mining_button")
            ),
            on_press=self.start_mining_button_click
        )
        self.start_mining_button._impl.native.Font = self.font.get(self.tr.size("start_mining_button"), True)
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

        self.add(
            self.selection_miner_box,
            self.selection_address_box,
            self.selection_pool_box,
            self.worker_box,
            self.stats_box,
            self.start_mining_box
        )
        if self.rtl:
            self.selection_miner_box.add(
                self.setup_miner_box,
                self.miner_selection,
                self.miner_label
            )
            self.selection_address_box.add(
                self.address_balance,
                self.address_selection,
                self.address_label
            )
            self.selection_pool_box.add(
                self.ssl_switch,
                self.pool_region_selection,
                self.pool_selection,
                self.pool_label
            )
            self.worker_box.add(
                self.empty_box,
                self.worker_input,
                self.worker_label
            )
            self.start_mining_box.add(
                self.start_mining_button,
                self.mining_box
            )
        else:
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
                self.pool_region_selection,
                self.ssl_switch
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


    def insert_widgets(self):
        if not self.mining_toggle:
            self.mining_toggle = True
            self.app.loop.create_task(self.update_mining_options())



    async def update_mining_options(self):
        addresses = self.addresses_storage.get_addresses()
        self.address_selection.items.clear()
        self.address_selection.items = addresses
        pools_list = self.get_pools_list()
        for pool in pools_list:
            self.pool_selection.items.insert(1, pool)
        
        recent_mining_options = self.settings.load_mining_options()
        if recent_mining_options:
            miner, mining_address, pool_server, pool_region, ssl, worker = recent_mining_options
            if miner:
                self.miner_selection.value = self.miner_selection.items.find(miner)
                self.address_selection.value = self.address_selection.items.find(mining_address)
                self.pool_selection.value = self.pool_selection.items.find(pool_server)
                self.pool_region_selection.value = self.pool_region_selection.items.find(pool_region)
                self.ssl_switch.value = ssl
                self.worker_input.value = worker


    async def verify_miners_apps(self, selection):
        self.selected_miner = self.miner_selection.value.miner
        if not self.selected_miner:
            return
        if self.selected_miner == self.tr.text("miner_selection"):
            return
        miner_path, url, zip_file = self.utils.get_miner_path(self.selected_miner)
        if not miner_path:
            self.miner_selection.enabled = False
            self.setup_miner_box.add(
                self.progress_bar
            )
            await self.utils.fetch_miner(
                self.miner_selection, self.setup_miner_box, self.progress_bar, self.selected_miner, zip_file, url, self.tor_enabled
            )


    async def display_address_balance(self, selection):
        self.selected_address = self.address_selection.value.select_address
        balance = self.addresses_storage.get_address_balance(self.selected_address)
        if float(balance) <= 0:
            self.address_balance.style.color = GRAY
        else:
            self.address_balance.style.color = WHITE
        format_balance = self.units.format_balance(float(balance))
        self.address_balance.text = format_balance
    

    def update_server_selection(self, selection):
        self.selected_pool = self.pool_selection.value.pool
        if not self.selected_pool:
            return
        
        pools_data = self.utils.get_pools_data()
        if self.selected_pool in pools_data:
            self.pool_api = pools_data[self.selected_pool]["api"]
            self.pool_port = pools_data[self.selected_pool]["port"]
            self.pool_ssl = pools_data[self.selected_pool]["ssl"]
            pool_rergion_items = pools_data[self.selected_pool]["regions"]
            self.pool_region_selection.items = pool_rergion_items
            self.pool_region_selection.enabled = True
        else:
            self.pool_region_selection.items.clear()
            self.pool_region_selection.enabled = False
        

    def get_pools_list(self):
        pools_data = self.utils.get_pools_data()
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
        if self.miner_selection.enabled is False:
            return
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
                log_file = Os.Path.Combine(str(self.app.paths.logs), 'miniZ.log')
                self.miner_command = f'{miner_path} --url '
                if self.ssl_switch.value is True:
                    self.miner_command += 'ssl://'
                    self.pool_port = self.pool_ssl
                self.miner_command += f'{self.selected_address}.{self.worker_name}@{self.selected_server}:{self.pool_port}  --logfile {log_file}'
                if self.selected_pool == "Zpool":
                    self.miner_command += ' --pass c=BTCZ,zap=BTCZ --pers auto'
                else:
                    self.miner_command += ' --pass x --par 144,5 --pers BitcoinZ'
                if self.tor_enabled:
                    if not self.selected_pool == "2Mars":
                        socks_port = self.get_socks_port()
                        self.miner_command += f' --socks 127.0.0.1:{socks_port}'
                    
            elif self.selected_miner == "Gminer":
                log_file = Os.Path.Combine(str(self.app.paths.logs), 'Gminer.log')
                self.miner_command = f'{miner_path} --server {self.selected_server} --logfile {log_file} --user {self.selected_address}'
                if self.ssl_switch.value is True:
                    self.miner_command += ' --ssl 1'
                    self.pool_port = self.pool_ssl
                if self.selected_pool == "Zpool":
                    self.miner_command += f'.{self.worker_name} --pass c=BTCZ,zap=BTCZ --algo 144_5 --pers auto'
                else:
                    self.miner_command += f'.{self.worker_name} --pass x --algo 144_5 --pers BitcoinZ'
                self.miner_command += f' --port {self.pool_port}'
                if self.tor_enabled:
                    if not self.selected_pool == "2Mars":
                        socks_port = self.get_socks_port()
                        self.miner_command += f' --proxy 127.0.0.1:{socks_port}'

            elif self.selected_miner == "lolMiner":
                log_file = Os.Path.Combine(str(self.app.paths.logs), 'lolMiner.log')
                self.miner_command = f'{miner_path} --pool '
                if self.ssl_switch.value is True:
                    self.miner_command += 'ssl://'
                    self.pool_port = self.pool_ssl
                self.miner_command += f'{self.selected_server}:{self.pool_port} --log "on" --logfile {log_file} --user {self.selected_address}'
                if self.selected_pool == "Zpool":
                    self.miner_command += f'.{self.worker_name} --pass c=BTCZ,zap=BTCZ --pers BitcoinZ --algo EQUI144_5'
                else:
                    self.miner_command += f'.{self.worker_name} --pass x --pers BitcoinZ --algo EQUI144_5'
                if self.tor_enabled:
                    if not self.selected_pool == "2Mars":
                        socks_port = self.get_socks_port()
                        self.miner_command += f' --socks5 127.0.0.1:{socks_port}'

            self.disable_mining_inputs()
            self.app.loop.create_task(self.start_mining_command(self.app))
            self.settings.save_mining_options(
                self.selected_miner,
                self.selected_address,
                self.selected_pool,
                self.pool_region_selection.value.region,
                self.ssl_switch.value,
                self.worker_name
            )
            self.mining_status = True
            self.fetch_stats_task = self.app.loop.create_task(self.fetch_miner_stats())


    async def start_mining_command(self, app):
        self.update_mining_button("stop")
        self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"startAnimation();")
        command = [self.miner_command]
        app.console.info_log(f"Starting mining...")
        app.console.mining_log(command)
        try:
            self.process = await asyncio.create_subprocess_shell(
                *command,
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
                    if cleaned_line.strip():
                        app.console.mining_log(cleaned_line)
                else:
                    break
            await self.process.wait()
            remaining_stdout = await self.process.stdout.read()
            remaining_stderr = await self.process.stderr.read()
            if remaining_stdout:
                app.console.mining_log(remaining_stdout.decode().strip())
            if remaining_stderr:
                app.console.mining_log(remaining_stderr.decode().strip())

        except Exception as e:
            app.console.mining_log(f"{e}")
            



    async def fetch_miner_stats(self):
        self.reset_miner_notify_stats()
        if not self.pool_api:
            return
        api = self.pool_api + self.selected_address
        solutions_value = None
        estimated_value = None
        estimated_earn_value = None
        self.app.console.info_log(f"Fetch miner stats : {api}")
        if self.tor_enabled:
            socks_port = self.get_socks_port()
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
        else:
            connector = None
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession(connector=connector) as session:
            while True:
                estimated_24h = 0
                converted_rate = 0.0
                try:
                    async with session.get(api, headers=headers) as response:
                        response.raise_for_status()
                        mining_data = await response.json()
                        if mining_data:
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
                                            converted_rate = self.units.hash_to_solutions(hashrate)
                                            solutions_value = f"{converted_rate:.2f} Sol/s"
                                            
                                            estimated_24h = await self.units.estimated_earn(24, hashrate)
                                            estimated_value = int(estimated_24h)
                            else:
                                total_hashrates = mining_data.get("total_hashrates", [])
                                if total_hashrates:
                                    for hashrate in total_hashrates:
                                        for algo, rate in hashrate.items():
                                            solutions_value = f"{rate:.2f}"
                                            converted_rate = self.units.solution_to_hash(rate)
                                            estimated_24h = await self.units.estimated_earn(24, converted_rate)
                                            estimated_value = int(estimated_24h)
                                            converted_rate = rate
                                else:
                                    rate = sum(float(miner.get("hashrate", "0").replace("h/s", "").strip()) for miner in mining_data.get("miners", []))
                                    if rate:
                                        solutions_value = f"{rate:.2f} Sol/s"
                                        converted_rate = self.units.solution_to_hash(rate)
                                        estimated_24h = await self.units.estimated_earn(24, converted_rate)
                                        estimated_value = int(estimated_24h)
                                        converted_rate = rate

                            btcz_price = self.settings.price()
                            if btcz_price:
                                estimated_earn = float(btcz_price) * float(estimated_24h)
                                estimated_earn_value = f"{self.units.format_price(estimated_earn)} {self.settings.symbol()}"

                            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setTotalShares('{total_share:.2f}');")
                            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setBalance('{self.units.format_balance(balance)}');")
                            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setImmatureBalance('{self.units.format_balance(immature_bal)}');")
                            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setPaidBalance('{self.units.format_balance(paid)}');")
                            if solutions_value:
                                self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setHashrate('{solutions_value}');")
                            if estimated_value:
                                self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setEstimatedBTCZ('{estimated_value}');")
                            if estimated_earn_value:
                                self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setEstimatedCurrency('{estimated_earn_value}');")

                            solutions_text = self.tr.text("notifymining_solutions")
                            balance_text = self.tr.text("notifymining_balance")
                            immature_text = self.tr.text("notifymining_immature")
                            paid_text = self.tr.text("notifymining_paid")
                            self.main.notifymining.text = f"{solutions_text} {converted_rate:.2f} Sol/s"
                            self.main.notifymining.solutions.text = f"⛏️ {solutions_text} {converted_rate:.2f} Sol/s"
                            self.main.notifymining.balance.text = f"💰 {balance_text} {self.units.format_balance(balance)}"
                            self.main.notifymining.immature.text = f"🔃 {immature_text} {self.units.format_balance(immature_bal)}"
                            self.main.notifymining.paid.text = f"💸 {paid_text} {self.units.format_balance(paid)}"

                            self.store_mining_stats(
                                self.selected_miner, self.selected_address, self.selected_pool,
                                self.pool_region_selection.value.region,
                                self.worker_name, total_share, balance, immature_bal,
                                paid, converted_rate, estimated_24h
                            )

                except Exception as e:
                    self.app.console.error_log(f"{e}")
                    self.fetch_stats_task = self.app.loop.create_task(self.fetch_miner_stats())
                    return

                await asyncio.sleep(60)


    def store_mining_stats(self, miner, address, pool, region, worker, shares, balance, immature, paid, solutions, reward):
        mining_stats = self.mobile_storage.get_mining_stats()
        if mining_stats:
            self.mobile_storage.update_mining_stats(
                miner, address, pool, region, worker, shares, balance, immature, paid, solutions, reward
            )
        else:
            self.mobile_storage.insert_mining_stats(
                miner, address, pool, region, worker, shares, balance, immature, paid, solutions, reward
            )


    def reset_miner_notify_stats(self):
        self.main.notifymining.solutions.text = f"⛏️ Solutions : 0.0 Sol/s"
        self.main.notifymining.balance.text = f"💰 Balance : 0.0000000"
        self.main.notifymining.immature.text = f"🔃 Immature : 0.0000000"
        self.main.notifymining.paid.text = f"💸 Paid : 0.0000000"


    def reload_addresses(self):
        if self.mining_toggle:
            addresses = self.addresses_storage.get_addresses()
            self.address_selection.items.clear()
            self.address_selection.items = addresses


    async def stop_mining_button_click(self, button):
        await self.stop_mining()
        

    async def stop_mining(self):
        if self.selected_miner == "MiniZ":
            process_name =  "miniZ.exe"
        elif self.selected_miner == "Gminer":
            process_name = "miner.exe"
        elif self.selected_miner == "lolMiner":
            process_name = "lolMiner.exe"
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == process_name:
                    proc.kill()
            self.process.terminate()
            await asyncio.sleep(0.5)
            self.app.console.info_log(self.tr.text("miner_stopped"))
            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setTotalShares('--');")
            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setBalance('');")
            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setImmatureBalance('');")
            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setPaidBalance('');")
            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setHashrate('');")
            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setEstimatedBTCZ('');")
            self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"setEstimatedCurrency('');")
        except Exception as e:
            self.app.console.error_log(f"Exception occurred while killing miner process: {e}")

        self.update_mining_button("start")
        self.miner_stats.control.CoreWebView2.ExecuteScriptAsync(f"stopAnimation();")
        self.enable_mining_inputs()
        self.mining_status = None
        self.miner_command = None

        if self.fetch_stats_task and not self.fetch_stats_task.done():
            self.app.console.info_log(f"Cancel miner stats task...")
            self.fetch_stats_task.cancel()
            try:
                await self.fetch_stats_task
            except asyncio.CancelledError:
                self.app.console.info_log(f"Task was cancelled")


    def update_mining_button(self, option):
        if option == "stop":
            self.start_mining_button.text = self.tr.text("stop_mining_button")
            self.start_mining_button._impl.native.MouseEnter -= self.start_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave -= self.start_mining_button_mouse_leave
            self.start_mining_button.on_press = None

            self.start_mining_button._impl.native.MouseEnter += self.stop_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave += self.stop_mining_button_mouse_leave
            self.start_mining_button.on_press = self.stop_mining_button_click

        elif option == "start":
            self.start_mining_button.text = self.tr.text("start_mining_button")
            self.start_mining_button._impl.native.MouseEnter -= self.stop_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave -= self.stop_mining_button_mouse_leave
            self.start_mining_button.on_press = None

            self.start_mining_button._impl.native.MouseEnter += self.start_mining_button_mouse_enter
            self.start_mining_button._impl.native.MouseLeave += self.start_mining_button_mouse_leave
            self.start_mining_button.on_press = self.start_mining_button_click

        self.start_mining_button.style.color = GRAY
        self.start_mining_button.style.background_color = rgb(30,33,36)


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


    def get_socks_port(self):
        torrc = self.utils.read_torrc()
        socks_port = torrc.get("SocksPort")
        return socks_port


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