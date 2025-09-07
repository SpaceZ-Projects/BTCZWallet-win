
import asyncio
import json
from datetime import datetime

from toga import (
    App, Box, Label, TextInput, Selection, 
    ImageView, Window, Switch, MultilineTextInput,
    Button
)
from ..framework import (
    Command, Color, ToolTip, FlatStyle, MenuStrip,
    RightToLeft
)
from toga.style.pack import Pack
from toga.constants import (
    COLUMN, ROW, TOP, CENTER, VISIBLE, HIDDEN
)
from toga.colors import (
    rgb, GRAY, WHITE, YELLOW, BLACK, RED
)

from .storage import StorageMessages, StorageTxs, StorageAddresses


class Send(Box):
    def __init__(self, app:App, main:Window, settings, units, commands, tr, font):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5)
            )
        )

        self.send_toggle = None
        self.transparent_toggle = None
        self.shielded_toggle = None
        self.is_valid_toggle = None
        self.z_addresses_limit_toggle = None
        self.operation_toggle = None

        self.app = app
        self.main = main
        self.commands = commands
        self.units = units
        self.settings = settings
        self.tr = tr
        self.font = font

        self.storagemsgs = StorageMessages(self.app)
        self.storagetxs = StorageTxs(self.app)
        self.addresses_storage = StorageAddresses(self.app)
        self.tooltip = ToolTip()

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True


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
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )
        self.transparent_label = Label(
            text=self.tr.text("transparent_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding = (0,0,3,0)
            )
        )
        self.transparent_label._impl.native.Font = self.font.get(self.tr.size("transparent_label"), True)
        self.transparent_button._impl.native.MouseEnter += self.transparent_button_mouse_enter
        self.transparent_label._impl.native.MouseEnter += self.transparent_button_mouse_enter
        self.transparent_button._impl.native.MouseLeave += self.transparent_button_mouse_leave
        self.transparent_label._impl.native.MouseLeave += self.transparent_button_mouse_leave
        self.transparent_button._impl.native.Click += self.transparent_button_click
        self.transparent_label._impl.native.Click += self.transparent_button_click

        self.transparent_line = Box(
            style=Pack(
                background_color = rgb(30,33,36),
                height = 2
            )
        )

        self.shielded_button = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )
        self.shielded_label = Label(
            text=self.tr.text("shielded_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding = (0,0,3,0)
            )
        )
        self.shielded_label._impl.native.Font = self.font.get(self.tr.size("shielded_label"), True)
        self.shielded_button._impl.native.MouseEnter += self.shielded_button_mouse_enter
        self.shielded_label._impl.native.MouseEnter += self.shielded_button_mouse_enter
        self.shielded_button._impl.native.MouseLeave += self.shielded_button_mouse_leave
        self.shielded_label._impl.native.MouseLeave += self.shielded_button_mouse_leave
        self.shielded_button._impl.native.Click += self.shielded_button_click
        self.shielded_label._impl.native.Click += self.shielded_button_click

        self.shielded_line = Box(
            style=Pack(
                background_color = rgb(30,33,36),
                height = 2
            )
        )

        self.from_address_label = Label(
            text=self.tr.text("from_address_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )
        self.from_address_label._impl.native.Font = self.font.get(self.tr.size("from_address_label"), True)

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
        self.address_selection._impl.native.Font = self.font.get(self.tr.size("address_selection"), True)
        self.address_selection._impl.native.FlatStyle = FlatStyle.FLAT
        self.address_selection._impl.native.DropDownHeight = 150

        self.address_balance = Label(
            text=self.tr.text("address_balance_value"),
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
                padding=(10,5,0,5),
                height = 55
            )
        )

        self.single_option = Switch(
            text=self.tr.text("single_option"),
            style=Pack(
                color = YELLOW,
                background_color = rgb(30,33,36)
            ),
            value=True,
            on_change=self.single_option_on_change
        )
        self.single_option._impl.native.Font = self.font.get(self.tr.size("single_option"), True)
        self.tooltip.insert(self.single_option._impl.native, self.tr.tooltip("single_option"))
        if self.rtl:
            self.single_option._impl.native.RightToLeft = RightToLeft.YES

        self.many_option = Switch(
            text=self.tr.text("many_option"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                padding = (0,20,0,0)
            ),
            on_change=self.many_option_on_change
        )
        self.many_option._impl.native.Font = self.font.get(self.tr.size("many_option"), True)
        self.tooltip.insert(self.many_option._impl.native, self.tr.tooltip("many_option"))
        if self.rtl:
            self.many_option._impl.native.RightToLeft = RightToLeft.YES

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
            text=self.tr.text("destination_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1,
                padding_top = 12
            )
        )
        self.destination_label._impl.native.Font = self.font.get(self.tr.size("destination_label"), True)

        self.destination_input_single = TextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 2,
                padding_top = 10
            ),
            on_change=self.is_valid_address
        )
        self.destination_input_single._impl.native.Font = self.font.get(self.tr.size("destination_input_single"), True)
        if self.rtl:
            self.destination_input_single._impl.native.RightToLeft = RightToLeft.YES
        self.destination_input_single.placeholder = self.tr.text("destination_input_single")

        self.destination_input_many = MultilineTextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 2,
                padding_top = 10,
                height = 75
            ),
            on_change=self.destination_input_many_on_change
        )
        self.destination_input_many._impl.native.Font = self.font.get(self.tr.size("destination_input_many"), True)
        if self.rtl:
            self.destination_input_many._impl.native.RightToLeft = RightToLeft.YES
        self.destination_input_many.placeholder = self.tr.text("destination_input_many")

        self.is_valid = ImageView(
            style=Pack(
                background_color = rgb(30,33,36),
                width = 30,
                height = 30,
                padding= self.tr.padding("is_valid")
            )
        )
        self.is_valid_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = self.tr.align("is_valid_box")
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
            text=self.tr.text("amount_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 2,
                padding_top = 12
            )
        )
        self.amount_label._impl.native.Font = self.font.get(self.tr.size("amount_label"), True)

        self.amount_input = TextInput(
            placeholder="0.00000000",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                flex = 1,
                padding_top = 10
            ),
            validators=[
                self.is_digit
            ],
            on_change=self.verify_balance
        )
        self.amount_input._impl.native.Font = self.font.get(self.tr.size("amount_input"), True)

        self.check_amount_label = Label(
            text="",
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                text_align = self.tr.align("check_amount_label"),
                flex = 5,
                padding_top = 12,
                padding_left = 10
            )
        )
        self.check_amount_label._impl.native.Font = self.font.get(10, True)

        self.split_option = Switch(
            text=self.tr.text("split_option"),
            value=True,
            style=Pack(
                color = YELLOW,
                background_color = rgb(30,33,36),
            ),
            on_change=self.split_option_on_change
        )
        self.split_option._impl.native.Font = self.font.get(self.tr.size("split_option"), True)
        self.tooltip.insert(self.split_option._impl.native, self.tr.tooltip("split_option"))
        if self.rtl:
            self.split_option._impl.native.RightToLeft = RightToLeft.YES

        self.each_option = Switch(
            text=self.tr.text("each_option"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                padding = self.tr.padding("each_option")
            ),
            on_change=self.each_option_on_change
        )
        self.each_option._impl.native.Font = self.font.get(self.tr.size("each_option"), True)
        self.tooltip.insert(self.each_option._impl.native, self.tr.tooltip("each_option"))
        if self.rtl:
            self.each_option._impl.native.RightToLeft = RightToLeft.YES


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

        self.fee_label = Label(
            text=self.tr.text("fee_label"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 2,
                padding_top = 12
            )
        )
        self.fee_label._impl.native.Font = self.font.get(self.tr.size("fee_label"), True)

        self.fee_input = TextInput(
            placeholder="0.00000000",
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                flex = 1,
                padding_top = 10
            ),
            validators=[
                self.is_digit
            ]
        )
        self.fee_input._impl.native.Font = self.font.get(self.tr.size("fee_input"), True)

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
            text=self.tr.text("operation_label"),
            style=Pack(
                color = GRAY,
                text_align= self.tr.align("operation_label"),
                background_color = rgb(30,33,36),
                padding_top = 5
            )
        )
        self.operation_label._impl.native.Font = self.font.get(10, True)

        self.operation_status = Label(
            text="",
            style=Pack(
                color = WHITE,
                text_align= self.tr.align("operation_status"),
                background_color = rgb(30,33,36),
                padding_top = 5
            )
        )
        self.operation_status._impl.native.Font = self.font.get(10, True)

        self.operation_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding = self.tr.padding("operation_box")
            )
        )

        self.send_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = self.tr.align("send_box")
            )
        )

        self.send_button = Button(
            text=self.tr.text("cashout_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 150,
                padding = self.tr.padding("cashout_button")
            ),
            on_press=self.send_button_click
        )
        self.send_button._impl.native.Font = self.font.get(self.tr.size("cashout_button"), True)
        self.send_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.send_button._impl.native.MouseEnter += self.send_button_mouse_enter
        self.send_button._impl.native.MouseLeave += self.send_button_mouse_leave

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
        if self.rtl:
            self.switch_box.add(
                self.shielded_button,
                self.transparent_button
            )
        else:
            self.switch_box.add(
                self.transparent_button,
                self.shielded_button
            )
        self.transparent_button.add(
            self.transparent_label,
            self.transparent_line
        )
        self.shielded_button.add(
            self.shielded_label,
            self.shielded_line
        )
        if self.rtl:
            self.selection_address_box.add(
                self.address_balance,
                self.address_selection,
                self.from_address_label
            )
        else:
            self.selection_address_box.add(
                self.from_address_label,
                self.address_selection,
                self.address_balance
            )
        self.send_options_box.add(
            self.send_options_switch
        )
        if self.rtl:
            self.send_options_switch.add(
                self.many_option,
                self.single_option
            )
            self.destination_box.add(
                self.is_valid_box,
                self.destination_input_single,
                self.destination_label
            )
        else:
            self.send_options_switch.add(
                self.single_option,
                self.many_option
            )
            self.destination_box.add(
                self.destination_label,
                self.destination_input_single,
                self.is_valid_box
            )
        self.is_valid_box.add(
            self.is_valid
        )
        if self.rtl:
            self.amount_box.add(
                self.check_amount_label,
                self.amount_input,
                self.amount_label
            )
            self.amount_options_switch.add(
                self.each_option,
                self.split_option
            )
        else:
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
        if self.rtl:
            self.fees_box.add(
                self.empty_box,
                self.fee_input,
                self.fee_label
            )
            self.confirmation_box.add(
                self.send_button,
                self.send_box
            )
        else:
            self.fees_box.add(
                self.fee_label,
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
        if self.rtl:
            self.operation_box.add(
                self.operation_status,
                self.operation_label
            )
        else:
            self.operation_box.add(
                self.operation_label,
                self.operation_status
            )


    def insert_widgets(self):
        if not self.send_toggle:
            self.send_toggle = True
            self.insert_menustrip()
            self.transparent_button_click(None, None)
            asyncio.create_task(self.update_address_balance())
        

    def insert_menustrip(self):
        destination_context_menu = MenuStrip(rtl=self.rtl)
        self.messages_address_cmd = Command(
            title=self.tr.text("messages_address_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_destination_messages_address,
            icon="images/deposit_messages_i.ico",
            mouse_enter=self.messages_address_cmd_mouse_enter,
            mouse_leave=self.messages_address_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        messages_address_commands = [self.messages_address_cmd]
        for command in messages_address_commands:
            destination_context_menu.Items.Add(command)
        self.destination_input_single._impl.native.ContextMenuStrip = destination_context_menu

        amount_context_menu = MenuStrip(rtl=self.rtl)
        self.percentage_25_cmd = Command(
            title=self.tr.text("percentage_25_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_25_amount,
            icon="images/percentage_i.ico",
            mouse_enter=self.percentage_25_cmd_mouse_enter,
            mouse_leave=self.percentage_25_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.percentage_50_cmd = Command(
            title=self.tr.text("percentage_50_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_50_amount,
            icon="images/percentage_i.ico",
            mouse_enter=self.percentage_50_cmd_mouse_enter,
            mouse_leave=self.percentage_50_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.percentage_75_cmd = Command(
            title=self.tr.text("percentage_75_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_75_amount,
            icon="images/percentage_i.ico",
            mouse_enter=self.percentage_75_cmd_mouse_enter,
            mouse_leave=self.percentage_75_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.max_amount_cmd = Command(
            title=self.tr.text("max_amount_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_max_amount,
            icon="images/max_i.ico",
            mouse_enter=self.max_amount_cmd_mouse_enter,
            mouse_leave=self.max_amount_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
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

        fee_context_menu = MenuStrip(rtl=self.rtl)
        self.slow_fee_cmd = Command(
            title=self.tr.text("slow_fee_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_slow_fee,
            icon="images/slow_i.ico",
            mouse_enter=self.slow_fee_cmd_mouse_enter,
            mouse_leave=self.slow_fee_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.normal_fee_cmd = Command(
            title=self.tr.text("normal_fee_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_normal_fee,
            icon="images/normal_i.ico",
            mouse_enter=self.normal_fee_cmd_mouse_enter,
            mouse_leave=self.normal_fee_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
        )
        self.fast_fee_cmd = Command(
            title=self.tr.text("fast_fee_cmd"),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            action=self.set_fast_fee,
            icon="images/fast_i.ico",
            mouse_enter=self.fast_fee_cmd_mouse_enter,
            mouse_leave=self.fast_fee_cmd_mouse_leave,
            font=self.font.get(9),
            rtl=self.rtl
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
        self.transparent_line.style.background_color = YELLOW
        self.update_send_options()

    
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

    
    def shielded_button_click(self, sender, event):
        self.clear_buttons()
        self.shielded_toggle = True
        self.shielded_button._impl.native.Click -= self.shielded_button_click
        self.shielded_label._impl.native.Click -= self.shielded_button_click
        self.shielded_label.style.color = rgb(114,137,218)
        self.shielded_label.style.background_color = rgb(66,69,73)
        self.shielded_button.style.background_color = rgb(66,69,73)
        self.shielded_line.style.background_color = rgb(114,137,218)
        self.update_send_options()

    
    def shielded_button_mouse_enter(self, sender, event):
        if self.shielded_toggle:
            return
        self.shielded_label.style.color = WHITE
        self.shielded_label.style.background_color = rgb(66,69,73)
        self.shielded_button.style.background_color = rgb(66,69,73)

    def shielded_button_mouse_leave(self, sender, event):
        if self.shielded_toggle:
            return
        self.shielded_label.style.color = GRAY
        self.shielded_label.style.background_color = rgb(30,33,36)
        self.shielded_button.style.background_color = rgb(30,33,36)

    def update_send_options(self):
        if self.send_toggle:
            if self.transparent_toggle:
                address_type = "transparent"
            if self.shielded_toggle:
                address_type = "shielded"
            selection_items = self.addresses_storage.get_addresses(address_type=address_type)
            selection_items.sort(key=lambda x: x[3], reverse=True)
            self.address_selection.items.clear()
            for item in selection_items:
                address = item[2]
                self.address_selection.items.append(address)
            self.set_slow_fee()

    def clear_buttons(self):
        if self.transparent_toggle:
            self.transparent_label.style.color = GRAY
            self.transparent_label.style.background_color = rgb(30,33,36)
            self.transparent_button.style.background_color = rgb(30,33,36)
            self.transparent_line.style.background_color = rgb(30,33,36)
            self.transparent_button._impl.native.Click += self.transparent_button_click
            self.transparent_label._impl.native.Click += self.transparent_button_click
            self.transparent_toggle = None

        elif self.shielded_toggle:
            self.shielded_label.style.color = GRAY
            self.shielded_label.style.background_color = rgb(30,33,36)
            self.shielded_button.style.background_color = rgb(30,33,36)
            self.shielded_line.style.background_color = rgb(30,33,36)
            self.shielded_button._impl.native.Click += self.shielded_button_click
            self.shielded_label._impl.native.Click += self.shielded_button_click
            self.shielded_toggle = None

    def send_button_mouse_enter(self, sender, event):
        self.send_button.style.color = BLACK
        if self.transparent_toggle:
            self.send_button.style.background_color = YELLOW
        elif self.shielded_toggle:
            self.send_button.style.background_color = rgb(114,137,218)

    def send_button_mouse_leave(self, sender, event):
        self.send_button.style.color = GRAY
        self.send_button.style.background_color = rgb(30,33,36)


    def set_destination_messages_address(self):
        address = self.storagemsgs.get_identity("address")
        if address:
            value = address[0]
        else:
            value = "You don't have messages address yet !"
        self.destination_input_single.value = value


    def set_25_amount(self):
        if self.address_selection.value.select_address:
            balance = self.format_balance
            if float(balance) > 0:
                fee = self.fee_input.value
                balance_after_fee = float(balance) - float(fee)
                amount = balance_after_fee * 0.25
                self.amount_input.value = f"{amount:.8f}"


    def set_50_amount(self):
        if self.address_selection.value.select_address:
            balance = self.format_balance
            if float(balance) > 0:
                fee = self.fee_input.value
                balance_after_fee = float(balance) - float(fee)
                amount = balance_after_fee * 0.50
                self.amount_input.value = f"{amount:.8f}"


    def set_75_amount(self):
        if self.address_selection.value.select_address:
            balance = self.format_balance
            if float(balance) > 0:
                fee = self.fee_input.value
                balance_after_fee = float(balance) - float(fee)
                amount = balance_after_fee * 0.75
                self.amount_input.value = f"{amount:.8f}"


    def set_max_amount(self):
        if self.address_selection.value.select_address:
            balance = self.format_balance
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
    
    
    async def display_address_balance(self, selection):
        self.format_balance = 0
        if selection.value is None:
            self.address_balance.text = self.tr.text("address_balance_value")
            return
        self.amount_input.value = ""
        selected_address = selection.value.select_address
        self.tooltip.insert(self.address_selection._impl.native, selected_address)
        self.single_option.enabled = True
        self.many_option.enabled =True
        if self.many_option.value is False:
            self.update_fees_option(True)
        balance = self.addresses_storage.get_address_balance(selected_address)
        if float(balance) > 0:
            self.address_balance.style.color = WHITE
            self.format_balance = self.units.format_balance(float(balance))
            if self.rtl:
                format_balance = self.units.arabic_digits(str(self.format_balance))
            else:
                format_balance = self.format_balance
            self.address_balance.text = format_balance    
        else:
            self.address_balance.style.color = GRAY
            self.address_balance.text = self.tr.text("address_balance_value")


    async def update_address_balance(self):
        self.format_balance = 0
        while True:
            if not self.send_toggle:
                await asyncio.sleep(1)
                continue
            if self.address_selection.value is None:
                self.address_balance.text = self.tr.text("address_balance_value")
                await asyncio.sleep(1)
                continue
            selected_address = self.address_selection.value.select_address
            balance = self.addresses_storage.get_address_balance(selected_address)
            if float(balance) > 0:
                self.address_balance.style.color = WHITE
                self.format_balance = self.units.format_balance(float(balance))
                if self.rtl:
                    format_balance = self.units.arabic_digits(str(self.format_balance))
                else:
                    format_balance = self.format_balance
                self.address_balance.text = format_balance    
            else:
                self.address_balance.style.color = GRAY
                self.address_balance.text = self.tr.text("address_balance_value")
            await asyncio.sleep(3)


    async def single_option_on_change(self, switch):
        if switch.value is True:
            self.many_option.value = False
            self.single_option.style.color = YELLOW
            selected_address = self.address_selection.value.select_address
            if selected_address:
                self.update_fees_option(True)
            self.destination_box.insert(1, self.destination_input_single)
            self.destination_input_single.readonly = False
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
        
    async def many_option_on_change(self, switch):
        if switch.value is True:
            self.single_option.value = False
            self.many_option.style.color = YELLOW
            self.destination_box.style.height = 100
            self.update_fees_option(False)
            self.destination_box.insert(1, self.destination_input_many)
            self.insert(5, self.amount_options_box)
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
        if self.many_option.value is True:
            self.destination_input_many.value = ""
        elif self.single_option.value is True:
            self.destination_input_single.value = ""
        self.amount_input.value = ""

    def update_fees_option(self, option):
        if option:
            self.fees_box.style.visibility = VISIBLE
        else:
            self.fees_box.style.visibility = HIDDEN


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
        balance = self.format_balance
        if float(balance) < float(amount):
            self.check_amount_label.text = self.tr.text("check_amount_label")
        else:
            self.check_amount_label.text = ""


    def is_digit(self, value):
        if not self.amount_input.value.replace('.', '', 1).isdigit():
            self.amount_input.value = ""
        if not self.fee_input.value.replace('.', '', 1).isdigit():
            self.fee_input.value = ""


    def store_shielded_transaction(self, address, txid, amount, fee):
        tx_type = "shielded"
        category = "send"
        amount = float(amount)
        blocks = self.main.home_page.current_blocks
        timesent = int(datetime.now().timestamp())
        self.storagetxs.insert_transaction(tx_type, category, address, txid, -amount, blocks, fee, timesent)


    def send_button_click(self, button):
        selected_address = self.address_selection.value.select_address if self.address_selection.value else None
        if self.many_option.value is True:
            destination_address = self.destination_input_many.value
        else:
            destination_address = self.destination_input_single.value
        amount = self.amount_input.value
        balance = self.format_balance
        if selected_address is None:
            self.main.error_dialog(
                title=self.tr.title("selectaddress_dialog"),
                message=self.tr.message("selectaddress_dialog")
            )
            self.address_selection.focus()
            return
        elif destination_address == "":
            self.main.error_dialog(
                title=self.tr.title("missingdestination_dialog"),
                message=self.tr.message("missingdestination_dialog")
            )
            if self.many_option.value is True:
                self.destination_input_many.focus()
            else:
                self.destination_input_single.focus()
            return
        elif self.z_addresses_limit_toggle:
            self.main.error_dialog(
                title=self.tr.title("zaddresseslimit_dialog"),
                message=self.tr.message("zaddresseslimit_dialog")
            )
            return
        elif not self.is_valid_toggle:
            self.main.error_dialog(
                title=self.tr.title("invalidaddress_dialog"),
                message=self.tr.message("invalidaddress_dialog")
            )
            self.destination_input_single.focus()
            return
        elif amount == "":
            self.main.error_dialog(
                title=self.tr.title("missingamount_dialog"),
                message=self.tr.message("missingamount_dialog")
            )
            self.amount_input.focus()
            return
        elif float(balance) < float(amount):
            self.main.error_dialog(
                title=self.tr.title("insufficientbalance_dialog"),
                message=self.tr.message("insufficientbalance_dialog")
            )
            self.amount_input.focus()
            return
        asyncio.create_task(self.make_transaction())


    async def make_transaction(self):
        self.disable_send()
        selected_address = self.address_selection.value.select_address
        amount = self.amount_input.value
        txfee = self.fee_input.value
        balance = self.format_balance
        if self.many_option.value is True:
            destination_address = self.destination_input_many.value
            addresses_array = self.create_addresses_array(destination_address)
            await self.send_many(selected_address, addresses_array)
        else:
            destination_address = self.destination_input_single.value
            await self.send_single(selected_address, destination_address, amount, txfee, balance)


    async def send_single(self, selected_address, destination_address, amount, txfee, balance):
        try:
            if (float(amount)+float(txfee)) > float(balance):
                self.main.error_dialog(
                    title=self.tr.title("insufficientbalance_dialog"),
                    message=self.tr.message("insufficientbalance_dialog")
                )
                self.enable_send()
                return
            operation, _= await self.commands.z_sendMany(selected_address, destination_address, amount, txfee)
            if operation:
                self.app.console.info_log(f"Operation: {operation}")
                transaction_status, _= await self.commands.z_getOperationStatus(operation)
                transaction_status = json.loads(transaction_status)
                if isinstance(transaction_status, list) and transaction_status:
                    status = transaction_status[0].get('status')
                    if status == "failed":
                        self.operation_status.text = self.tr.text("send_failed")
                    elif status == "executing":
                        self.operation_status.text = self.tr.text("send_executing")
                    elif status == "success":
                        self.operation_status.text = self.tr.text("send_success")
                    if status == "executing" or status =="success":
                        await asyncio.sleep(1)
                        while True:
                            transaction_result, _= await self.commands.z_getOperationResult(operation)
                            transaction_result = json.loads(transaction_result)
                            if isinstance(transaction_result, list) and transaction_result:
                                status = transaction_result[0].get('status')
                                result = transaction_result[0].get('result', {})
                                txid = result.get('txid')
                                if status == "failed":
                                    self.operation_status.text = self.tr.text("send_failed")
                                    self.enable_send()
                                    self.main.error_dialog(
                                        title=self.tr.title("sendfailed_dialog"),
                                        message=self.tr.message("sendfailed_dialog")
                                    )
                                    return
                                elif status == "executing":
                                    self.operation_status.text = self.tr.text("send_executing")
                                elif status == "success":
                                    self.operation_status.text = self.tr.text("send_success")
                                    self.app.console.info_log(f"TX: {txid}")
                                if selected_address.startswith('z'):
                                    self.store_shielded_transaction(selected_address, txid, amount, txfee)
                                self.enable_send()
                                self.main.info_dialog(
                                    title=self.tr.title("sendsuccess_dialog"),
                                    message=self.tr.message("sendsuccess_dialog")
                                )
                                await self.clear_inputs()
                                return
                            await asyncio.sleep(3)
                    else:
                        self.enable_send()
                        self.main.error_dialog(
                            title=self.tr.title("sendfailed_dialog"),
                            message=self.tr.message("sendfailed_dialog")
                        )
            else:
                self.enable_send()
                self.main.error_dialog(
                    title=self.tr.title("sendfailed_dialog"),
                    message=self.tr.message("sendfailed_dialog")
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
            address_balance = self.format_balance
            if float(total_amount) > float(address_balance):
                message = self.tr.message("insufficientmany_dialog")
                self.main.error_dialog(
                    title=self.tr.title("insufficientmany_dialog"),
                    message=f"{message} {total_amount:.8f}"
                )
                return
            else:
                amount = amount_value
        transactions = [{"address": address, "amount": amount} for address in addresses]
        return transactions


    
    async def send_many(self, selected_address, destination_addresses):
        try:
            operation, _= await self.commands.z_sendToManyAddresses(selected_address, destination_addresses)
            if operation:
                self.app.console.info_log(f"Operation: {operation}")
                transaction_status, _= await self.commands.z_getOperationStatus(operation)
                transaction_status = json.loads(transaction_status)
                if isinstance(transaction_status, list) and transaction_status:
                    status = transaction_status[0].get('status')
                    if status == "failed":
                        self.operation_status.text = self.tr.text("send_failed")
                    elif status == "executing":
                        self.operation_status.text = self.tr.text("send_executing")
                    elif status == "success":
                        self.operation_status.text = self.tr.text("send_success")
                    self.operation_status.text = status
                    if status == "executing" or status =="success":
                        await asyncio.sleep(1)
                        while True:
                            transaction_result, _= await self.commands.z_getOperationResult(operation)
                            transaction_result = json.loads(transaction_result)
                            if isinstance(transaction_result, list) and transaction_result:
                                status = transaction_status[0].get('status')
                                result = transaction_result[0].get('result', {})
                                txid = result.get('txid')
                                if status == "failed":
                                    self.operation_status.text = self.tr.text("send_failed")
                                    self.enable_send()
                                    self.main.error_dialog(
                                        title=self.tr.title("sendfailed_dialog"),
                                        message=self.tr.message("sendfailed_dialog")
                                    )
                                    return
                                elif status == "executing":
                                    self.operation_status.text = self.tr.text("send_executing")
                                elif status == "success":
                                    self.operation_status.text = self.tr.text("send_success")
                                    self.app.console.info_log(f"TX: {txid}")
                                if selected_address.startswith('z'):
                                    self.store_shielded_transaction(selected_address, txid, self.amount_input.value, self.fee_input.value)
                                self.enable_send()
                                self.main.info_dialog(
                                    title=self.tr.title("sendsuccess_dialog"),
                                    message=self.tr.message("sendsuccess_dialog")
                                )
                                await self.clear_inputs()
                                return
                            await asyncio.sleep(3)

                    else:
                        self.enable_send()
                        self.main.error_dialog(
                            title=self.tr.title("sendfailed_dialog"),
                            message=self.tr.message("sendfailed_dialog")
                        )
            else:
                self.enable_send()
                self.main.error_dialog(
                    title=self.tr.title("sendfailed_dialog"),
                    message=self.tr.message("sendfailed_dialog")
                )
        except Exception as e:
            self.enable_send()
            print(f"An error occurred: {e}")

    
    def disable_send(self):
        self.operation_toggle = True
        self.send_button.enabled = False
        if self.many_option.value is True:
            self.destination_input_many.readonly = True
        elif self.single_option.value is True:
            self.destination_input_single.readonly = True
        self.amount_input.readonly = True
        self.fee_input.readonly = True


    def enable_send(self):
        self.operation_toggle = None
        self.send_button.enabled = True
        if self.many_option.value is True:
            self.destination_input_many.readonly = False
        elif self.single_option.value is True:
            self.destination_input_single.readonly = False
        self.amount_input.readonly = False
        self.fee_input.readonly = False
        self.operation_status.text = ""

    
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