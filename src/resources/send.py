
import asyncio
import json

from toga import (
    App, Box, Label, TextInput, Selection, 
    ImageView, Window, Switch, MultilineTextInput
)
from ..framework import (
    Command, Color, ToolTip, ComboStyle, MenuStrip
)
from toga.style.pack import Pack
from toga.constants import (
    COLUMN, ROW, TOP, BOLD, CENTER,
    LEFT, VISIBLE, HIDDEN
)
from toga.colors import (
    rgb, GRAY, WHITE, YELLOW, BLACK, RED
)
from .client import Client
from .utils import Utils
from .storage import Storage


class Send(Box):
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
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.storage = Storage(self.app)
        self.tooltip = ToolTip()

        self.send_toggle = None
        self.transparent_toggle = None
        self.private_toggle = None
        self.is_valid_toggle = None
        self.z_addresses_limit_toggle = None

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
                padding=(10,5,0,5),
                height = 55
            )
        )

        self.single_option = Switch(
            text="Single",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 11
            ),
            on_change=self.single_option_on_change
        )
        self.tooltip.insert(self.single_option._impl.native, "Send to single address")

        self.many_option = Switch(
            text="Many",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 11,
                padding = (0,20,0,0)
            ),
            on_change=self.many_option_on_change
        )
        self.tooltip.insert(self.many_option._impl.native, "Send to many addresses")

        self.send_options_switch = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding=(5,5,0,5),
                height = 30,
                alignment = CENTER
            )
        )
        self.send_options_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                padding=(5,5,0,5),
                height = 30,
                alignment = CENTER
            )
        )

        self.destination_label = Label(
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

        self.destination_input_single = TextInput(
            placeholder="address",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 2,
                padding_top = 10
            ),
            on_change=self.is_valid_address
        )

        self.destination_input_many = MultilineTextInput(
            placeholder="addresses list",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 2,
                padding_top = 10,
                height = 75
            ),
            on_change=self.destination_input_many_on_change
        )

        self.is_valid = ImageView(
            style=Pack(
                background_color = rgb(30,33,36),
                width = 30,
                height = 30,
                padding= (9,0,0,10)
            )
        )
        self.is_valid_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1 
            )
        )

        self.destination_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding = (0,5,0,5),
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
            placeholder="0.00000000",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1,
                padding_top = 10
            ),
            validators=[
                self.is_digit
            ],
            on_change=self.verify_balance
        )

        self.check_amount_label = Label(
            text="",
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 11,
                text_align = LEFT,
                flex = 5,
                padding_top = 12,
                padding_left = 10
            )
        )

        self.split_option = Switch(
            text="Split",
            value=True,
            style=Pack(
                color = YELLOW,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 11
            ),
            on_change=self.split_option_on_change
        )
        self.tooltip.insert(self.split_option._impl.native, "Split the total amount equally across all addresses.")

        self.each_option = Switch(
            text="Each",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 11,
                padding_left = 20
            ),
            on_change=self.each_option_on_change
        )
        self.tooltip.insert(self.each_option._impl.native, "Set a specific amount for each address.")


        self.amount_options_switch = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                height = 30,
                alignment = CENTER
            )
        )
        self.amount_options_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                padding=(0,5,0,5),
                height = 30,
                alignment = CENTER
            )
        )

        self.amount_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding = (5,5,0,5),
                height = 50
            )
        )

        self.fees_label = Label(
            text="Fee :",
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
        self.fee_input = TextInput(
            placeholder="0.00000000",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 12,
                flex = 1,
                padding_top = 10
            ),
            validators=[
                self.is_digit
            ]
        )
        self.empty_box = Box(
            style=Pack(
                background_color = rgb(30,33,36),
                flex = 5
            )
        )
        self.fees_box = Box(
           style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding = (5,5,0,5),
                height = 50
            ) 
        )

        self.separator_box = Box(
           style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                flex = 1
            ) 
        )

        self.operation_label = Label(
            text="Operation Status :",
            style=Pack(
                color = GRAY,
                text_align= LEFT,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 11
            )
        )

        self.operation_status = Label(
            text="",
            style=Pack(
                color = WHITE,
                text_align= LEFT,
                background_color = rgb(30,33,36),
                font_weight = BOLD,
                font_size = 11
            )
        )

        self.operation_box = Box(
            style=Pack(
                direction = ROW,
                padding_left = 10
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
                padding = 7,
                width = 200,
                height = 40
            )
        )
        self.send_button._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_button._impl.native.MouseLeave += self.send_button_mouse_leave
        self.send_label._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_label._impl.native.MouseLeave += self.send_button_mouse_leave
        self.send_button._impl.native.Click += self.send_button_click
        self.send_label._impl.native.Click += self.send_button_click

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
                self.send_options_box,
                self.destination_box,
                self.amount_box,
                self.fees_box,
                self.separator_box,
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
            self.send_options_box.add(
                self.send_options_switch
            )
            self.send_options_switch.add(
                self.single_option,
                self.many_option
            )
            self.destination_box.add(
                self.destination_label,
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
            self.amount_options_switch.add(
                self.split_option,
                self.each_option
            )
            self.amount_options_box.add(
                self.amount_options_switch
            )
            self.fees_box.add(
                self.fees_label,
                self.fee_input,
                self.empty_box
            )
            self.confirmation_box.add(
                self.send_box,
                self.send_button
            )
            self.send_box.add(
                self.operation_box
            )
            self.operation_box.add(
                self.operation_label,
                self.operation_status
            )
            self.send_button.add(
                self.send_label
            )
            self.send_toggle = True
            self.transparent_button_click(None, None)
            self.insert_menustrip()
        

    def insert_menustrip(self):
        destination_context_menu = MenuStrip()
        self.messages_address_cmd = Command(
            title="Send to messages address",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_destination_messages_address,
            icon="images/deposit_messages_i.ico",
            mouse_enter=self.messages_address_cmd_mouse_enter,
            mouse_leave=self.messages_address_cmd_mouse_leave
        )
        messages_address_commands = [self.messages_address_cmd]
        for command in messages_address_commands:
            destination_context_menu.Items.Add(command)
        self.destination_input_single._impl.native.ContextMenuStrip = destination_context_menu

        amount_context_menu = MenuStrip()
        self.percentage_25_cmd = Command(
            title="25 amount",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_25_amount,
            icon="images/percentage_i.ico",
            mouse_enter=self.percentage_25_cmd_mouse_enter,
            mouse_leave=self.percentage_25_cmd_mouse_leave
        )
        self.percentage_50_cmd = Command(
            title="50 amount",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_50_amount,
            icon="images/percentage_i.ico",
            mouse_enter=self.percentage_50_cmd_mouse_enter,
            mouse_leave=self.percentage_50_cmd_mouse_leave
        )
        self.percentage_75_cmd = Command(
            title="75 amount",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_75_amount,
            icon="images/percentage_i.ico",
            mouse_enter=self.percentage_75_cmd_mouse_enter,
            mouse_leave=self.percentage_75_cmd_mouse_leave
        )
        self.max_amount_cmd = Command(
            title="Max amount",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_max_amount,
            icon="images/max_i.ico",
            mouse_enter=self.max_amount_cmd_mouse_enter,
            mouse_leave=self.max_amount_cmd_mouse_leave
        )
        amount_commands = [
            self.percentage_25_cmd,
            self.percentage_50_cmd,
            self.percentage_75_cmd,
            self.max_amount_cmd
        ]
        for command in amount_commands:
            amount_context_menu.Items.Add(command)
        self.amount_input._impl.native.ContextMenuStrip = amount_context_menu

        fee_context_menu = MenuStrip()
        self.slow_fee_cmd = Command(
            title="Slow",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_slow_fee,
            icon="images/slow_i.ico",
            mouse_enter=self.slow_fee_cmd_mouse_enter,
            mouse_leave=self.slow_fee_cmd_mouse_leave
        )
        self.normal_fee_cmd = Command(
            title="Normal",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_normal_fee,
            icon="images/normal_i.ico",
            mouse_enter=self.normal_fee_cmd_mouse_enter,
            mouse_leave=self.normal_fee_cmd_mouse_leave
        )
        self.fast_fee_cmd = Command(
            title="Fast",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_fast_fee,
            icon="images/fast_i.ico",
            mouse_enter=self.fast_fee_cmd_mouse_enter,
            mouse_leave=self.fast_fee_cmd_mouse_leave
        )
        fee_commands = [
            self.slow_fee_cmd,
            self.normal_fee_cmd,
            self.fast_fee_cmd
        ]
        for command in fee_commands:
            fee_context_menu.Items.Add(command)
        self.fee_input._impl.native.ContextMenuStrip = fee_context_menu


    def transparent_button_click(self, sender, event):
        self.clear_buttons()
        self.transparent_toggle = True
        self.transparent_button._impl.native.Click -= self.transparent_button_click
        self.transparent_label._impl.native.Click -= self.transparent_button_click
        self.transparent_label.style.color = YELLOW
        self.transparent_label.style.background_color = rgb(66,69,73)
        self.transparent_button.style.background_color = rgb(66,69,73)
        self.address_selection.focus()
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
        self.address_selection.focus()
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


    def set_destination_messages_address(self):
        selected_address = self.address_selection.value.select_address
        if selected_address == "Main Account":
            self.main.error_dialog(
                title="Error",
                message="You can't send amount from Main Account to messages (z) address."
            )
            return
        address = self.storage.get_identity("address")
        if address:
            value = address[0]
        else:
            value = "You don't have messages address yet !"
        self.destination_input_single.value = value


    def set_25_amount(self):
        if self.address_selection.value.select_address:
            selected_address = self.address_selection.value.select_address
            balance = self.address_balance.text
            if selected_address == "Main Account":
                if float(balance) > 0.0002:
                    balance_after_fee = float(balance) - 0.0001
                    amount = balance_after_fee * 0.25
                    self.amount_input.value = f"{amount:.8f}"
            else:
                if float(balance) > 0:
                    fee = self.fee_input.value
                    balance_after_fee = float(balance) - float(fee)
                    amount = balance_after_fee * 0.25
                    self.amount_input.value = f"{amount:.8f}"


    def set_50_amount(self):
        if self.address_selection.value.select_address:
            selected_address = self.address_selection.value.select_address
            balance = self.address_balance.text
            if selected_address == "Main Account":
                if float(balance) > 0.0002:
                    balance_after_fee = float(balance) - 0.0001
                    amount = balance_after_fee * 0.50
                    self.amount_input.value = f"{amount:.8f}"
            else:
                if float(balance) > 0:
                    fee = self.fee_input.value
                    balance_after_fee = float(balance) - float(fee)
                    amount = balance_after_fee * 0.50
                    self.amount_input.value = f"{amount:.8f}"


    def set_75_amount(self):
        if self.address_selection.value.select_address:
            selected_address = self.address_selection.value.select_address
            balance = self.address_balance.text
            if selected_address == "Main Account":
                if float(balance) > 0.0002:
                    balance_after_fee = float(balance) - 0.0001
                    amount = balance_after_fee * 0.75
                    self.amount_input.value = f"{amount:.8f}"
            else:
                if float(balance) > 0:
                    fee = self.fee_input.value
                    balance_after_fee = float(balance) - float(fee)
                    amount = balance_after_fee * 0.75
                    self.amount_input.value = f"{amount:.8f}"


    def set_max_amount(self):
        if self.address_selection.value.select_address:
            selected_address = self.address_selection.value.select_address
            balance = self.address_balance.text
            if selected_address == "Main Account":
                if float(balance) > 0.0002:
                    amount = float(balance) - 0.0001
                    self.amount_input.value = f"{amount:.8f}"
            else:
                if float(balance) > 0:
                    fee = self.fee_input.value
                    amount = float(balance) - float(fee)
                    self.amount_input.value = f"{amount:.8f}"


    def set_slow_fee(self):
        self.fee_input.value = "0.00000100"

    def set_normal_fee(self):
        self.fee_input.value = "0.00001000"

    def set_fast_fee(self):
        self.fee_input.value = "0.00010000"
    

    def messages_address_cmd_mouse_enter(self):
        self.messages_address_cmd.icon = "images/deposit_messages_a.ico"
        self.messages_address_cmd.color = Color.BLACK

    def messages_address_cmd_mouse_leave(self):
        self.messages_address_cmd.icon = "images/deposit_messages_i.ico"
        self.messages_address_cmd.color = Color.WHITE


    def percentage_25_cmd_mouse_enter(self):
        self.percentage_25_cmd.icon = "images/percentage_a.ico"
        self.percentage_25_cmd.color = Color.BLACK

    def percentage_25_cmd_mouse_leave(self):
        self.percentage_25_cmd.icon = "images/percentage_i.ico"
        self.percentage_25_cmd.color = Color.WHITE

    def percentage_50_cmd_mouse_enter(self):
        self.percentage_50_cmd.icon = "images/percentage_a.ico"
        self.percentage_50_cmd.color = Color.BLACK

    def percentage_50_cmd_mouse_leave(self):
        self.percentage_50_cmd.icon = "images/percentage_i.ico"
        self.percentage_50_cmd.color = Color.WHITE

    def percentage_75_cmd_mouse_enter(self):
        self.percentage_75_cmd.icon = "images/percentage_a.ico"
        self.percentage_75_cmd.color = Color.BLACK

    def percentage_75_cmd_mouse_leave(self):
        self.percentage_75_cmd.icon = "images/percentage_i.ico"
        self.percentage_75_cmd.color = Color.WHITE
    
    def max_amount_cmd_mouse_enter(self):
        self.max_amount_cmd.icon = "images/max_a.ico"
        self.max_amount_cmd.color = Color.BLACK

    def max_amount_cmd_mouse_leave(self):
        self.max_amount_cmd.icon = "images/max_i.ico"
        self.max_amount_cmd.color = Color.WHITE

    def slow_fee_cmd_mouse_enter(self):
        self.slow_fee_cmd.icon = "images/slow_a.ico"
        self.slow_fee_cmd.color = Color.BLACK

    def slow_fee_cmd_mouse_leave(self):
        self.slow_fee_cmd.icon = "images/slow_i.ico"
        self.slow_fee_cmd.color = Color.WHITE

    
    def normal_fee_cmd_mouse_enter(self):
        self.normal_fee_cmd.icon = "images/normal_a.ico"
        self.normal_fee_cmd.color = Color.BLACK

    def normal_fee_cmd_mouse_leave(self):
        self.normal_fee_cmd.icon = "images/normal_i.ico"
        self.normal_fee_cmd.color = Color.WHITE

    def fast_fee_cmd_mouse_enter(self):
        self.fast_fee_cmd.icon = "images/fast_a.ico"
        self.fast_fee_cmd.color = Color.BLACK

    def fast_fee_cmd_mouse_leave(self):
        self.fast_fee_cmd.icon = "images/fast_i.ico"
        self.fast_fee_cmd.color = Color.WHITE


    async def get_transparent_addresses(self):
        addresses_data, _ = await self.commands.ListAddresses()
        if addresses_data:
            addresses_data = json.loads(addresses_data)
        else:
            addresses_data = []
        if addresses_data is not None:
            address_items = [("Main Account")] + [(address_info, address_info) for address_info in addresses_data]
        else:
            address_items = [("Main Account")]
        return address_items
    
    
    async def get_private_addresses(self):
        addresses_data, _ = await self.commands.z_listAddresses()
        addresses_data = json.loads(addresses_data)
        if addresses_data is not None:
            if len(addresses_data) == 1:
                address_items = [(addresses_data[0], addresses_data[0])]
            else:
                address_items = [(address, address) for address in addresses_data]
        else:
            address_items = []
        return address_items
    
    
    async def display_address_balance(self, selection):
        if selection.value is None:
            self.address_balance.text = "0.00000000"
            return
        self.amount_input.value = ""
        selected_address = selection.value.select_address
        self.tooltip.insert(self.address_selection._impl.native, selected_address)
        if selected_address != "Main Account":
            self.single_option.enabled = True
            self.many_option.enabled =True
            if self.many_option.value is False:
                self.update_fees_option(True)
            balance, _ = await self.commands.z_getBalance(selected_address)
            if balance:
                if float(balance) <= 0:
                    self.address_balance.style.color = GRAY
                else:
                    self.address_balance.style.color = WHITE
                format_balance = self.utils.format_balance(float(balance))
                self.address_balance.text = format_balance
        elif selected_address == "Main Account":
            self.single_option.value = True
            self.single_option.enabled = False
            self.many_option.enabled =False
            self.update_fees_option(False)
            total_balances, _ = await self.commands.z_getTotalBalance()
            if total_balances:
                balances = json.loads(total_balances)
                transparent = balances.get('transparent')
                if float(transparent) <= 0:
                    self.address_balance.style.color = GRAY
                else:
                    self.address_balance.style.color = WHITE
                format_balance = self.utils.format_balance(float(transparent))
                self.address_balance.text = format_balance
        else:
            self.address_balance.text = "0.00000000"


    def single_option_on_change(self, switch):
        if switch.value is True:
            self.many_option.value = False
            self.single_option.style.color = YELLOW
            self.destination_box.insert(1, self.destination_input_single)
            self.destination_input_single.readonly = False
            self.update_fees_option(True)
            self.is_valid_toggle = None
        else:
            if self.many_option.value is True:
                self.single_option.value = False
                self.single_option.style.color = GRAY
                self.destination_box.remove(
                    self.destination_input_single
                )
            else:
                self.single_option.value = True
        
    def many_option_on_change(self, switch):
        if switch.value is True:
            self.single_option.value = False
            self.many_option.style.color = YELLOW
            self.destination_box.style.height = 100
            self.destination_box.insert(1, self.destination_input_many)
            self.insert(5, self.amount_options_box)
            self.update_fees_option(False)
            self.is_valid_toggle = True
        else:
            if self.single_option.value is True:
                self.many_option.value = False
                self.many_option.style.color = GRAY
                self.destination_box.style.height = 55
                self.destination_box.remove(
                    self.destination_input_many
                )
                self.remove(self.amount_options_box)
            else:
                self.many_option.value = True


    def split_option_on_change(self, switch):
        if switch.value is True:
            self.each_option.value = False
            self.each_option.style.color = GRAY
        else:
            self.each_option.value = True
            self.each_option.style.color = YELLOW

    def each_option_on_change(self, switch):
        if switch.value is True:
            self.split_option.value = False
            self.split_option.style.color = GRAY
        else:
            self.split_option.value = True
            self.split_option.style.color = YELLOW


    async def clear_inputs(self):
        if self.transparent_toggle:
            selection_items = await self.get_transparent_addresses()
        if self.private_toggle:
            selection_items = await self.get_private_addresses()
        self.address_selection.items.clear()
        self.address_selection.items = selection_items
        if self.many_option.value is True:
            self.destination_input_many.value = ""
        elif self.single_option.value is True:
            self.destination_input_single.value = ""
        self.amount_input.value = ""

    def update_fees_option(self, option):
        if option:
            self.fees_box.style.visibility = VISIBLE
            self.app.add_background_task(self.set_default_fee)
        else:
            self.fees_box.style.visibility = HIDDEN

    async def set_default_fee(self, widget):
        result, _= await self.commands.getInfo()
        result = json.loads(result)
        if result is not None:
            paytxfee = result.get('paytxfee')
            relayfee = result.get('relayfee')
        if paytxfee == 0.0:
            self.fee_input.value = f"{relayfee:.8f}"
        else:
            self.fee_input.value = f"{paytxfee:.8f}"


    async def is_valid_address(self, input):
        address = self.destination_input_single.value
        if not address:
            self.is_valid.image = None
            return
        if address.startswith("t"):
            result, _ = await self.commands.validateAddress(address)
        elif address.startswith("z"):
            result, _ = await self.commands.z_validateAddress(address)
        else:
            self.is_valid.image = "images/notvalid.png"
            return
        if result is not None:
            result = json.loads(result)
            is_valid = result.get('isvalid')
            if is_valid is True:
                self.is_valid.image = "images/valid.png"
                self.is_valid_toggle = True
            elif is_valid is False:
                self.is_valid.image = "images/notvalid.png"
                self.is_valid_toggle = False


    async def destination_input_many_on_change(self, input):
        addresses = self.destination_input_many.value
        if not addresses:
            self.is_valid.image = None
            return
        inputs_lines = addresses.strip().split('\n')
        count_z_addresses = sum(1 for address in inputs_lines if address.strip().lower().startswith('z'))
        if count_z_addresses > 54:
            self.z_addresses_limit_toggle = True
            return
        self.z_addresses_limit_toggle = False


    
    async def verify_balance(self, input):
        amount = self.amount_input.value
        if not amount:
            self.check_amount_label.text = ""
            return
        balance = self.address_balance.text
        if float(balance) < float(amount):
            self.check_amount_label.text = "Insufficient"
        else:
            self.check_amount_label.text = ""


    def is_digit(self, value):
        if not self.amount_input.value.replace('.', '', 1).isdigit():
            self.amount_input.value = ""
        if not self.fee_input.value.replace('.', '', 1).isdigit():
            self.fee_input.value = ""


    def send_button_click(self, sender, event):
        selected_address = self.address_selection.value.select_address if self.address_selection.value else None
        if self.many_option.value is True:
            destination_address = self.destination_input_many.value
        else:
            destination_address = self.destination_input_single.value
        amount = self.amount_input.value
        balance = self.address_balance.text
        if selected_address is None:
            self.main.error_dialog(
                "Oops! No address selected",
                "Please select the address you want to send from."
            )
            self.address_selection.focus()
            return
        elif destination_address == "":
            self.main.error_dialog(
                "Destination address is missing",
                "Please enter a destination address where you want to send the funds."
            )
            if self.many_option.value is True:
                self.destination_input_many.focus()
            else:
                self.destination_input_single.focus()
            return
        elif self.z_addresses_limit_toggle:
            self.main.error_dialog(
                title="Error",
                message="The maximum number of zaddr outputs is 54 due to transaction size limits."
            )
            return
        elif not self.is_valid_toggle:
            self.main.error_dialog(
                "Error",
                "The destination address is not valid"
            )
            self.destination_input_single.focus()
            return
        elif amount == "":
            self.main.error_dialog(
                "Amount not entered",
                "Please specify the amount you wish to send."
            )
            self.amount_input.focus()
            return
        elif float(balance) < float(amount):
            self.main.error_dialog(
                "Insufficient balance",
                "You don't have enough balance to complete this transaction. Please adjust the amount."
            )
            self.amount_input.focus()
            return
        self.app.add_background_task(self.make_transaction)


    async def make_transaction(self, widget):
        self.disable_send()
        selected_address = self.address_selection.value.select_address
        amount = self.amount_input.value
        txfee = self.fee_input.value
        balance = self.address_balance.text
        if self.many_option.value is True:
            destination_address = self.destination_input_many.value
            addresses_array = self.create_addresses_array(destination_address)
            await self.send_many(selected_address, addresses_array)
        else:
            destination_address = self.destination_input_single.value
            await self.send_single(selected_address, destination_address, amount, txfee, balance)


    async def send_single(self, selected_address, destination_address, amount, txfee, balance):
        try:
            if selected_address == "Main Account" and destination_address.startswith("t"):
                operation, _= await self.commands.sendToAddress(destination_address, amount)
                if operation is not None:
                    self.main.info_dialog(
                        title="Success",
                        message="Transaction success"
                    )
                    await self.clear_inputs()
                else:
                    self.main.error_dialog(
                        title="Error",
                        message="Transaction failed."
                    )
                self.enable_send()
            elif selected_address != "Main Account":
                if (float(amount)+float(txfee)) > float(balance):
                    self.main.error_dialog(
                        "Insufficient balance",
                        "You don't have enough balance to complete this transaction. Please adjust the amount."
                    )
                    self.enable_send()
                    return
                operation, _= await self.commands.z_sendMany(selected_address, destination_address, amount, txfee)
                if operation:
                    transaction_status, _= await self.commands.z_getOperationStatus(operation)
                    transaction_status = json.loads(transaction_status)
                    if isinstance(transaction_status, list) and transaction_status:
                        status = transaction_status[0].get('status')
                        self.operation_status.text = status
                        if status == "executing" or status =="success":
                            await asyncio.sleep(1)
                            while True:
                                transaction_result, _= await self.commands.z_getOperationResult(operation)
                                transaction_result = json.loads(transaction_result)
                                if isinstance(transaction_result, list) and transaction_result:
                                    status = transaction_result[0].get('status')
                                    self.operation_status.text = status
                                    if status == "failed":
                                        self.enable_send()
                                        self.main.error_dialog(
                                            title="Error",
                                            message="Transaction failed."
                                        )
                                        return
                                    self.enable_send()
                                    self.main.info_dialog(
                                        title="Success",
                                        message="Transaction success"
                                    )
                                    await self.clear_inputs()
                                    return
                                await asyncio.sleep(3)
                else:
                    self.enable_send()
                    self.main.error_dialog(
                        title="Error",
                        message="Transaction failed."
                    )
        except Exception as e:
            self.enable_send()
            print(f"An error occurred: {e}")



    def create_addresses_array(self, addresses_list):
        addresses = [line.strip() for line in addresses_list.strip().split('\n') if line.strip()]
        amount_value = self.amount_input.value
        if self.split_option.value is True:
            amount = float(amount_value) / len(addresses)
            amount = f"{amount:.8f}"
        elif self.each_option.value is True:
            total_amount = float(amount_value) * len(addresses)
            address_balance = self.address_balance.text
            if float(total_amount) > float(address_balance):
                self.main.error_dialog(
                    "Error...",
                    f"Insufficient balance for this transaction.\nTotal amount = {total_amount:.8f}"
                )
                return
            else:
                amount = amount_value
        transactions = [{"address": address, "amount": amount} for address in addresses]
        return transactions


    
    async def send_many(self, selected_address, destination_address):
        try:
            operation, _= await self.commands.z_sendToManyAddresses(selected_address, destination_address)
            if operation:
                transaction_status, _= await self.commands.z_getOperationStatus(operation)
                transaction_status = json.loads(transaction_status)
                if isinstance(transaction_status, list) and transaction_status:
                    status = transaction_status[0].get('status')
                    self.operation_status.text = status
                    if status == "executing" or status =="success":
                        await asyncio.sleep(1)
                        while True:
                            transaction_result, _= await self.commands.z_getOperationResult(operation)
                            transaction_result = json.loads(transaction_result)
                            if isinstance(transaction_result, list) and transaction_result:
                                status = transaction_status[0].get('status')
                                self.operation_status.text = status
                                if status == "failed":
                                    self.enable_send()
                                    self.main.error_dialog(
                                        title="Error",
                                        message="Transaction failed."
                                    )
                                    return
                                self.enable_send()
                                self.main.info_dialog(
                                    title="Success",
                                    message="Transaction success"
                                )
                                await self.clear_inputs()
                                return
                            await asyncio.sleep(3)
            else:
                self.enable_send()
                self.main.error_dialog(
                    title="Error",
                    message="Transaction failed."
                )
        except Exception as e:
            self.enable_send()
            print(f"An error occurred: {e}")

    
    def disable_send(self):
        self.send_button._impl.native.Enabled = False
        self.send_label._impl.native.Enabled = False
        if self.many_option.value is True:
            self.destination_input_many.readonly = True
        elif self.single_option.value is True:
            self.destination_input_single.readonly = True
        self.amount_input.readonly = True
        self.fee_input.readonly = True


    def enable_send(self):
        self.send_button._impl.native.Enabled = True
        self.send_label._impl.native.Enabled = True
        if self.many_option.value is True:
            self.destination_input_many.readonly = False
        elif self.single_option.value is True:
            self.destination_input_single.readonly = False
        self.amount_input.readonly = False
        self.fee_input.readonly = False
        self.operation_status.text = ""