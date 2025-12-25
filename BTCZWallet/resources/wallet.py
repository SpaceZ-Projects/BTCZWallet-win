
import asyncio
from pathlib import Path

from toga import (
    App, Box, Label, Window, TextInput,
    Button, ProgressBar, ImageView
)
from ..framework import (
    Cursors, FlatStyle, Forms, ProgressStyle, Os, DockStyle,
    BTCZControl, Color, FormBorderStyle, Drawing, Table,
    BorderStyle, SelectMode, AlignTable, Keys, Command, WebView
)
from toga.style.pack import Pack
from toga.colors import (
    rgb, WHITE, GRAY, RED, GREENYELLOW, BLACK
)
from toga.constants import (
    TOP, ROW, COLUMN, RIGHT, CENTER
)

from .storage import StorageAddresses



class Wallet(Box):
    def __init__(self, app:App, main:Window, settings, units, rpc, tr, font):
        super().__init__(
            style=Pack(
                direction = ROW,
                height = 120,
                alignment = TOP,
                background_color = rgb(40,43,48),
                padding =5
            )
        )

        self.app = app
        self.main = main

        self.rpc = rpc
        self.units = units
        self.settings = settings
        self.tr = tr
        self.font = font

        self.addresses_storage = StorageAddresses(self.app)

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        face_image = "images/bitcoinz_face.png"
        back_image = "images/bitcoinz_back.png"
        host = Forms.Integration.ElementHost()
        host.Dock = DockStyle.FILL
        btcz_control = BTCZControl(face_image, back_image, 2)
        host.Child = btcz_control

        self.bitcoinz_logo = Box(
            style=Pack(
                width=100,
                height=100,
                background_color = rgb(40,43,48),
                padding = self.tr.padding("bitcoinz_logo"),
            )
        )
        self.bitcoinz_logo._impl.native.Controls.Add(host)

        self.bitcoinz_title = Label(
            text=self.tr.text("bitcoinz_title"),
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = self.tr.align("bitcoinz_title"),
                padding = self.tr.padding("bitcoinz_title")
            )
        )
        self.bitcoinz_title._impl.native.Font = self.font.get(self.tr.size("bitcoinz_title"), True)

        self.bitcoinz_version = Label(
            text="",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                text_align = self.tr.align("bitcoinz_version"),
                padding = self.tr.padding("bitcoinz_version")
            )
        )
        self.bitcoinz_version._impl.native.Font = self.font.get(8, True)
        
        self.bitcoinz_title_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment=CENTER,
                flex = 1
            )
        )
        self.balances_box = Box(
            style=Pack(
                direction = COLUMN,
                padding = 10,
                alignment = RIGHT,
                flex = 1.5,
                background_color = BLACK
            )
        )

        html_path = Path(__file__).parent / "html" / "wallet.html"
        self.balances_output = WebView(
            app=self.app,
            content=html_path,
            background_color=Color.rgb(40,43,48)
        )
        self.balances_box._impl.native.Controls.Add(self.balances_output.control)
        
        if self.rtl:
            self.add(
                self.balances_box,
                self.bitcoinz_title_box,
                self.bitcoinz_logo
            )
        else:
            self.add(
                self.bitcoinz_logo,
                self.bitcoinz_title_box,
                self.balances_box
            )
        self.bitcoinz_title_box.add(
            self.bitcoinz_title,
            self.bitcoinz_version
        )

        self.app.loop.create_task(self.get_node_version())
        self.app.loop.create_task(self.update_total_balances())
        self.app.loop.create_task(self.update_transparent_addresses())
        self.app.loop.create_task(self.update_shielded_addresses())


    async def get_node_version(self):
        result, _ = await self.rpc.getInfo()
        if not result:
            return
        subversion = result.get("subversion", "")
        build = result.get("build", "")
        clean = subversion.strip("/")
        if ":" in clean:
            name, version = clean.split(":", 1)
            formatted_version = f"{name} v {version}"
        else:
            formatted_version = f"v {clean}" if clean else "unknown"
        if build and "-" in build:
            build_suffix = build.split("-", 1)[1]
        else:
            build_suffix = build or "unknown"
        self.bitcoinz_version.text = (
            f"Core : {formatted_version} | Build : {build_suffix}"
        )


    async def update_total_balances(self):
        self.app.console.event_log(f"✔: Total balances")
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            balances,_ = await self.rpc.z_getTotalBalance()
            if balances:
                totalbalance = self.units.format_balance(float(balances.get('total')))
                transparentbalance = self.units.format_balance(float(balances.get('transparent')))
                shieldedbalance = self.units.format_balance(float(balances.get('private')))
                if self.rtl:
                    totalbalance = self.units.arabic_digits(totalbalance)
                    transparentbalance = self.units.arabic_digits(transparentbalance)
                    shieldedbalance = self.units.arabic_digits(shieldedbalance)
                if self.settings.hidden_balances():
                    totalbalance = "*.********"
                    transparentbalance = "*.********"
                    shieldedbalance = "*.********"
                js_code = f'setBalances("{totalbalance}", "{transparentbalance}", "{shieldedbalance}");'
                self.balances_output.control.CoreWebView2.ExecuteScriptAsync(js_code)
            
            unconfirmed_balance,_ = await self.rpc.getUnconfirmedBalance()
            unconfirmed = self.units.format_balance(float(unconfirmed_balance))
            if float(unconfirmed) > 0:
                if self.rtl:
                    unconfirmed = self.units.arabic_digits(unconfirmed)
                if self.settings.hidden_balances():
                    unconfirmed = "*.********"
            else:
                unconfirmed = 0
            js_unconfirmed = f'setUnconfirmedBalance("{unconfirmed}");'
            self.balances_output.control.CoreWebView2.ExecuteScriptAsync(js_unconfirmed)
            
            await asyncio.sleep(4)


    async def update_transparent_addresses(self):
        self.app.console.event_log("✔: Sync transparent addresses")
        address_type = "transparent"
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            stored_addresses = self.addresses_storage.get_addresses(address_type=address_type)
            stored_dict = {data[2]: data[3] for data in stored_addresses}

            addresses_data,_ = await self.rpc.ListAddresses()
            addresses_group,_ = await self.rpc.listAddressgroupPings()

            global_balance_change = False

            for group in addresses_group:
                for entry in group:
                    address = entry[0]
                    balance = entry[1] if len(entry) > 1 else 0.0

                    if address not in addresses_data:
                        is_change_address = True
                    else:
                        is_change_address = None
                    if address not in stored_dict:
                        self.addresses_storage.insert_address(address_type, is_change_address, address, balance)
                    else:
                        old_balance = stored_dict[address]
                        if old_balance != balance:
                            self.addresses_storage.update_balance(address, balance)
                            global_balance_change = True

            stored_addresses = self.addresses_storage.get_addresses(address_type=address_type)
            stored_set = {data[2] for data in stored_addresses}

            for address in addresses_data:
                if address not in stored_set:
                    option = "insert"
                else:
                    option = "update"
                await self.insert_address(address_type, address, option)
            
            if global_balance_change:
                self.main.mobile_server.broker.push("update_balances")

            await asyncio.sleep(10)


    async def update_shielded_addresses(self):
        self.app.console.event_log("✔: Sync shielded addresses")
        address_type = "shielded"

        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue

            stored_addresses = self.addresses_storage.get_addresses(address_type=address_type)
            stored_dict = {data[2]: data[3] for data in stored_addresses}

            addresses_data, _ = await self.rpc.z_listAddresses()

            global_balance_change = False

            if addresses_data:
                for address_info in addresses_data:
                    if isinstance(address_info, dict):
                        address = address_info.get("address")
                        balance = address_info.get("balance", 0.0)
                    else:
                        address = address_info
                        balance, _ = await self.rpc.z_getBalance(address)
                    if address not in stored_dict:
                        option = "insert"
                        self.addresses_storage.insert_address(address_type, None, address, balance)
                    else:
                        option = "update"
                        old_balance = stored_dict[address]
                        if old_balance != balance:
                            self.addresses_storage.update_balance(address, balance)
                            global_balance_change = True

                    await self.insert_address(address_type, address, option, balance)

                if global_balance_change:
                    self.main.mobile_server.broker.push("update_balances")

            await asyncio.sleep(20)


    async def insert_address(self, address_type, address, option, balance=None):
        if balance is None:
            balance, _ = await self.rpc.z_getBalance(address)

        if option == "insert":
            self.addresses_storage.insert_address(address_type, None, address, balance)
        elif option == "update":
            self.addresses_storage.update_balance(address, balance)





class AddAddress(Window):
    def __init__(self, main:Window, book_window:Window, utils, rpc, font, tr):
        super().__init__(
            size = (550, 200),
            resizable=False
        )

        self.main = main
        self.book_window = book_window
        self.utils = utils
        self.rpc = rpc
        self.font = font
        self.tr = tr

        self.storage = StorageAddresses(self.app)
        self.is_valid_toggle = None

        self.title = "Add Address"
        position_center = self.utils.window_center_to_parent(self.book_window, self)
        self.position = position_center
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.name_label = Label(
            text="Name :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1
            )
        )
        self.name_label._impl.native.Font = self.font.get(11, True)

        self.name_input = TextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                width = 250,
                padding = (0,150,0,0)
            )
        )
        self.name_input._impl.native.Font = self.font.get(11, True)

        self.name_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                flex = 1,
                padding = (10,0,0,0)
            )
        )

        self.address_label = Label(
            text="Address :",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                flex = 1
            )
        )
        self.address_label._impl.native.Font = self.font.get(11, True)

        self.address_input = TextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                width = 350
            ),
            on_change=self.is_valid_address
        )
        self.address_input._impl.native.Font = self.font.get(11, True)

        self.is_valid = ImageView(
            style=Pack(
                background_color = rgb(30,33,36),
                width = 30,
                height = 30,
                padding = (0,10,0,10)
            )
        )

        self.address_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                flex = 1
            )
        )

        self.cancel_button = Button(
            text=self.tr.text("cancel_button"),
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                width = 100
            ),
            on_press=self.close_add_window
        )
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.confirm_button = Button(
            text=self.tr.text("confirm_button"),
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (0,0,0,20),
                width = 100
            ),
            on_press=self.confirm_address
        )
        self.confirm_button._impl.native.Font = self.font.get(self.tr.size("confirm_button"), True)
        self.confirm_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.confirm_button._impl.native.MouseEnter += self.confirm_button_mouse_enter
        self.confirm_button._impl.native.MouseLeave += self.confirm_button_mouse_leave

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER,
                background_color = rgb(30,33,36),
                height = 40,
                padding = (15,0,10,0)
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.name_box,
            self.address_box,
            self.buttons_box
        )
        self.name_box.add(
            self.name_label,
            self.name_input
        )
        self.address_box.add(
            self.address_label,
            self.address_input,
            self.is_valid
        )
        self.buttons_box.add(
            self.cancel_button,
            self.confirm_button
        )


    async def confirm_address(self, button):
        name = self.name_input.value.strip()
        address = self.address_input.value.strip()
        if not name or not address:
            self.error_dialog(
                title="Missing Requirments",
                message="Name and Address is required"
            )
            return
        elif not self.is_valid_toggle:
            self.error_dialog(
                title=self.tr.title("invalidaddress_dialog"),
                message=self.tr.message("invalidaddress_dialog")
            )
            return
        address_book = self.storage.get_address_book("address")
        if address in address_book:
            self.error_dialog(
                title="Address Exists",
                message="This address is already exists"
            )
            return
        address_book = self.storage.get_address_book("name")
        if name in address_book:
            self.error_dialog(
                title="Name Exists",
                message="This name is already exists"
            )
            return
        self.storage.insert_book(name, address)
        self.main.mobile_server.broker.push("update_book")
        self.close()
        self.book_window.realod_address_book()
        

    async def is_valid_address(self, input):
        address = self.address_input.value.strip()
        if not address:
            self.is_valid.image = None
            return
        if address.startswith("t"):
            result, _ = await self.rpc.validateAddress(address)
        elif address.startswith("z"):
            result, _ = await self.rpc.z_validateAddress(address)
        else:
            self.is_valid.image = "images/notvalid.png"
            return
        if result is not None:
            is_valid = result.get('isvalid')
            if is_valid is True:
                self.is_valid.image = "images/valid.png"
                self.is_valid_toggle = True
            elif is_valid is False:
                self.is_valid.image = "images/notvalid.png"
                self.is_valid_toggle = None


    def confirm_button_mouse_enter(self, sender, event):
        self.confirm_button.style.color = BLACK
        self.confirm_button.style.background_color = GREENYELLOW

    def confirm_button_mouse_leave(self, sender, event):
        self.confirm_button.style.color = GRAY
        self.confirm_button.style.background_color = rgb(30,33,36)


    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)


    def close_add_window(self, button):
        self.close()
        self.app.current_window = self.book_window

            


class AddressBook(Window):
    def __init__(self, main:Window ,utils, rpc, font, tr, option = None, size = None, location = None):
        super().__init__(
            resizable=False
        )

        self.main = main
        self.utils = utils
        self.rpc = rpc
        self.font = font
        self.tr = tr
        self.option = option

        self.storage = StorageAddresses(self.app)

        self.no_addresses_toggle = None

        self.title = "Address Book"
        self._impl.native.Icon = self.window_icon("images/Book.ico")
        self.size = (700,400)

        position_center = self.utils.window_center_to_parent(self.main, self)
        self.position = position_center
        self.on_close = self.close_book_window

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        background_color = (30,33,36)
        multiselect = False
        self.column_widths={0:150,1:538}
        selection_backcolors={
            0:Color.rgb(15,15,15),
            1:Color.rgb(40,43,48)
        }

        if option:
            self.size = size
            background_color = (25,25,25)
            self.column_widths={0:size[0] - 12}
            selection_backcolors={
                0:Color.rgb(40,43,48)
            }
            self._impl.native.FormBorderStyle = FormBorderStyle.NONE
            self._impl.native.Location = Drawing.Point(*location)
            self._impl.native.ShowInTaskbar = False
            self._impl.native.Deactivate += self._close_address_book

            if option == "many":
                multiselect = True


        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(*background_color),
                flex = 1,
                alignment = CENTER
            )
        )

        self.add_button = Button(
            text="Add Address",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 100,
                padding =(5,10,0,10)
            ),
            on_press=self.show_add_window
        )
        self.add_button._impl.native.Font = self.font.get(9, True)
        self.add_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.add_button._impl.native.MouseEnter += self.add_button_mouse_enter
        self.add_button._impl.native.MouseLeave += self.add_button_mouse_leave

        self.empty_label = Label(
            text="",
            style=Pack(
                background_color = rgb(40,43,48),
                flex = 1
            )
        )

        self.menu_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 40,
                alignment = CENTER
            )
        )

        self.no_addresses_label = Label(
            text="No addresses available",
            style=Pack(
                color = GRAY,
                background_color = rgb(*background_color),
                text_align = CENTER
            )
        )
        self.no_addresses_label._impl.native.Font = self.font.get(10, True)

        self.empty_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(*background_color),
                flex = 1,
                alignment = CENTER
            )
        )

        self.book_table = Table(
            background_color=Color.rgb(*background_color),
            cell_color=Color.rgb(30,33,36),
            text_color=Color.GRAY,
            multiselect=multiselect,
            dockstyle=DockStyle.FILL,
            align=AlignTable.MIDCENTER,
            row_visible=False,
            column_visible=False,
            row_heights=35,
            column_count=2,
            select_mode=SelectMode.FULLROWSELECT,
            borderstyle=BorderStyle.NONE,
            readonly=True,
            selection_backcolors=selection_backcolors,
            cell_font=self.font.get(10, True),
            on_double_click=self.on_table_double_click,
        )
        self.book_table.KeyDown += self.table_keydown

        self.book_box = Box(
            style=Pack(
                flex = 1,
                background_color = rgb(*background_color),
                padding = (5,5,0,5)
            )
        )

        self.content = self.main_box
        self.book_box._impl.native.Controls.Add(self.book_table)
        if not option:
            self.main_box.add(
                self.menu_box,
            )
            self.menu_box.add(
                self.add_button,
                self.empty_label
            )

        self.empty_box.add(
            self.no_addresses_label
        )


        self.insert_book_menustrip()
        self.load_address_book()


    def insert_book_menustrip(self):
        if not self.option:
            self.edit_address_cmd = Command(
                title="Remove address",
                color=Color.WHITE,
                background_color=Color.rgb(30,33,36),
                action=self.remove_address,
                icon="images/remove_i.ico",
                mouse_enter=self.edit_address_cmd_mouse_enter,
                mouse_leave=self.edit_address_cmd_mouse_leave,
                font=self.font.get(9)
            )
            self.book_table.commands = [self.edit_address_cmd]
    
    def load_address_book(self):
        book = []
        address_book = self.storage.get_address_book()
        if not address_book:
            self.main_box.add(
                self.empty_box
            )
            self.no_addresses_toggle = True
            return
        self.main_box.add(
            self.book_box
        )
        for data in address_book:
            name = data[0]
            address = data[1]
            if self.option:
                row = {
                    "Name": name
                }
            else:
                row = {
                    "Name": name,
                    "Address": address
                }
            book.append(row)
        self.book_table.data_source = book
        self.book_table.column_widths = self.column_widths


    def realod_address_book(self):
        book = []
        if self.no_addresses_toggle:
            self.main_box.remove(
                self.empty_box
            )
            self.main_box.add(
                self.book_box
            )
            self.no_addresses_toggle = None
        address_book = self.storage.get_address_book()
        if not address_book:
            self.main_box.remove(
                self.book_box
            )
            self.main_box.add(
                self.empty_box
            )
            self.no_addresses_toggle = True
            return
        for data in address_book:
            name = data[0]
            address = data[1]
            row = {
                    "Name": name,
                    "Address": address
                }
            book.append(row)
        self.book_table.data_source = book
        self.book_table.column_widths = self.column_widths


    def show_add_window(self, button):
        add_window = AddAddress(self.main, self, self.utils, self.rpc, self.font, self.tr)
        add_window._impl.native.ShowDialog(self._impl.native)


    def remove_address(self):
        selected_cells = self.book_table.selected_cells
        for cell in selected_cells:
            if cell.ColumnIndex == 1:
                address = cell.Value
                self.storage.delete_address_book(address)
                self.main.mobile_server.broker.push("update_book")
        self.realod_address_book()


    def on_table_double_click(self, sender, event):
        if self.option == "single":
            row_index = event.RowIndex
            name = sender.Rows[row_index].Cells[0].Value
            address = self.storage.get_address_book(name=name)
            self.main.send_page.destination_input_single.value = address[0]
            self.close()


    def table_keydown(self, sender, e):
        if not self.option:
            if e.KeyCode == Keys.F5:
                self.realod_address_book()
                
        elif self.option == "many":
            selected_cells = self.book_table.selected_cells
            if len(selected_cells) > 1:
                if e.KeyCode == Keys.Enter:
                    self.main.send_page.destination_input_many.value = ""
                    for cell in selected_cells:
                        name = cell.Value
                        address = self.storage.get_address_book(name=name)
                        self.main.send_page.destination_input_many.value += f"{address[0]}\n"
                    self.close()


    def add_button_mouse_enter(self, sender, event):
        self.add_button.style.color = BLACK
        self.add_button.style.background_color = GREENYELLOW

    def add_button_mouse_leave(self, sender, event):
        self.add_button.style.color = GRAY
        self.add_button.style.background_color = rgb(30,33,36)

    def edit_address_cmd_mouse_enter(self):
        self.edit_address_cmd.icon = "images/remove_a.ico"
        self.edit_address_cmd.color = Color.BLACK

    def edit_address_cmd_mouse_leave(self):
        self.edit_address_cmd.icon = "images/remove_i.ico"
        self.edit_address_cmd.color = Color.WHITE


    def window_icon(self, path):
        icon_path = Os.Path.Combine(str(self.app.paths.app), path)
        icon = Drawing.Icon(icon_path)
        return icon


    def _close_address_book(self, sender, event):
        try:
            self.close()
        except Exception:
            pass

    def close_book_window(self, widget):
        self.main.book_toggle = None
        self.close()
        self.app.current_window = self.main
        


class ImportKey(Window):
    def __init__(self, main:Window, settings, utils, rpc, tr, font):
        super().__init__(
            size = (600, 150),
            resizable= False
        )
        
        self.main = main
        self.utils = utils
        self.rpc = rpc
        self.settings = settings
        self.tr = tr
        self.font = font

        self.title = self.tr.title("importkey_window")
        position_center = self.utils.window_center_to_parent(self.main, self)
        self.position = position_center
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.info_label = Label(
            text=self.tr.text("info_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                padding_top = 5
            )
        )
        self.info_label._impl.native.Font = self.font.get(11)

        self.key_input = TextInput(
            style=Pack(
                color = WHITE,
                text_align= CENTER,
                background_color = rgb(30,33,36),
                flex = 3,
                padding_left = 10
            )
        )
        self.key_input._impl.native.Font = self.font.get(self.tr.size("key_input"), True)
        
        self.import_button = Button(
            text=self.tr.text("import_button"),
            style=Pack(
                color= GRAY,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (0,10,0,10)
            ),
            on_press=self.import_button_click
        )
        self.import_button._impl.native.Font = self.font.get(self.tr.size("import_button"), True)
        self.import_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.import_button._impl.native.MouseEnter += self.import_button_mouse_enter
        self.import_button._impl.native.MouseLeave += self.import_button_mouse_leave

        self.progress_bar = ProgressBar(
            style=Pack(
                height= 25,
                flex = 1,
                padding = (0,10,0,10)
            )
        )
        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (5,0,10,0)
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
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.input_box,
            self.cancel_button
        )
        self.input_box.add(
            self.key_input,
            self.import_button
        )

    def import_button_click(self, button):
        if not self.key_input.value:
            self.error_dialog(
                title=self.tr.title("missingkey_dialog"),
                message=self.tr.message("missingkey_dialog")
            )
            self.key_input.focus()
            return
        self.input_box.remove(
            self.import_button
        )
        self.input_box.add(
            self.progress_bar
        )
        self.key_input.readonly = True
        self.cancel_button.enabled = False
        self.main.import_key_toggle = True
        self.app.loop.create_task(self.import_private_key())


    async def import_private_key(self):
        def on_result(widget, result):
            if result is None:
                self.main.import_key_toggle = None
                self.input_box.remove(
                    self.progress_bar
                )
                self.input_box.add(
                    self.import_button
                )
                self.key_input.readonly = False
                self.cancel_button.enabled = True
        key = self.key_input.value.strip()
        _, error_message = await self.rpc.ImportPrivKey(key)
        if error_message:
            _, error_message = await self.rpc.z_ImportKey(key)
            if error_message:
                self.error_dialog(
                    title=self.tr.title("invalidkey_dialog"),
                    message=self.tr.message("invalidkey_dialog"),
                    on_result=on_result
                )
                return     
        await self.update_import_window()


    async def update_import_window(self):
        while True:
            result,_ = await self.rpc.getInfo()
            if result:
                self.close()
                self.main.import_key_toggle = None
                self.main.transactions_page.reload_transactions()
                self.main.receive_page.reload_addresses()
                self.main.mining_page.reload_addresses()
                self.app.current_window = self.main
                return
            
            await asyncio.sleep(5)


    def import_button_mouse_enter(self, sender, event):
        self.import_button.style.color = BLACK
        self.import_button.style.background_color = GREENYELLOW

    def import_button_mouse_leave(self, sender, event):
        self.import_button.style.color = GRAY
        self.import_button.style.background_color = rgb(30,33,36)

    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)

    def close_import_key(self, button):
        self.close()
        self.app.current_window = self.main




class ImportWallet(Window):
    def __init__(self, main:Window, settings, utils, rpc, tr, font):
        super().__init__(
            size = (600, 150),
            resizable= False
        )
        
        self.main = main
        self.utils = utils
        self.rpc = rpc
        self.settings = settings
        self.tr = tr
        self.font = font

        self.title = self.tr.title("importwallet_window")
        position_center = self.utils.window_center_to_parent(self.main, self)
        self.position = position_center
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.info_label = Label(
            text=self.tr.text("info_label"),
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                padding_top = 5
            )
        )
        self.info_label._impl.native.Font = self.font.get(11)

        self.file_input = TextInput(
            value=self.tr.text("file_input"),
            style=Pack(
                color = GRAY,
                text_align= CENTER,
                background_color = rgb(40,43,48),
                flex = 3,
                padding_left = 10
            ),
            readonly=True
        )
        self.file_input._impl.native.Font = self.font.get(self.tr.size("file_input"), True)
        self.file_input._impl.native.AllowDrop = True
        self.file_input._impl.native.Click += self.select_wallet_file
        self.file_input._impl.native.DragEnter += Forms.DragEventHandler(self.on_drag_enter)
        self.file_input._impl.native.DragDrop += Forms.DragEventHandler(self.on_drag_drop)
        self.file_input._impl.native.Cursor = Cursors.HAND
        
        self.import_button = Button(
            text=self.tr.text("import_button"),
            style=Pack(
                color= GRAY,
                background_color = rgb(30,33,36),
                flex = 1,
                padding = (0,10,0,10)
            ),
            on_press = self.import_button_click
        )
        self.import_button._impl.native.Font = self.font.get(self.tr.size("import_button"), True)
        self.import_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.import_button._impl.native.MouseEnter += self.import_button_mouse_enter
        self.import_button._impl.native.MouseLeave += self.import_button_mouse_leave

        self.progress_bar = ProgressBar(
            style=Pack(
                height= 25,
                flex = 1,
                padding = (0,10,0,10)
            )
        )
        self.progress_bar._impl.native.Style = ProgressStyle.MARQUEE

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (5,0,10,0)
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
            on_press=self.close_import_file
        )
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.input_box,
            self.cancel_button
        )
        self.input_box.add(
            self.file_input,
            self.import_button
        )

    def select_wallet_file(self, sender, event):
        def on_result(widget, result):
            if result:
                self.file_input.value = result
                self.file_input.style.color = WHITE
        self.open_file_dialog(
            title=self.tr.title("selectfile_dialog"),
            on_result=on_result
        )
        

    def on_drag_enter(self, sender, event):
        if event.Data.GetDataPresent("FileDrop"):
            event.Effect = Forms.DragDropEffects.Copy
        else:
            event.Effect = Forms.DragDropEffects(0)


    def on_drag_drop(self, sender, event):
        files = event.Data.GetData("FileDrop")
        if files and len(files) > 0:
            self.file_input.value = files[0]
            self.file_input.style.color = WHITE


    def import_button_click(self, button):
        if self.file_input.value == self.tr.text("file_input"):
            self.error_dialog(
                title=self.tr.title("missingfile_dialog"),
                message=self.tr.message("missingfile_dialog")
            )
            return

        extension = Os.Path.GetExtension(self.file_input.value)
        if extension:
            self.error_dialog(
                title=self.tr.title("invalidfile_dialog"),
                message=self.tr.message("invalidfile_dialog")
            )
            return
        
        self.input_box.remove(
            self.import_button
        )
        self.input_box.add(
            self.progress_bar
        )
        self.file_input._impl.native.Click -= self.select_wallet_file
        self.file_input._impl.native.AllowDrop = False
        self.cancel_button.enabled = False
        self.main.import_key_toggle = True
        self.app.loop.create_task(self.import_wallet_file())


    async def import_wallet_file(self):
        file_path = self.file_input.value
        await self.rpc.z_ImportWallet(file_path) 
        await self.update_import_window()


    async def update_import_window(self):
        while True:
            result,_ = await self.rpc.getInfo()
            if result:
                self.close()
                self.main.import_key_toggle = None
                self.main.transactions_page.reload_transactions()
                self.main.receive_page.reload_addresses()
                self.main.mining_page.reload_addresses()
                return
            
            await asyncio.sleep(5)


    def import_button_mouse_enter(self, sender, event):
        self.import_button.style.color = BLACK
        self.import_button.style.background_color = GREENYELLOW

    def import_button_mouse_leave(self, sender, event):
        self.import_button.style.color = GRAY
        self.import_button.style.background_color = rgb(30,33,36)

    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)

    def close_import_file(self, button):
        self.close()
        self.app.current_window = self.main