
import asyncio
import json
from datetime import datetime, timezone
import aiohttp
from aiohttp_socks import ProxyConnector, ProxyConnectionError, ProxyError

from toga import (
    App, Window, ScrollContainer, Box,
    Label, Divider, Button, TextInput, Switch
)
from ..framework import (
    ToolTip, FlatStyle, Forms, Color,
    Command, ClipBoard, Os, Sys, Drawing
)
from toga.constants import COLUMN, ROW, CENTER, BOLD, Direction
from toga.style.pack import Pack
from toga.colors import (
    rgb, WHITE, GRAY, RED, GREENYELLOW, BLACK
)



class AddNode(Window):
    def __init__(self, main:Window, utils, commands, tr, monda_font):
        super().__init__(
            resizable=False
        )

        self.main = main
        
        self.utils = utils
        self.commands = commands
        self.tr = tr
        self.monda_font = monda_font

        self.title = self.tr.title("addnode_window")
        self.size = (550, 120)
        self.position = self.utils.windows_screen_center(self.size)
        self._impl.native.ControlBox = False

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.address_input = TextInput(
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 3,
                padding_left = 10
            )
        )

        self.add_button = Button(
            text=self.tr.text("add_button"),
            style=Pack(
                color= GRAY,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (0,10,0,10)
            ),
            on_press=self.add_button_click
        )
        self.add_button._impl.native.Font = self.monda_font.get(9, True)
        self.add_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.add_button._impl.native.MouseEnter += self.add_button_mouse_enter
        self.add_button._impl.native.MouseLeave += self.add_button_mouse_leave

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (10,0,10,0)
            )
        )

        self.cancel_button = Button(
            text=self.tr.text("cancel_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_import_key
        )
        self.cancel_button._impl.native.Font = self.monda_font.get(9, True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.input_box,
            self.cancel_button
        )
        self.input_box.add(
            self.address_input,
            self.add_button
        )


    async def add_button_click(self, button):
        def on_result(widget, result):
            if result is None:
                self.close()
                self.app.current_window = self.main
        node_address = self.address_input.value.strip()
        if not node_address:
            self.error_dialog(
                title=self.tr.title("missingnode_dialog"),
                message=self.tr.message("missingnode_dialog")
            )
            return
        self.cancel_button.enabled = False
        self.add_button.enabled = False
        if 'onion' in node_address:
            torrc = self.utils.read_torrc()
            socks_port = torrc.get("SocksPort")
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:{socks_port}')
            try:
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(f"http://{node_address}", timeout=10) as response:
                        await response.text()
            except (ProxyConnectionError, ProxyError) as e:
                self.error_dialog(
                    title=self.tr.title("proxyerror_dialog"),
                    message=self.tr.message("proxyerror_dialog")
                )
                self.cancel_button.enabled = True
                self.add_button.enabled = True
                return
            except aiohttp.ServerDisconnectedError:
                pass
        else:
            try:
                host, port = node_address.split(":")
                port = int(port)
            except ValueError:
                self.error_dialog(
                    title=self.tr.title("invalidnode_dialog"),
                    message=self.tr.message("invalidnode_dialog")
                )
                self.cancel_button.enabled = True
                self.add_button.enabled = True
                return
            try:
                reader, writer = await asyncio.open_connection(host, port)
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                message = self.tr.message("connectionfailed_dilag")
                self.error_dialog(
                    title=self.tr.title("connectionfailed_dilag"),
                    message=f"{message} {node_address}."
                )
                self.cancel_button.enabled = True
                self.add_button.enabled = True
                return
        addnodes = []
        config_file_path = self.utils.get_config_path()
        with open(config_file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("addnode="):
                    addnodes.append(line.split("=", 1)[1].strip())
        if node_address in addnodes:
            self.error_dialog(
                title=self.tr.title("duplicatenode_dialog"),
                message=self.tr.message("duplicatenode_dialog")
            )
            return
        with open(config_file_path, 'a') as file:
            file.write(f"\naddnode={node_address}")

        await self.commands.addNode(node_address)
        message = self.tr.message("addednode_dialog")
        self.info_dialog(
            title=self.tr.title("addednode_dialog"),
            message=f"{node_address} {message}",
            on_result=on_result
        )

            

    def add_button_mouse_enter(self, sender, event):
        self.add_button.style.color = BLACK
        self.add_button.style.background_color = GREENYELLOW

    def add_button_mouse_leave(self, sender, event):
        self.add_button.style.color = GRAY
        self.add_button.style.background_color = rgb(30,33,36)

    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)

    def close_import_key(self, button):
        self.close()
        self.app.current_window = self.main



class TorConfig(Window):
    def __init__(self, settings, utils, commands, tr, monda_font, main:Window = None, startup:Window = None):
        super().__init__(
            resizable=False
        )

        self.main = main
        self.startup = startup

        self.utils = utils
        self.commands = commands
        self.settings = settings
        self.tr = tr

        self.tooltip = ToolTip()
        self.app_data = self.app.paths.data

        if self.main:
            self.size = (350, 325)
        if self.startup:
            self.size = (350, 280)
        self.title = self.tr.title("torconfig_window")
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self._impl.native.ControlBox = False

        self.monda_font = monda_font

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1,
                alignment = CENTER
            )
        )

        self.enabled_label = Label(
            text=self.tr.text("enabled_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER
            )
        )
        self.enabled_label._impl.native.Font = self.monda_font.get(11, True)

        self.socks_label = Label(
            text=self.tr.text("socks_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                padding_top = 16
            )
        )
        self.socks_label._impl.native.Font = self.monda_font.get(11, True)

        self.onlyonion_label = Label(
            text=self.tr.text("onlyonion_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                padding_top = 16
            )
        )
        self.onlyonion_label._impl.native.Font = self.monda_font.get(11, True)

        self.service_label = Label(
            text=self.tr.text("service_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                padding_top = 16
            )
        )
        self.service_label._impl.native.Font = self.monda_font.get(11, True)

        self.service_port_label = Label(
            text=self.tr.text("service_port_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                padding_top = 19
            )
        )
        self.service_port_label._impl.native.Font = self.monda_font.get(11, True)

        self.hostname_label = Label(
            text=self.tr.text("hostname_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                padding_top = 19
            )
        )
        self.hostname_label._impl.native.Font = self.monda_font.get(11, True)

        self.labels_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding_top = 10
            )
        )

        self.enabled_switch = Switch(
            text="",
            style=Pack(
                background_color = rgb(30,33,36),
                padding = (5,0,0,65)
            )
        )
        self.tooltip.insert(self.enabled_switch._impl.native, self.tr.tooltip("enabled_label"))

        self.socks_input = TextInput(
            placeholder="Default 9050",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                padding_top = 15
            )
        )
        self.socks_input._impl.native.Font = self.monda_font.get(11, True)
        self.tooltip.insert(self.socks_input._impl.native, self.tr.tooltip("socks_label"))

        self.onlyonion_switch = Switch(
            text="",
            style=Pack(
                background_color = rgb(30,33,36),
                padding = (15,0,0,65)
            )
        )
        self.tooltip.insert(self.onlyonion_switch._impl.native, self.tr.tooltip("onlyonion_label"))

        self.service_switch = Switch(
            text="",
            style=Pack(
                background_color = rgb(30,33,36),
                padding = (23,0,0,65)
            ),
            on_change=self.update_service_input
        )
        self.tooltip.insert(self.service_switch._impl.native, self.tr.tooltip("service_label"))

        self.service_input = TextInput(
            placeholder="Default 1989",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                padding_top = 17
            )
        )
        self.service_input.enabled = False
        self.service_input._impl.native.Font = self.monda_font.get(11, True)
        self.tooltip.insert(self.service_input._impl.native, self.tr.tooltip("service_port_label"))

        self.hostname_input = TextInput(
            placeholder="None",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                padding_top = 10
            ),
            readonly=True
        )
        self.hostname_input._impl.native.Font = self.monda_font.get(11)

        self.inputs_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (10,30,0,0)
            )
        )

        self.options_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (10,5,10,5)
            )
        )

        self.cancel_button = Button(
            text=self.tr.text("cancel_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_tor_config
        )
        self.cancel_button._impl.native.Font = self.monda_font.get(9, True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.save_button = Button(
            text=self.tr.text("save_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (0,0,10,20),
                width = 100
            ),
            on_press=self.save_options
        )
        self.save_button._impl.native.Font = self.monda_font.get(9, True)
        self.save_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.save_button._impl.native.MouseEnter += self.save_button_mouse_enter
        self.save_button._impl.native.MouseLeave += self.save_button_mouse_leave

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER,
                background_color = rgb(40,43,48)
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.options_box,
            self.buttons_box
        )
        self.options_box.add(
            self.labels_box,
            self.inputs_box
        )
        self.labels_box.add(
            self.enabled_label,
            self.socks_label,
            self.onlyonion_label,
            self.service_label,
            self.service_port_label
        )
        if self.main:
            self.labels_box.add(
                self.hostname_label
            )
        self.inputs_box.add(
            self.enabled_switch,
            self.socks_input,
            self.onlyonion_switch,
            self.service_switch,
            self.service_input
        )
        if self.main:
            self.inputs_box.add(
                self.hostname_input
            )
        self.buttons_box.add(
            self.cancel_button,
            self.save_button
        )
        self.load_torrc_config()


    def load_torrc_config(self):
        torrc = self.utils.read_torrc()
        if torrc:
            socks_port = torrc.get("SocksPort", "")
            tor_service = torrc.get("HiddenServiceDir", "")
            if tor_service:
                self.service_switch.value = True
                self.service_input.enabled = True
                service_port_line = torrc.get("HiddenServicePort", "")
                if service_port_line:
                    service_port = service_port_line.split()[0]
                else:
                    service_port = ""
                self.service_input.value = service_port

            self.socks_input.value = socks_port

        if self.main:
            hostname = self.utils.get_onion_hostname()
            if hostname:
                self.hostname_input.value = f"{hostname}:{service_port}"

        if self.startup:
            self.enabled_switch.value = True
            self.onlyonion_switch.value = False
        else:
            self.enabled_switch.value = self.settings.tor_network()
            self.onlyonion_switch.value = self.settings.only_onion()



    async def save_options(self, button):
        if self.enabled_switch.value is False:
            self.settings.update_settings("tor_network", False)
            self.close()
            if self.startup:
                if self.startup.node_status:
                    await self.startup.open_main_menu()
                else:
                    await self.startup.verify_binary_files()
            return
                
        if not self.socks_input.value:
            socks_port = "9050"
        else:
            socks_port = self.socks_input.value.strip()
        if self.onlyonion_switch.value is True:
            self.settings.update_settings("only_onion", True)
        else:
            self.settings.update_settings("only_onion", False)
        if self.service_switch.value is True:
            tor_service = Os.Path.Combine(str(self.app_data), "tor_service")
        else:
            tor_service = None
        if tor_service and not self.service_input.value:
            service_port = "1989"
        else:
            service_port = self.service_input.value.strip()
        self.settings.update_settings("tor_network", True)
        self.utils.create_torrc(socks_port, tor_service, service_port)
        self.close()

        if self.startup:
            self.app.current_window = self.startup
            self.startup.tor_icon.image = "images/tor_on.png"
            self.startup.network_status.style.color = rgb(114,137,218)
            self.startup.network_status.text = self.tr.text("tor_enabled")
            if self.startup.startup.node_status:
                await self.commands.stopNode()
                await asyncio.sleep(1)
            await self.startup.startup.verify_tor_files()
        else:
            self.app.current_window = self.main
        


    def update_service_input(self, switch):
        if switch.value is True:
            self.service_input.enabled = True
        else:
            self.service_input.value = ""
            self.service_input.enabled = False


    def save_button_mouse_enter(self, sender, event):
        self.save_button.style.color = BLACK
        self.save_button.style.background_color = GREENYELLOW

    def save_button_mouse_leave(self, sender, event):
        self.save_button.style.color = GRAY
        self.save_button.style.background_color = rgb(30,33,36)


    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)


    async def close_tor_config(self, button):
        self.close()
        if self.startup:
            self.settings.update_settings("tor_network", False)
            if self.startup.node_status:
                await self.startup.open_main_menu()
            else:
                await self.startup.verify_binary_files()




class NodeInfo(Window):
    def __init__(self, node, settings, utils, units, tr, monda_font):
        super().__init__(
            resizable=False
        )

        self.node = node

        self.utils = utils
        self.units = units
        self.settings = settings
        self.tr = tr
        self.monda_font = monda_font

        self.tooltip = ToolTip()

        self.size = (350, 510)
        self.title = self.tr.title("nodeinfo_window")
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self._impl.native.ControlBox = False

        self.address = self.node.get('addr')
        self.address_local = self.node.get('addrlocal')
        address = self.utils.shorten_address(self.address)
        address_local = self.utils.shorten_address(self.address_local)
        subver = self.node.get('subver')
        clean_subversion = subver.strip('/')
        conntime = self.node.get('conntime')
        conn_time = datetime.fromtimestamp(conntime, tz=timezone.utc)
        conn_duration = self.units.create_timer(conn_time)

        node_data = {
            "Node ID": self.node.get('id'),
            "Address": address,
            "Local Address": address_local,
            "Services": self.node.get('services'),
            "Last Sent": datetime.fromtimestamp(self.node.get('lastsend')).strftime("%Y-%m-%d %H:%M:%S"),
            "Last Received": datetime.fromtimestamp(self.node.get('lastrecv')).strftime("%Y-%m-%d %H:%M:%S"),
            "Bytes Sent": self.units.format_bytes(self.node.get('bytessent')),
            "Bytes Received": self.units.format_bytes(self.node.get('bytesrecv')),
            "Connection Time": conn_duration,
            "Time Offset": self.node.get('timeoffset'),
            "Ping Time": f"{int(self.node.get('pingtime') * 1000)} ms",
            "Version": self.node.get('version'),
            "Subversion": clean_subversion,
            "Inbound": self.node.get('inbound'),
            "Starting Height": self.node.get('startingheight'),
            "Ban Score": self.node.get('banscore'),
            "Synced Headers": self.node.get('synced_headers'),
            "Synced Blocks": self.node.get('synced_blocks'),
            "Whitelisted": self.node.get('whitelisted')
        }

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1,
                alignment = CENTER
            )
        )

        self.close_button = Button(
            text="Close",
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_top = 10,
                width = 100
            ),
            on_press=self.close_node_info
        )
        self.close_button._impl.native.Font = self.monda_font.get(9, True)
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

        self.content = self.main_box

        for label_text, value_text in node_data.items():
            info_label = Label(
                f"{label_text} : {value_text}",
                style=Pack(
                    color = WHITE,
                    background_color = rgb(40,43,48),
                    padding = (1,0,0,5)
                )
            )
            info_label._impl.native.Font = self.monda_font.get(10)
            if label_text == "Address":
                self.tooltip.insert(info_label._impl.native, self.address)
            if label_text == "Local Address":
                self.tooltip.insert(info_label._impl.native, self.address_local)
                
            self.main_box.add(
                info_label
            )

        self.main_box.add(
            self.close_button
        )


    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)


    def close_node_info(self, button):
        self.close()



class Node(Box):
    def __init__(self, app:App, peer_window:Window, node, settings, utils, units, commands, tr, monda_font):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 40,
                padding_top = 5
            )
        )
        self.app = app
        self.peer_window = peer_window
        self.node = node

        self.utils = utils
        self.units = units
        self.commands = commands
        self.settings = settings
        self.tr = tr
        self.tooltip = ToolTip()
        self.clipboard = ClipBoard()

        self.monda_font = monda_font

        self.address = self.node.get('addr')
        self.address_local = self.node.get('addrlocal')
        address = self.utils.shorten_address(self.address)
        address_local = self.utils.shorten_address(self.address_local)
        bytessent = self.node.get('bytessent')
        bytesrecv = self.node.get('bytesrecv')
        subver = self.node.get('subver')
        clean_subversion = subver.strip('/')
        conntime = self.node.get('conntime')
        conn_time = datetime.fromtimestamp(conntime, tz=timezone.utc)
        conn_duration = self.units.create_timer(conn_time)


        self.node_address = Label(
            text=address,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                flex = 1.5,
                padding_top = 10
            )
        )
        self.node_address._impl.native.Font = self.monda_font.get(9, True)
        self.tooltip.insert(self.node_address._impl.native, self.address)

        self.node_address_local = Label(
            text=address_local,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                flex = 1.5,
                padding_top = 10
            )
        )
        self.node_address_local._impl.native.Font = self.monda_font.get(9, True)
        self.tooltip.insert(self.node_address_local._impl.native, self.address_local)

        self.node_sent = Label(
            text=self.units.format_bytes(bytessent),
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_sent._impl.native.Font = self.monda_font.get(9)

        self.node_receive = Label(
            text=self.units.format_bytes(bytesrecv),
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_receive._impl.native.Font = self.monda_font.get(9)

        self.node_subversion = Label(
            text=clean_subversion,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_subversion._impl.native.Font = self.monda_font.get(9, True)

        self.node_conntime= Label(
            text=conn_duration,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_conntime._impl.native.Font = self.monda_font.get(9, True)

        self.add(
            self.node_address,
            self.node_address_local,
            self.node_sent,
            self.node_receive,
            self.node_subversion,
            self.node_conntime
        )
        self.insert_node_menustrip()


    def insert_node_menustrip(self):
        context_menu = Forms.ContextMenuStrip()
        self.node_info_cmd = Command(
            title=self.tr.text("node_info_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.node_info_cmd_mouse_enter,
            mouse_leave=self.node_info_cmd_mouse_leave,
            action=self.show_node_info,
            icon="images/about_i.ico"
        )
        self.copy_node_cmd = Command(
            title=self.tr.text("copy_node_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.copy_node_cmd_mouse_enter,
            mouse_leave=self.copy_node_cmd_mouse_leave,
            action=self.copy_node_address,
            icon="images/copy_i.ico"
        )
        self.remove_node_cmd = Command(
            title=self.tr.text("remove_node_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.remove_node_cmd_mouse_enter,
            mouse_leave=self.remove_node_cmd_mouse_leave,
            action=self.remove_node_from_config,
            icon="images/remove_node_i.ico"
        )
        commands = [
            self.node_info_cmd,
            self.copy_node_cmd,
            self.remove_node_cmd
        ]
        for command in commands:
            context_menu.Items.Add(command)
        self._impl.native.ContextMenuStrip = context_menu
        self.node_address._impl.native.ContextMenuStrip = context_menu
        self.node_address_local._impl.native.ContextMenuStrip = context_menu
        self.node_sent._impl.native.ContextMenuStrip = context_menu
        self.node_receive._impl.native.ContextMenuStrip = context_menu
        self.node_subversion._impl.native.ContextMenuStrip = context_menu


    def show_node_info(self):
        self.node_info = NodeInfo(
            self.node, self.settings, self.utils, self.units, self.tr, self.monda_font
        )
        self.node_info._impl.native.ShowDialog(self.peer_window._impl.native)


    def copy_node_address(self):
        self.clipboard.copy(self.address)
        self.peer_window.info_dialog(
            title=self.tr.title("copynode_dilog"),
            message=self.tr.message("copynode_dilog")
        )


    def remove_node_from_config(self):
        config_file_path = self.utils.get_config_path()
        with open(config_file_path, 'r') as file:
            lines = file.readlines()
        update_lines = []
        for line in lines:
            if line.startswith('addnode='):
                _, value = line.split('=', 1)
                value = value.strip()
                if value != self.address:
                    update_lines.append(line)
            else:
                update_lines.append(line)
        with open(config_file_path, 'w') as file:
            file.writelines(update_lines)
        self.app.add_background_task(self.remove_node)
        
    
    async def remove_node(self, widget):
        await self.commands.disconnectNode(self.address)
        await self.commands.removeNode(self.address)
        message = self.tr.message("removenode_dialog")
        self.peer_window.info_dialog(
            title=self.tr.title("removenode_dialog"),
            message=f"{self.address} {message}"
        )
        
    
    def node_info_cmd_mouse_enter(self):
        self.node_info_cmd.icon = "images/about_a.ico"
        self.node_info_cmd.color = Color.BLACK

    def node_info_cmd_mouse_leave(self):
        self.node_info_cmd.icon = "images/about_i.ico"
        self.node_info_cmd.color = Color.WHITE
    
    def copy_node_cmd_mouse_enter(self):
        self.copy_node_cmd.icon = "images/copy_a.ico"
        self.copy_node_cmd.color = Color.BLACK

    def copy_node_cmd_mouse_leave(self):
        self.copy_node_cmd.icon = "images/copy_i.ico"
        self.copy_node_cmd.color = Color.WHITE    
    
    def remove_node_cmd_mouse_enter(self):
        self.remove_node_cmd.icon = "images/remove_node_a.ico"
        self.remove_node_cmd.color = Color.BLACK

    def remove_node_cmd_mouse_leave(self):
        self.remove_node_cmd.icon = "images/remove_node_i.ico"
        self.remove_node_cmd.color = Color.WHITE




class Peer(Window):
    def __init__(self, main:Window, settings, utils, units, commands, tr, monda_font):
        super().__init__()

        self.peers_list = []
        self.node_map = {}

        self.main = main

        self.commands = commands
        self.utils = utils
        self.units = units
        self.settings = settings
        self.tr = tr
        self.monda_font = monda_font

        self.tooltip = ToolTip()

        self.title = self.tr.title("peer_window")
        self.size = (900,607)
        self._impl.native.Opacity = self.main._impl.native.Opacity
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self.on_close = self.close_peers_window
        self._impl.native.Resize += self._handle_on_resize

        self.main_scroll = ScrollContainer(
            style=Pack(
                background_color = rgb(30,33,36)
            )
        )

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.titles_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                height = 40
            )
        )
        self.address_title = Label(
            text=self.tr.text("address_title"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1.5,
                padding_top = 10
            )
        )
        self.address_title._impl.native.Font = self.monda_font.get(10, True)

        self.address_local_title = Label(
            text=self.tr.text("address_local_title"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1.5,
                padding_top = 10
            )
        )
        self.address_local_title._impl.native.Font = self.monda_font.get(10, True)

        self.sent_title = Label(
            text=self.tr.text("sent_title"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.sent_title._impl.native.Font = self.monda_font.get(10, True)

        self.received_title = Label(
            text=self.tr.text("received_title"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.received_title._impl.native.Font = self.monda_font.get(10, True)

        self.subversion_title = Label(
            text=self.tr.text("subversion_title"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.subversion_title._impl.native.Font = self.monda_font.get(10, True)

        self.conntime_title = Label(
            text=self.tr.text("conntime_title"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.conntime_title._impl.native.Font = self.monda_font.get(10, True)

        self.content = self.main_scroll

        self.main_scroll.content = self.main_box

        self.main_box.add(
            self.titles_box
        )
        self.titles_box.add(
            self.address_title,
            self.address_local_title,
            self.sent_title,
            self.received_title,
            self.subversion_title,
            self.conntime_title
        )

        self.app.add_background_task(self.get_peers_info)


    async def get_peers_info(self, widget):
        while True:
            if not self.main.peer_toggle:
                return
            if self.main.import_key_toggle:
                self.main.peer_toggle = None
                self.close()
                return

            peerinfo, _ = await self.commands.getPeerinfo()
            if peerinfo:
                peerinfo = json.loads(peerinfo)
                current_addresses = set()
                node_by_address = {}

                for node in peerinfo:
                    address = node.get('addr')
                    current_addresses.add(address)
                    node_by_address[address] = node

                    if address not in self.peers_list:
                        self.peers_list.append(address)
                        self.add_peer(node)

                for address in list(self.peers_list):
                    if address not in current_addresses:
                        self.remove_peer({'addr': address})
                        self.peers_list.remove(address)
                    else:
                        self.update_peer(node_by_address[address])

                current_addresses.clear()

            await asyncio.sleep(5)


    def add_peer(self, node):
        node_box = Node(
            self.app, self, node, self.settings, self.utils, self.units, self.commands, self.tr, self.monda_font
        )
        box_divider = Divider(
            direction=Direction.HORIZONTAL,
            style=Pack(
                background_color = WHITE,
                flex =1
            )
        )
        self.main_box.add(node_box, box_divider)
        self.node_map[node.get('addr')] = (node_box, box_divider)

    
    def update_peer(self, node):
        address = node.get('addr')
        widgets = self.node_map.get(address)
        if not widgets:
            return
        node_box, _ = widgets
        lastsend = node.get('lastsend')
        lastrecv = node.get('lastrecv')
        conntime = node.get('conntime')
        conn_time = datetime.fromtimestamp(conntime, tz=timezone.utc)
        last_send = datetime.fromtimestamp(lastsend).strftime('%Y-%m-%d %H:%M:%S')
        last_receive = datetime.fromtimestamp(lastrecv).strftime('%Y-%m-%d %H:%M:%S')
        conn_duration = self.units.create_timer(conn_time)
        node_box.node_sent.text = self.units.format_bytes(node.get('bytessent'))
        self.tooltip.insert(node_box.node_sent._impl.native, f"Last send :{last_send}")
        node_box.node_receive.text = self.units.format_bytes(node.get('bytesrecv'))
        self.tooltip.insert(node_box.node_receive._impl.native, f"Last receive :{last_receive}")
        node_box.node_conntime.text = conn_duration
        node_box.node = node


    def remove_peer(self, node):
        address = node.get('addr')
        widgets = self.node_map.get(address)
        if widgets:
            node_box, box_divider = widgets
            self.main_box.remove(node_box)
            self.main_box.remove(box_divider)
            del self.node_map[address]


    def _handle_on_resize(self, sender, event:Sys.EventArgs):
        min_width = 916
        min_height = 646
        self._impl.native.MinimumSize = Drawing.Size(min_width, min_height)


    def close_peers_window(self, widget):
        self.main.peer_toggle = None
        self.close()