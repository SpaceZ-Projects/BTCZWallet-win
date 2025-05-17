
import asyncio
import json
from datetime import datetime, timezone

from toga import App, Window, ScrollContainer, Box, Label
from ..framework import ToolTip
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.style.pack import Pack
from toga.colors import rgb, WHITE, GRAY

from .client import Client
from .units import Units


class Node(Box):
    def __init__(self, app:App, node):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 40,
                padding_top = 5
            )
        )
        self.app = app

        self.units = Units(self.app)
        self.tooltip = ToolTip()

        address = node.get('addr')
        address_tooltip = address
        if 'onion' in address:
            address = address[:12] + "...onion"
        address_local = node.get('addrlocal')
        bytessent = node.get('bytessent')
        bytesrecv = node.get('bytesrecv')
        subver = node.get('subver')
        clean_subversion = subver.strip('/')
        conntime = node.get('conntime')
        conn_time = datetime.fromtimestamp(conntime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        duration = now - conn_time
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if days > 0:
            conn_duration_str = f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            conn_duration_str = f"{hours}h {minutes}m"
        else:
            conn_duration_str = f"{minutes}m"


        self.node_address = Label(
            text=address,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.tooltip.insert(self.node_address._impl.native, address_tooltip)

        self.node_address_local = Label(
            text=address_local,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_sent = Label(
            text=self.units.format_bytes(bytessent),
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_receive = Label(
            text=self.units.format_bytes(bytesrecv),
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_subversion = Label(
            text=clean_subversion,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.node_conntime= Label(
            text=conn_duration_str,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.add(
            self.node_address,
            self.node_address_local,
            self.node_sent,
            self.node_receive,
            self.node_subversion,
            self.node_conntime
        )


class Peer(Window):
    def __init__(self, main:Window):
        super().__init__()

        self.main = main
        self.commands = Client(self.app)
        self.units = Units(self.app)
        self.tooltip = ToolTip()

        self.title = "Peers Info"
        self.size = self.main.size
        self.position = self.main.position
        self.on_close = self.close_peers_window

        self.peers_list = []
        self.node_map = {}

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
            text="Address",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.address_local_title = Label(
            text="Address local",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.sent_title = Label(
            text="Sent",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.receive_title = Label(
            text="Received",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.subversion_title = Label(
            text="Subversion",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.conntime_title = Label(
            text="Conn. Time",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.content = self.main_scroll

        self.main_scroll.content = self.main_box

        self.main_box.add(
            self.titles_box
        )
        self.titles_box.add(
            self.address_title,
            self.address_local_title,
            self.sent_title,
            self.receive_title,
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
            peerinfo, _= await self.commands.getPeerinfo()
            if peerinfo:
                peerinfo = json.loads(peerinfo)
                for node in peerinfo:
                    address = node.get('addr')
                    if address not in self.peers_list:
                        self.peers_list.append(address)
                        self.add_peer(node)
                    else:
                        self.update_peer(node)
            
            await asyncio.sleep(10)


    def add_peer(self, node):
        node_box = Node(self.app, node)
        self.main_box.add(node_box)
        self.node_map[node.get('addr')] = node_box

    
    def update_peer(self, node):
        address = node.get('addr')
        node_box = self.node_map.get(address)
        if not node:
            return
        lastsend = node.get('lastsend')
        lastrecv = node.get('lastrecv')
        conntime = node.get('conntime')
        conn_time = datetime.fromtimestamp(conntime, tz=timezone.utc)
        last_send = datetime.fromtimestamp(lastsend).strftime('%Y-%m-%d %H:%M:%S')
        last_receive = datetime.fromtimestamp(lastrecv).strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.now(timezone.utc)
        duration = now - conn_time
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        if days > 0:
            conn_duration = f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            conn_duration = f"{hours}h {minutes}m"
        else:
            conn_duration = f"{minutes}m"
        node_box.node_sent.text = self.units.format_bytes(node.get('bytessent'))
        self.tooltip.insert(node_box.node_sent._impl.native, f"Last send :{last_send}")
        node_box.node_receive.text = self.units.format_bytes(node.get('bytesrecv'))
        self.tooltip.insert(node_box.node_receive._impl.native, f"Last receive :{last_receive}")
        node_box.node_conntime.text = conn_duration


    def close_peers_window(self, widget):
        self.main.peer_toggle = None
        self.close()