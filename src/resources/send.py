import asyncio
import json

from toga import (
    App, Box, Label, TextInput, Selection, ImageView
)
from ..framework import Forms
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, TOP, BOLD, CENTER, LEFT
from toga.colors import rgb, GRAY, WHITE, YELLOW, BLACK

from .client import Client


class Send(Box):
    def __init__(self, app:App):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5)
            )
        )

        self.app = app
        self.commands = Client(self.app)

        self.send_toggle = None
        self.transparent_toggle = None
        self.private_toggle = None

        self.switch_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = TOP,
                height = 35,
                padding = (5,5,0,5)
            )
        )

        self.transparent_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )
        self.transparent_label = Label(
            text="Transparent",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
        self.transparent_button._impl.native.MouseEnter += self.transparent_button_mouse_enter
        self.transparent_label._impl.native.MouseEnter += self.transparent_button_mouse_enter
        self.transparent_button._impl.native.MouseLeave += self.transparent_button_mouse_leave
        self.transparent_label._impl.native.MouseLeave += self.transparent_button_mouse_leave
        self.transparent_button._impl.native.Click += self.transparent_button_click
        self.transparent_label._impl.native.Click += self.transparent_button_click
        self.private_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )
        self.private_label = Label(
            text="Private",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )
        self.private_button._impl.native.MouseEnter += self.private_button_mouse_enter
        self.private_label._impl.native.MouseEnter += self.private_button_mouse_enter
        self.private_button._impl.native.MouseLeave += self.private_button_mouse_leave
        self.private_label._impl.native.MouseLeave += self.private_button_mouse_leave
        self.private_button._impl.native.Click += self.private_button_click
        self.private_label._impl.native.Click += self.private_button_click

        self.from_address_label = Label(
            text="From :",
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
            accessor="select_address"
        )
        self.address_selection._impl.native.FlatStyle = Forms.FlatStyle.Flat

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
                flex = 1,
                padding=(10,5,0,5),
                height = 55
            )
        )

        self.distination_label = Label(
            text="To :",
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

        self.distination_input = TextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 2,
                padding_top = 10
            )
        )

        self.is_valid = ImageView(
            style=Pack(
                background_color = rgb(30,33,36),
                width = 20,
                height = 20,
                flex = 1
            )
        )
        self.is_valid_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1 
            )
        )

        self.distination_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding_left = 5,
                padding_right = 5,
                height = 55
            )
        )

        self.amount_label = Label(
            text="Amount :",
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

        self.amount_input = TextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1,
                padding_top = 10
            )
        )

        self.check_amount_label = Label(
            text="test",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                text_align = LEFT,
                flex = 5,
                padding_top = 12,
                padding_left = 10
            )
        )

        self.amount_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding_left = 5,
                padding_right = 5,
                height = 55
            )
        )

        self.fees_box = Box(
           style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                padding_left = 5,
                padding_right = 5,
                height = 55
            ) 
        )

        self.sparator_box = Box(
           style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                flex = 1
            ) 
        )

        self.send_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.send_label = Label(
            text="Cash Out",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            )
        )

        self.send_button = Box(
            style=Pack(
                background_color = rgb(40,43,48),
                alignment = CENTER,
                padding = 5,
                width = 200,
                height = 40
            )
        )
        self.send_button._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_button._impl.native.MouseLeave += self.send_button_mouse_leave
        self.send_label._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_label._impl.native.MouseLeave += self.send_button_mouse_leave

        self.confirmation_box = Box(
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
        if not self.send_toggle:
            self.add(
                self.switch_box,
                self.selection_address_box,
                self.distination_box,
                self.amount_box,
                self.fees_box,
                self.sparator_box,
                self.confirmation_box
            )
            self.switch_box.add(
                self.transparent_button,
                self.private_button
            )
            self.transparent_button.add(
                self.transparent_label
            )
            self.private_button.add(
                self.private_label
            )
            self.selection_address_box.add(
                self.from_address_label,
                self.address_selection,
                self.address_balance
            )
            self.distination_box.add(
                self.distination_label,
                self.distination_input,
                self.is_valid_box
            )
            self.is_valid_box.add(
                self.is_valid
            )
            self.amount_box.add(
                self.amount_label,
                self.amount_input,
                self.check_amount_label
            )
            self.confirmation_box.add(
                self.send_box,
                self.send_button
            )
            self.send_button.add(
                self.send_label
            )
            self.send_toggle = True
            self.transparent_button_click(None, None)

    def transparent_button_click(self, sender, event):
        self.clear_buttons()
        self.transparent_toggle = True
        self.transparent_button._impl.native.Click -= self.transparent_button_click
        self.transparent_label._impl.native.Click -= self.transparent_button_click
        self.transparent_label.style.color = YELLOW
        self.transparent_label.style.background_color = rgb(66,69,73)
        self.transparent_button.style.background_color = rgb(66,69,73)
        self.app.add_background_task(self.update_send_options)

    
    def transparent_button_mouse_enter(self, sender, event):
        if self.transparent_toggle:
            return
        self.transparent_label.style.color = WHITE
        self.transparent_label.style.background_color = rgb(66,69,73)
        self.transparent_button.style.background_color = rgb(66,69,73)

    def transparent_button_mouse_leave(self, sender, event):
        if self.transparent_toggle:
            return
        self.transparent_label.style.color = GRAY
        self.transparent_label.style.background_color = rgb(30,33,36)
        self.transparent_button.style.background_color = rgb(30,33,36)

    
    def private_button_click(self, sender, event):
        self.clear_buttons()
        self.private_toggle = True
        self.private_button._impl.native.Click -= self.private_button_click
        self.private_label._impl.native.Click -= self.private_button_click
        self.private_label.style.color = rgb(114,137,218)
        self.private_label.style.background_color = rgb(66,69,73)
        self.private_button.style.background_color = rgb(66,69,73)
        self.app.add_background_task(self.update_send_options)

    
    def private_button_mouse_enter(self, sender, event):
        if self.private_toggle:
            return
        self.private_label.style.color = WHITE
        self.private_label.style.background_color = rgb(66,69,73)
        self.private_button.style.background_color = rgb(66,69,73)

    def private_button_mouse_leave(self, sender, event):
        if self.private_toggle:
            return
        self.private_label.style.color = GRAY
        self.private_label.style.background_color = rgb(30,33,36)
        self.private_button.style.background_color = rgb(30,33,36)

    async def update_send_options(self, widegt):
        if self.transparent_toggle:
            selection_items = await self.get_transparent_addresses()
        if self.private_toggle:
            selection_items = await self.get_private_addresses()

        self.address_selection.items.clear()
        self.address_selection.items = selection_items

    def clear_buttons(self):
        if self.transparent_toggle:
            self.transparent_label.style.color = GRAY
            self.transparent_label.style.background_color = rgb(30,33,36)
            self.transparent_button.style.background_color = rgb(30,33,36)
            self.transparent_button._impl.native.Click += self.transparent_button_click
            self.transparent_label._impl.native.Click += self.transparent_button_click
            self.transparent_toggle = None

        elif self.private_toggle:
            self.private_label.style.color = GRAY
            self.private_label.style.background_color = rgb(30,33,36)
            self.private_button.style.background_color = rgb(30,33,36)
            self.private_button._impl.native.Click += self.private_button_click
            self.private_label._impl.native.Click += self.private_button_click
            self.private_toggle = None

    def send_button_mouse_enter(self, sender, event):
        if self.transparent_toggle:
            self.send_label.style.color = BLACK
            self.send_button.style.background_color = YELLOW
            self.send_label.style.background_color = YELLOW
        elif self.private_toggle:
            self.send_label.style.color = WHITE
            self.send_button.style.background_color = rgb(114,137,218)
            self.send_label.style.background_color = rgb(114,137,218)

    def send_button_mouse_leave(self, sender, event):
        self.send_label.style.color = GRAY
        self.send_button.style.background_color = rgb(40,43,48)
        self.send_label.style.background_color = rgb(40,43,48)


    async def get_transparent_addresses(self):
        addresses_data, _ = await self.commands.ListAddresses()
        if addresses_data:
            addresses_data = json.loads(addresses_data)
        else:
            addresses_data = []
        if addresses_data:
            address_items = [("Main Account")] + [(address_info, address_info) for address_info in addresses_data]
        else:
            address_items = [("Main Account")]
        return address_items
    
    async def get_private_addresses(self):
        addresses_data, _ = await self.commands.z_listAddresses()
        if addresses_data:
            addresses_data = json.loads(addresses_data)
        if addresses_data is not None:
            if len(addresses_data) == 1:
                address_items = [(addresses_data[0], addresses_data[0])]
            else:
                address_items = [(address, address) for address in addresses_data]
        else:
            address_items = []
        return address_items