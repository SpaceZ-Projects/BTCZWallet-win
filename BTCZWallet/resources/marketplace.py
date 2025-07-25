
import asyncio
import uuid
from datetime import datetime

from toga import (
    Window, Box, Button, Label, TextInput, ImageView,
    MultilineTextInput, Selection, ScrollContainer, App,
    NumberInput
)
from ..framework import (
    Sys, Drawing, FlatStyle, Forms, Cursors, Os, RichLabel,
    ToolTip, Command, Color, ClipBoard, DockStyle, BorderStyle,
    run_async
)
from toga.constants import COLUMN, CENTER, ROW, LEFT
from toga.style import Pack
from toga.colors import (
    rgb, GRAY, WHITE, RED, BLACK, GREENYELLOW,
    YELLOW
)

from .storage import StorageMarket, StorageMessages



class DisplayImage(Window):
    def __init__(self, main, utils, font, image):
        super().__init__(
            resizable=False
        )

        self.main = main
        self.font = font

        width, height = image.Width, image.Height
        screen_width, screen_height = self.app.screens[0].size
        max_width, max_height = screen_width - 150, screen_height - 150

        if width > max_width or height > max_height:
            aspect_ratio = width / height
            if width / max_width > height / max_height:
                width = max_width
                height = int(max_width / aspect_ratio)
            else:
                height = max_height
                width = int(max_height * aspect_ratio)
        

        self.title = "Image View"
        self.size = (width, height)
        self._impl.native.BackColor = Color.rgb(30,33,36)
        position_center = utils.windows_screen_center(self.size)
        self.position = position_center
        self._impl.native.ControlBox = False

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = CENTER,
                background_color = rgb(30,33,36)
            )
        )

        self.image_view = ImageView(
            image=image,
            style=Pack(
                background_color = rgb(30,33,36)
            )
        )

        self.close_button = Button(
            text="Close",
            style=Pack(
                color = RED,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (10,0,10,0),
                width = 100
            ),
            on_press=self.close_image_view
        )
        self.close_button._impl.native.Font = self.font.get(9, True)
        self.close_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.close_button._impl.native.MouseEnter += self.close_button_mouse_enter
        self.close_button._impl.native.MouseLeave += self.close_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.image_view,
            self.close_button
        )


    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = BLACK
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = RED
        self.close_button.style.background_color = rgb(30,33,36)

    def close_image_view(self, button):
        self.close()
        self.app.current_window = self.main




class PlaceOrder(Window):
    def __init__(self, main:Window, item_view:Box, utils, tr, font, item, order_qauntity, total_price, market, contact_id):
        super().__init__(
            resizable=False,
            closable=False
        )

        self.main = main
        self.item_view = item_view
        self.utils = utils
        self.tr = tr
        self.font = font

        self.title = "Confirm Order"
        self.size = (550,250)
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self._impl.native.ControlBox = False

        self.item_id = item.get('id')
        self.item_title = item.get('title')
        self.order_quantity = order_qauntity
        self.total_price = total_price
        self.market = market
        self.contact_id = contact_id

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = CENTER,
                background_color = rgb(30,33,36)
            )
        )

        self.title_label = Label(
            text=f"Item Title :\n{self.item_title}",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                padding = (10,0,0,0)
            )
        )
        self.title_label._impl.native.Font = self.font.get(12, True)

        self.quantity_label = Label(
            text=f"Quantity : {self.order_quantity}",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                padding = (25,0,0,0)
            )
        )
        self.quantity_label._impl.native.Font = self.font.get(11, True)

        self.total_label = Label(
            text=f"Total Price : {self.total_price} BTCZ",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = CENTER,
                padding = (10,0,0,0)
            )
        )
        self.total_label._impl.native.Font = self.font.get(11, True)

        self.comment_label = Label(
            text=f"Comment :",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                text_align = LEFT,
                padding = (10,0,0,10)
            )
        )
        self.comment_label._impl.native.Font = self.font.get(11, True)

        self.comment_input = MultilineTextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                padding = (0,10,5,10)
            )
        )
        self.comment_input._impl.native.Font = self.font.get(10, True)

        self.order_info = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1,
                padding = 5
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
            on_press=self.close_confirm_window
        )
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.place_order_button = Button(
            text="Place Order",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (0,0,10,20),
                width = 100
            ),
            on_press=self.place_order
        )
        self.place_order_button._impl.native.Font = self.font.get(9, True)
        self.place_order_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.place_order_button._impl.native.MouseEnter += self.place_order_button_mouse_enter
        self.place_order_button._impl.native.MouseLeave += self.place_order_button_mouse_leave

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER,
                background_color = rgb(30,33,36)
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.order_info,
            self.buttons_box
        )
        self.order_info.add(
            self.title_label,
            self.quantity_label,
            self.total_label,
            self.comment_label,
            self.comment_input
        )
        self.buttons_box.add(
            self.cancel_button,
            self.place_order_button
        )


    def place_order(self, button):
        button.enabled = False
        self.cancel_button.enabled = False
        run_async(self.make_request())

    async def make_request(self):
        url = f"http://{self.market[0]}/place_order"
        params = {
            "id": str(self.item_id),
            "contact_id": str(self.contact_id),
            "total_price": str(self.total_price),
            "quantity": str(self.order_quantity),
            "comment": str(self.comment_input.value.strip())
        }
        result = await self.utils.make_request(self.contact_id, url, params)
        if not result or "error" in result:
            self.cancel_button.enabled = True
            self.place_order_button.enabled = True
            return
        self.close()
        self.app.current_window = self.main
        self.app.add_background_task(self.item_view.result_dialog)


    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)


    def place_order_button_mouse_enter(self, sender, event):
        self.place_order_button.style.color = BLACK
        self.place_order_button.style.background_color = GREENYELLOW

    def place_order_button_mouse_leave(self, sender, event):
        self.place_order_button.style.color = GRAY
        self.place_order_button.style.background_color = rgb(30,33,36)


    def close_confirm_window(self, button):
        self.close()
        self.app.current_window = self.main




class ItemView(Box):
    def __init__(self, app:App, main:Window, utils, units, tr, font, item, market, contact_id):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 55,
                alignment = CENTER
            )
        )

        self.app = app
        self.main = main
        self.utils = utils
        self.units = units
        self.tr = tr
        self.font = font
        self.item = item

        self.item_id = item.get('id')
        self.item_title = item.get('title')
        self.image_url = item.get('image')
        item_description = item.get('description')
        self.item_price = item.get('price')
        self.item_currency = item.get('currency')

        self.market = market
        self.contact_id = contact_id
        self.image_stream = None

        self.item_image = ImageView(
            image="images/loading_image.gif",
            style=Pack(
                background_color = rgb(40,43,48),
                width = 45,
                height = 45,
                padding = (2,15,0,5)
            )
        )
        self.item_image._impl.native.Click += self.show_item_image

        self.title_label = Label(
            text=self.item_title[:75],
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 3
            )
        )
        self.title_label._impl.native.Font = self.font.get(10, True)

        self.price_label = Label(
            text=self.item_price,
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.price_label._impl.native.Font = self.font.get(10, True)

        self.currency_label = Label(
            text=self.item_currency,
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.currency_label._impl.native.Font = self.font.get(10, True)

        self.view_button = Button(
            text="View",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 80,
                padding = (0,15,0,0)
            ),
            on_press=self.show_item
        )
        self.view_button._impl.native.Font = self.font.get(9, True)
        self.view_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.view_button._impl.native.MouseEnter += self.view_button_mouse_enter
        self.view_button._impl.native.MouseLeave += self.view_button_mouse_leave

        self.item_info = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                height = 50,
                alignment = CENTER
            )
        )

        self.description_label = Label(
            text=f"Description :",
            style=Pack(
                color = GRAY,
                background_color=rgb(30,33,36)
            )
        )
        self.description_label._impl.native.Font = font=self.font.get(11, True)

        self.description_value = RichLabel(
            text=f"{item_description}",
            font=self.font.get(10, True),
            wrap=True,
            readonly=True,
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            dockstyle=DockStyle.FILL,
            borderstyle=BorderStyle.NONE
        )

        self.description_value_box = Box(
            style=Pack(
                background_color=rgb(30,33,36),
                padding = (5,0,0,5),
                flex = 1
            )
        )

        self.description_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(30,33,36),
                padding = (5,0,0,5),
                flex = 2
            )
        )

        self.quantity_label = Label(
            text="Quantity :",
            style=Pack(
                color = WHITE,
                background_color=rgb(30,33,36)
            )
        )
        self.quantity_label._impl.native.Font = self.font.get(10, True)

        self.quantity_input = NumberInput(
            value=1,
            step=1,
            min=1,
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                width = 80,
                padding = (0,0,0,10)
            ),
            on_change=self.calculate_total_price
        )
        self.quantity_input._impl.native.Font = self.font.get(11, True)

        self.quantity_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (10,0,0,0)
            )
        )

        self.available_label = Label(
            text=f"Available :",
            style=Pack(
                color = GREENYELLOW,
                background_color=rgb(30,33,36),
                padding = (3,0,0,82)
            )
        )
        self.available_label._impl.native.Font = self.font.get(8.5, True)

        self.available_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36)
            )
        )

        self.total_label = Label(
            text="Total Price (BTCZ)",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(30,33,36)
            )
        )
        self.total_label._impl.native.Font = self.font.get(11, True)

        self.total_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(30,33,36)
            )
        )
        self.total_value._impl.native.Font = self.font.get(11, True)

        self.total_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.buy_button = Button(
            text="Buy",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 100,
                padding = (0,0,10,0)
            ),
            on_press=self.confirm_order
        )
        self.buy_button._impl.native.Font = self.font.get(9, True)
        self.buy_button._impl.native.FlatStyle = FlatStyle.FLAT

        self.item_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                flex = 1
            )
        )

        self.item_options = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                padding = (10,5,5,10),
                height = 200,
                alignment = CENTER
            )
        )

        self.add(
            self.item_info
        )
        self.item_info.add(
            self.item_image,
            self.title_label,
            self.price_label,
            self.currency_label,
            self.view_button
        )
        self.item_box.add(
            self.quantity_box,
            self.available_box,
            self.total_box,
            self.buy_button
        )
        self.quantity_box.add(
            self.quantity_label,
            self.quantity_input
        )
        self.available_box.add(
            self.available_label
        )
        self.total_box.add(
            self.total_label,
            self.total_value
        )

        self.app.add_background_task(self.display_image)


    async def display_image(self, widget):
        if not self.image_url:
            self.item_image.image = "images/image_not_found.png"
            return
        result = await self.utils.make_request(self.contact_id, self.image_url, return_bytes=True)
        if result:
            stream = Os.MemoryStream(result)
            self.image_stream = Drawing.Image.FromStream(stream)
            self.item_image._impl.native.Image = self.image_stream
        else:
            if not self.main.marketplace_toggle:
                return
            await asyncio.sleep(3)
            self.app.add_background_task(self.display_image)


    async def show_item(self, button):
        self.view_button.enabled = False
        params = {"get": "quantity"}
        url = f"http://{self.market[0]}/item/{self.item_id}"
        result = await self.utils.make_request(self.contact_id, url, params)
        if "error" in result:
            self.view_button.enabled = True
            return
        self.item_quantity = result.get('quantity')
        if self.item_quantity <= 0:
            self.available_label.style.color = RED
        self.available_label.text = f"Available : {self.item_quantity}"
        self.style.height = 280
        self.view_button.text = "Hide"
        self.view_button.style.color = BLACK
        self.view_button.style.background_color = rgb(114,137,218)
        self.add(self.item_options)
        self.item_options.add(self.description_box, self.item_box)
        self.description_box.add(self.description_label, self.description_value_box)
        self.description_value_box._impl.native.Controls.Add(self.description_value)
        if self.item_currency == "BTCZ":
            self.total_value.text = self.units.format_balance(self.item_price)
            self.calculated_price = self.item_price
        else:
            url = f"http://{self.market[0]}/price"
            result = await self.utils.make_request(self.contact_id, url)
            btcz_price = result.get('price')
            item_price = self.item_price / float(btcz_price)
            self.total_value.text =  self.units.format_balance(item_price)
            self.calculated_price = item_price
        quantity = int(self.quantity_input.value)
        self.total_price = self.calculated_price * quantity
        self.view_button.on_press = self.hide_item_click
        self.view_button.enabled = True
        self.view_button._impl.native.MouseEnter -= self.view_button_mouse_enter
        self.view_button._impl.native.MouseLeave -= self.view_button_mouse_leave


    def hide_item_click(self, button):
        self.hide_item()
    
    def hide_item(self):
        self.view_button.enabled = False
        self.style.height = 55
        self.view_button.text = "View"
        self.view_button.style.color = GRAY
        self.view_button.style.background_color = rgb(30,33,36)
        self.description_value_box._impl.native.Controls.Remove(self.description_value)
        self.description_box.remove(self.description_label, self.description_value_box)
        self.item_options.remove(self.description_box, self.item_box)
        self.remove(self.item_options)
        self.view_button.on_press = self.show_item
        self.view_button.enabled = True
        self.view_button._impl.native.MouseEnter += self.view_button_mouse_enter
        self.view_button._impl.native.MouseLeave += self.view_button_mouse_leave


    def result_dialog(self, widget):
        self.hide_item()
        self.main.info_dialog(
            title="Order Placed",
            message="Your order was placed successfully."
        )


    async def confirm_order(self, button):
        quantity = int(self.quantity_input.value)
        if self.item_quantity <= 0:
            self.main.error_dialog(
                title="Out of Stock",
                message="This item is currently out of stock and cannot be ordered."
            )
            return
        elif quantity > self.item_quantity:
            self.main.error_dialog(
                title="Quantity Exceeds Stock",
                message=f"You requested {quantity}, but only {self.item_quantity} items are available."
            )
            return
        elif float(self.main.balance) <= self.total_price:
            self.main.error_dialog(
                title="Insufficient Balance",
                message="You do not have enough balance to complete this purchase."
            )
            return
        confirm_window = PlaceOrder(
            self.main, self, self.utils, self.tr, self.font, self.item, quantity, self.total_price, self.market, self.contact_id
        )
        confirm_window._impl.native.ShowDialog(self.main._impl.native)


    async def calculate_total_price(self, input):
        quantity = int(self.quantity_input.value)
        self.total_price = self.calculated_price * quantity
        self.total_value.text = self.units.format_balance(self.total_price)


    def show_item_image(self, sender, event):
        if self.image_stream:
            image_window = DisplayImage(self.main, self.utils, self.font, self.image_stream)
            image_window._impl.native.ShowDialog(self.main._impl.native)


    def view_button_mouse_enter(self, sender, event):
        self.view_button.style.color = BLACK
        self.view_button.style.background_color = YELLOW

    def view_button_mouse_leave(self, sender, event):
        self.view_button.style.color = GRAY
        self.view_button.style.background_color = rgb(30,33,36)



class MarketView(Window):
    def __init__(self, chat, main:Window, utils, units, commands, tr, font, username, contact_id):
        super().__init__()

        self.chat = chat
        self.main = main
        self.utils = utils
        self.units = units
        self.commands = commands
        self.tr = tr
        self.font = font
        self.contact_id = contact_id

        self.title = f"{username}'s Market"
        self.size = (900,607)
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self._impl.native.Resize += self._handle_on_resize
        self.on_close = self.close_market_window

        self.storage = StorageMessages(self.app)
        self.market_status = None
        self.marketplace_toggle = True
        self.items_data = []

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.status_label = Label(
            text="Status : Loading...",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                padding = (10,10,0,10),
                flex = 1
            )
        )
        self.status_label._impl.native.Font = self.font.get(10, True)

        self.orders_button = Button(
            text="My Orders",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 100,
                padding =(5,10,0,0)
            )
        )
        self.orders_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.orders_button._impl.native.Font = self.font.get(9, True)

        self.balance_label = Label(
            text="Balance : 0.00000000",
            style=Pack(
                color = rgb(114,137,218),
                background_color = rgb(40,43,48),
                padding = (10,10,0,20)
            )
        )
        self.balance_label._impl.native.Font = self.font.get(10, True)

        self.menu_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 40
            )
        )

        self.items_scroll = ScrollContainer(
            style=Pack(
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.items_list = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.menu_box,
            self.items_scroll
        )
        self.menu_box.add(
            self.status_label,
            self.orders_button,
            self.balance_label
        )
        self.items_scroll.content = self.items_list

        self.app.add_background_task(self.update_balance)
        self.app.add_background_task(self.get_status)


    async def update_balance(self, widget):
        while True:
            if not self.marketplace_toggle:
                return
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            address = self.storage.get_identity("address")
            if address:
                balance, _= await self.commands.z_getBalance(address[0])
                self.balance = self.units.format_balance(balance)
                self.balance_label.text = f"Balance : {self.balance}"
            await asyncio.sleep(5)


    async def get_status(self, widget):
        market = self.storage.get_hostname(self.contact_id)
        url = f'http://{market[0]}/status'
        result = await self.utils.make_request(self.contact_id, url)
        if not result or "error" in result:
            self.status_label.text = "Status : Offline"
            self.status_label.style.color = RED
            return
        self.status_label.text = "Status : Online"
        self.status_label.style.color = GREENYELLOW
        self.app.add_background_task(self.update_status)
        self.app.add_background_task(self.get_market_items)


    async def update_status(self, widget):
        market = self.storage.get_hostname(self.contact_id)
        url = f'http://{market[0]}/status'
        while True:
            if not self.marketplace_toggle:
                return
            result = await self.utils.make_request(self.contact_id, url)
            if not result or "error" in result:
                self.market_status = None
                self.status_label.text = "Status : Offline"
                self.status_label.style.color = RED
            else:
                self.market_status = True
                self.status_label.text = "Status : Online"
                self.status_label.style.color = GREENYELLOW

            await asyncio.sleep(60)


    async def get_market_items(self, widget):
        market = self.storage.get_hostname(self.contact_id)
        url = f'http://{market[0]}/items'
        result = await self.utils.make_request(self.contact_id, url)
        if "error" in result:
            return
        for item in result:
            item_id = item.get('id')
            item_view = ItemView(
                self.app, self, self.utils, self.units, self.tr, self.font, item, market, self.contact_id
            )
            self.items_list.add(item_view)
            self.items_data.append(item_id)
        self.app.add_background_task(self.update_items_list)


    async def update_items_list(self, widget):
        market = self.storage.get_hostname(self.contact_id)
        url = f'http://{market[0]}/items'
        while True:
            if not self.marketplace_toggle:
                return
            result = await self.utils.make_request(self.contact_id, url)
            if "error" in result:
                pass
            else:
                current_ids = set()
                for item in result:
                    item_id = item.get('id')
                    current_ids.add(item_id)
                    if item_id not in self.items_data:
                        item_view = ItemView(
                            self.app, self, self.utils, self.units, self.tr, self.font, item, market, self.contact_id
                        )
                        self.items_list.insert(0, item_view)
                        self.items_data.append(item_id)

                for item_view in self.items_list.children:
                    if item_view.item_id not in current_ids:
                        self.items_list.remove(item_view)
                        self.items_data.remove(item_view.item_id)

            await asyncio.sleep(60)


    def _handle_on_resize(self, sender, event:Sys.EventArgs):
        min_width = 916
        min_height = 646
        self._impl.native.MinimumSize = Drawing.Size(min_width, min_height)


    def close_market_window(self, widget):
        self.marketplace_toggle = None
        self.chat.marketplace_toggle = None
        self.close()



class AddItem(Window):
    def __init__(self, main:Window, settings, utils, tr, font):
        super().__init__()

        self.main = main
        self.settings = settings
        self.utils = utils
        self.tr = tr
        self.font = font

        self.storage = StorageMarket(self.app)

        self.title = "Add Item"
        self.size = (500, 450)
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self._impl.native.ControlBox = False

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.title_label = Label(
            text="Title :",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                padding = (11,0,0,0)
            )
        )
        self.title_label._impl.native.Font = self.font.get(10, True)

        self.image_label = Label(
            text="Image :",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                padding = (55,0,0,0)
            )
        )
        self.image_label._impl.native.Font = self.font.get(10, True)

        self.description_label = Label(
            text="Description :",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                padding = (85,0,0,0)
            )
        )
        self.description_label._impl.native.Font = self.font.get(10, True)

        self.price_label = Label(
            text="Price :",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                padding = (52,0,0,0)
            )
        )
        self.price_label._impl.native.Font = self.font.get(10, True)

        self.quantity_label = Label(
            text="Quantity :",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                padding = (20,0,0,0)
            )
        )
        self.quantity_label._impl.native.Font = self.font.get(10, True)

        self.labes_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )

        self.title_input = TextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                width = 250,
                padding = (10,15,0,15)
            )
        )
        self.title_input._impl.native.Font = self.font.get(11, True)

        self.image_input = ImageView(
            style=Pack(
                background_color = rgb(30,33,36),
                width = 100,
                height = 100
            )
        )
        self.image_input._impl.native.AllowDrop = True
        self.image_input._impl.native.Click += self.select_image_file
        self.image_input._impl.native.DragEnter += Forms.DragEventHandler(self.on_drag_enter)
        self.image_input._impl.native.DragDrop += Forms.DragEventHandler(self.on_drag_drop)
        self.image_input._impl.native.Cursor = Cursors.HAND

        self.clear_button = Button(
            text="Clear",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 80,
                padding = (0,0,0,15)
            ),
            on_press=self.clear_image_input
        )
        self.clear_button._impl.native.Font = self.font.get(9, True)
        self.clear_button._impl.native.FlatStyle = FlatStyle.FLAT

        self.image_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                padding = (10,0,0,15)
            )
        )

        self.description_input = MultilineTextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                padding = (10,15,0,15)
            )
        )
        self.description_input._impl.native.Font = self.font.get(11, True)
        
        self.price_input = TextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                width = 100,
                padding = (10,15,0,15)
            ),
            validators=[self.is_digit]
        )
        self.price_input._impl.native.Font = self.font.get(11, True)

        self.currencies_selection = Selection(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                padding = (10,0,0,10)
            ),
            items=[
                {"currency": ""}
            ],
            accessor="currency"
        )
        self.currencies_selection._impl.native.Font = self.font.get(10, True)
        self.currencies_selection._impl.native.FlatStyle = FlatStyle.FLAT
        self.currencies_selection._impl.native.DropDownHeight = 150

        self.price_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48)
            )
        )

        self.quantity_input = NumberInput(
            value=1,
            step=1,
            min=1,
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                width = 80,
                padding = (10,15,0,15)
            )
        )
        self.quantity_input._impl.native.Font = self.font.get(11, True)

        self.inputs_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 2
            )
        )

        self.options_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = 5,
                flex = 1
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
            on_press=self.close_additem
        )
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.add_button = Button(
            text="Add",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding = (0,0,10,20),
                width = 100
            ),
            on_press=self.add_new_item
        )
        self.add_button._impl.native.Font = self.font.get(9, True)
        self.add_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.add_button._impl.native.MouseEnter += self.add_button_mouse_enter
        self.add_button._impl.native.MouseLeave += self.add_button_mouse_leave

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER,
                background_color = rgb(30,33,36)
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.options_box,
            self.buttons_box
        )
        self.options_box.add(
            self.labes_box,
            self.inputs_box
        )
        self.labes_box.add(
            self.title_label,
            self.image_label,
            self.description_label,
            self.price_label,
            self.quantity_label
        )
        self.inputs_box.add(
            self.title_input,
            self.image_box,
            self.description_input,
            self.price_box,
            self.quantity_input
        )
        self.image_box.add(
            self.image_input
        )
        self.price_box.add(
            self.price_input,
            self.currencies_selection
        )
        self.buttons_box.add(
            self.cancel_button,
            self.add_button
        )

        self.load_currencies()


    def load_currencies(self):
        currencies_data = [{"currency": "BTCZ"}]
        current_currency = self.settings.currency()
        if current_currency:
            currencies_data.append({"currency": current_currency.upper()})
        self.currencies_selection.items.clear()
        self.currencies_selection.items = currencies_data
        self.currencies_selection.value = self.currencies_selection.items.find("BTCZ")


    async def add_new_item(self, button):
        def on_result(widget, result):
            if result is None:
                self.close()
                self.app.current_window = self.main

        if not self.title_input.value:
            self.error_dialog(
                title="Missing Title",
                message="Item title is required"
            )
            self.title_input.focus()
            return
        if not self.price_input.value:
            self.error_dialog(
                title="Missing Price",
                message="Item price is required"
            )
            self.price_input.focus()
            return
        if not self.quantity_input.value:
            self.error_dialog(
                title="Missing Quantity",
                message="Item quantity is required"
            )
            self.quantity_input.focus()
            return
        quantity = self.quantity_input.value
        if int(quantity) <= 0:
            self.quantity_input.value = "1"
            return
        item_id = str(uuid.uuid4())
        title = self.title_input.value.strip()
        new_filename = None
        if self.image_input.image:
            original_path = self.image_input.image.path
            ext = Os.Path.GetExtension(str(original_path))
            new_filename = f"{item_id}{ext}"
            destination_dir = Os.Path.Combine(str(self.app.paths.data), "items")
            if not Os.Directory.Exists(destination_dir):
                Os.Directory.CreateDirectory(destination_dir)
            new_path = Os.Path.Combine(destination_dir, new_filename)
            Os.File.Copy(str(original_path), new_path, overwrite=True)

        description = self.description_input.value.strip()
        price = self.price_input.value
        currency = self.currencies_selection.value.currency
        quantity = int(self.quantity_input.value)
        timestamp = int(datetime.now().timestamp())
        self.storage.insert_item(item_id, title, new_filename, description, price, currency, quantity, timestamp)
        self.info_dialog(
            title="Item Added",
            message=f"The item {title} has been successfully added",
            on_result=on_result
        )


    def select_image_file(self, sender, event):
        def on_result(widget, result):
            if result:
                extentions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
                ext = Os.Path.GetExtension(str(result))
                if ext not in extentions:
                    self.error_dialog(
                        title="Invalid Image Format",
                        message="Only image files (.jpg, .png, .gif, etc.) are allowed."
                    )
                    return
                self.image_input.image = result
                self.image_box.add(
                    self.clear_button
                )
        self.open_file_dialog(
            title=self.tr.title("selectfile_dialog"),
            file_types=["jpg", "jpeg", "png", "gif", "bmp", "webp"],
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
            self.image_input.image = files[0]
            self.image_box.add(
                self.clear_button
            )


    def clear_image_input(self, button):
        self.image_input.image = None
        self.image_box.remove(
            self.clear_button
        )


    def is_digit(self, value):
        if not self.price_input.value.replace('.', '', 1).isdigit():
            self.price_input.value = ""


    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = RED
        self.cancel_button.style.background_color = rgb(30,33,36)


    def add_button_mouse_enter(self, sender, event):
        self.add_button.style.color = BLACK
        self.add_button.style.background_color = GREENYELLOW

    def add_button_mouse_leave(self, sender, event):
        self.add_button.style.color = GRAY
        self.add_button.style.background_color = rgb(30,33,36)


    def close_additem(self, button):
        self.close()
        self.app.current_window = self.main



class Item(Box):
    def __init__(self, app:App ,main:Window, storage, font, item):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 55,
                alignment = CENTER
            )
        )
        
        self.main = main
        self.font = font
        self.storage = storage
        self.tootip = ToolTip()
        self.clipboard = ClipBoard()

        item_id, title, image_name, description, price, currency, quantity, timestamp = item
        self.item_id = item_id
        if not image_name:
            image_path = "images/image_not_found.png"
        else:
            items_path = Os.Path.Combine(str(app.paths.data), "items")
            image_path = Os.Path.Combine(items_path, image_name)

        self.item_image = ImageView(
            image=image_path,
            style=Pack(
                background_color = rgb(40,43,48),
                width = 45,
                height = 45,
                padding = (5,15,0,5)
            )
        )

        self.item_title = Label(
            text=title[:75],
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 3
            )
        )
        self.item_title._impl.native.Font = self.font.get(10, True)

        self.item_id_label = Label(
            text=f"{item_id[:15]}...",
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.item_id_label._impl.native.Font = self.font.get(9, True)
        self.tootip.insert(self.item_id_label._impl.native, item_id)

        self.item_price = Label(
            text=price,
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.item_price._impl.native.Font = self.font.get(10, True)

        self.item_currency = Label(
            text=currency,
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.item_currency._impl.native.Font = self.font.get(10, True)

        self.item_quantity = Label(
            text=f"QN: {quantity}",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.item_quantity._impl.native.Font = self.font.get(10, True)

        self.add(
            self.item_image,
            self.item_title,
            self.item_id_label,
            self.item_price,
            self.item_currency,
            self.item_quantity
        )

        self.insert_item_menustrip()


    def insert_item_menustrip(self):
        context_menu = Forms.ContextMenuStrip()
        self.copy_id_cmd = Command(
            title="Copy id",
            icon="images/copy_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.copy_id_cmd_mouse_enter,
            mouse_leave=self.copy_id_cmd_mouse_leave,
            action=self.copy_item_id
        )
        self.remove_item_cmd = Command(
            title="Remove item",
            icon="images/remove_item_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.remove_item_cmd_mouse_enter,
            mouse_leave=self.remove_item_cmd_mouse_leave,
            action=self.remove_item_from_list
        )
        commands = [
            self.copy_id_cmd,
            self.remove_item_cmd
        ]
        for command in commands:
            context_menu.Items.Add(command)
        self._impl.native.ContextMenuStrip = context_menu
        self.item_image._impl.native.ContextMenuStrip = context_menu
        self.item_title._impl.native.ContextMenuStrip = context_menu
        self.item_id_label._impl.native.ContextMenuStrip = context_menu


    def copy_item_id(self):
        self.clipboard.copy(self.item_id)
        self.main.info_dialog(
            title="Copied",
            message="The item id has copied to clipboard.",
        )

    def remove_item_from_list(self):
        def on_result(widget, result):
            if result is True:
                self.storage.delete_item(self.item_id)
                self.main.items_list.remove(self)
                self.main.items_data.remove(self.item_id)
        self.main.question_dialog(
            title="Removing Item",
            message="Are you sure you want to remove this item ?",
            on_result=on_result
        )


    def copy_id_cmd_mouse_enter(self):
        self.copy_id_cmd.icon = "images/copy_a.ico"
        self.copy_id_cmd.color = Color.BLACK

    def copy_id_cmd_mouse_leave(self):
        self.copy_id_cmd.icon = "images/copy_i.ico"
        self.copy_id_cmd.color = Color.WHITE

    def remove_item_cmd_mouse_enter(self):
        self.remove_item_cmd.icon = "images/remove_item_a.ico"
        self.remove_item_cmd.color = Color.BLACK

    def remove_item_cmd_mouse_leave(self):
        self.remove_item_cmd.icon = "images/remove_item_i.ico"
        self.remove_item_cmd.color = Color.WHITE




class Order(Box):
    def __init__(self, main:Window, storage, font, order):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 55,
                alignment = CENTER
            )
        )

        self.main = main
        self.font = font
        self.storage = storage
        self.tootip = ToolTip()
        self.clipboard = ClipBoard()

        order_id, item_id, contact_id, total_price, quantity, comment, address, status, created, expired = order

        self.order_icon = ImageView(
            image="images/order.png",
            style=Pack(
                background_color = rgb(40,43,48),
                width = 45,
                height = 45,
                padding = (5,15,0,5)
            )
        )

        self.order_id_label = Label(
            text=f"{order_id[:15]}...",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 2
            )
        )
        self.order_id_label._impl.native.Font = self.font.get(10, True)
        self.tootip.insert(self.order_id_label._impl.native, order_id)

        self.item_id_label = Label(
            text=f"{item_id[:15]}...",
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.item_id_label._impl.native.Font = self.font.get(9, True)
        self.tootip.insert(self.item_id_label._impl.native, item_id)

        self.total_price_label = Label(
            text=f"{total_price} BTCZ",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.total_price_label._impl.native.Font = self.font.get(10, True)

        self.status_label = Label(
            text=status,
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.status_label._impl.native.Font = self.font.get(10, True)

        self.add(
            self.order_icon,
            self.order_id_label,
            self.item_id_label,
            self.total_price_label,
            self.status_label
        )



class MarketPlace(Window):
    def __init__(self, main:Window, notify, settings, utils, tr, font, server):
        super().__init__()

        self.main = main
        self.notify = notify
        self.settings = settings
        self.utils = utils
        self.tr = tr
        self.font = font
        self.server = server

        self.market_storage = StorageMarket(self.app)
        self.message_storage = StorageMessages(self.app)

        self.title = "Market Place"
        self.size = (900,607)
        self._impl.native.Opacity = self.main._impl.native.Opacity
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self._impl.native.Resize += self._handle_on_resize
        self.on_close = self.close_market_window

        self.items_data = []
        self.orders_data = []
        self.search_toggle = None
        self.items_toggle = True
        self.orders_toggle = None

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.add_button = Button(
            text="Add Item",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 100,
                padding =(5,0,0,10)
            ),
            on_press=self.show_additem
        )
        self.add_button._impl.native.Font = self.font.get(9, True)
        self.add_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.add_button._impl.native.MouseEnter += self.add_button_mouse_enter
        self.add_button._impl.native.MouseLeave += self.add_button_mouse_leave

        self.search_label = Label(
            text="Search :",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                padding = (7,10,0,10)
            )
        )
        self.search_label._impl.native.Font = self.font.get(10, True)

        self.search_input = TextInput(
            placeholder=" Item ID or Title",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                padding=(5,10,0,0),
                flex = 1
            ),
            on_confirm=self.search_item,
            on_change=self.clean_search
        )
        self.search_input._impl.native.Font = self.font.get(11, True)

        self.orders_button = Button(
            text="  Orders",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 110,
                padding =(5,10,0,0)
            ),
            on_press=self.show_orders_list
        )
        self.orders_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.orders_button._impl.native.Font = self.font.get(9, True)
        self.orders_button._impl.native.MouseEnter += self.orders_button_mouse_enter
        self.orders_button._impl.native.MouseLeave += self.orders_button_mouse_leave

        self.start_server = Button(
            text="",
            enabled=False,
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 100,
                padding =(5,10,0,0)
            )
        )
        self.start_server._impl.native.FlatStyle = FlatStyle.FLAT
        self.start_server._impl.native.Font = self.font.get(9, True)

        self.menu_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 40
            )
        )

        self.items_scroll = ScrollContainer(
            style=Pack(
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.items_list = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.menu_box,
            self.items_scroll
        )
        self.menu_box.add(
            self.add_button,
            self.search_label,
            self.search_input,
            self.orders_button,
            self.start_server
        )
        self.items_scroll.content = self.items_list

        self.load_market_config()


    def load_market_config(self):
        if self.server.server_status:
            self.start_server.text = "Stop"
            self.start_server._impl.native.MouseEnter += self.stop_server_mouse_enter
            self.start_server._impl.native.MouseLeave += self.stop_server_mouse_leave
            self.start_server.on_press = self.stop_market_server
        else:
            self.start_server.text = "Host"
            self.start_server._impl.native.MouseEnter += self.start_server_mouse_enter
            self.start_server._impl.native.MouseLeave += self.start_server_mouse_leave
            self.start_server.on_press = self.start_market_server

        torrc = self.utils.read_torrc()
        if torrc:
            hs_dirs = torrc.get("HiddenServiceDir", [])
            hs_ports = torrc.get("HiddenServicePort", [])
            if not isinstance(hs_dirs, list):
                hs_dirs = [hs_dirs]
            if not isinstance(hs_ports, list):
                hs_ports = [hs_ports]
            for dir_path, port_line in zip(hs_dirs, hs_ports):
                if dir_path.endswith("market_service"):
                    self.market_port = port_line.split()[1].split(":")[1] if port_line else ""
                    self.start_server.enabled = True
        self.load_items_list()
        self.app.add_background_task(self.updating_items_list)



    def load_items_list(self):
        market_items = self.market_storage.get_market_items()
        if market_items:
            sorted_items = sorted(market_items, key=lambda x: x[7], reverse=True)
            for item in sorted_items:
                item_info = Item(self.app, self, self.market_storage, self.font, item)
                self.items_list.add(item_info)
                self.items_data.append(item[0])


    def load_orders_list(self):
        market_orders = self.market_storage.get_market_orders()
        if market_orders:
            sorted_orders = sorted(market_orders, key=lambda x: x[8], reverse=True)
            for order in sorted_orders:
                order_info = Order(self, self.market_storage, self.font, order)
                self.items_list.add(order_info)
                self.orders_data.append(order[0])


    async def updating_items_list(self, widget):
        while True:
            if not self.main.marketplace_toggle:
                return
            if not self.items_toggle:
                await asyncio.sleep(1)
                continue
            market_items = self.market_storage.get_market_items()
            if market_items:
                sorted_items = sorted(market_items, key=lambda x: x[7], reverse=True)
                for item in sorted_items:
                    if item[0] not in self.items_data:
                        item_info = Item(self.app, self, self.market_storage, self.font, item)
                        self.items_data.append(item[0])
                        if not self.search_toggle:
                            self.items_list.insert(0, item_info)
            await asyncio.sleep(3)


    async def updating_orders_list(self, widget):
        while True:
            if not self.main.marketplace_toggle:
                return
            if not self.orders_toggle:
                return
            market_orders = self.market_storage.get_market_orders()
            if market_orders:
                sorted_orders = sorted(market_orders, key=lambda x: x[8], reverse=True)
                for order in sorted_orders:
                    if order[0] not in self.orders_data:
                        order_info = Order(self, self.market_storage, self.font, order)
                        self.orders_data.append(order[0])
                        self.items_list.insert(0, order_info)
            await asyncio.sleep(3)



    def start_market_server(self, button):         
        self.start_server.enabled = False
        host = "127.0.0.1"
        port = self.market_port      
        self.server.host = host
        self.server.port = port
        self.server.market_storage = self.market_storage
        self.server.messages_storage = self.message_storage

        result = self.server.start()
        if result is True:
            self.notify.show()
            self.notify.send_note(
                title="Marketplace Server",
                text=f"Server started successfully, and listening to {host}:{port}"
            )
            self.update_host_button("start")
        else:
            self.error_dialog(
                title="Error",
                message="Failed to start server. Please check the configuration and try again."
            )
        self.start_server.enabled = True


    async def show_orders_list(self, button):
        if not self.orders_toggle:
            self.items_toggle = None
            self.orders_button.enabled = False
            self.menu_box.remove(self.add_button)
            self.orders_button._impl.native.Text = "  Items"
            self.search_input.placeholder = " Order ID"
            self.search_input.on_confirm = self.search_order
            self.orders_button.on_press = self.show_items_list
            self.items_list.clear()
            self.items_data.clear()
            self.load_orders_list()
            self.orders_toggle = True
            self.app.add_background_task(self.updating_orders_list)
            self.orders_button.enabled = True


    async def show_items_list(self, button):
        if not self.items_toggle:
            self.orders_toggle = None
            self.orders_button.enabled = False
            self.orders_button._impl.native.Text = "  Orders"
            self.search_input.placeholder=" Item ID or Title"
            self.search_input.on_confirm = self.search_item
            self.orders_button.on_press = self.show_orders_list
            self.items_list.clear()
            self.orders_data.clear()
            self.load_items_list()
            self.menu_box.insert(0, self.add_button)
            self.items_toggle = True
            self.orders_button.enabled = True


    def search_item(self, input):
        if not input.value:
            return
        item = self.market_storage.get_item(input.value.strip())
        if item:
            self.items_list.clear()
            info_item = Item(self, self.market_storage, self.font, item)
            self.items_list.add(info_item)
            self.search_toggle = True
        else:
            market_items = self.market_storage.search_title(input.value.strip())
            if market_items:
                self.items_list.clear()
                sorted_items = sorted(market_items, key=lambda x: x[7], reverse=True)
                for item in sorted_items:
                    info_item = Item(self.app, self, self.market_storage, self.font, item)
                    self.items_list.add(info_item)
                self.search_toggle = True
            else:
                self.error_dialog(
                    title="Not Found",
                    message="The item is not found."
                )


    def search_order(self, input):
        if not input.value:
            return

        
    def clean_search(self, input):
        if not input.value:
            if self.search_toggle:
                self.items_list.clear()
                if self.items_toggle:
                    self.load_items_list()
                elif self.orders_toggle:
                    self.load_orders_list()
                self.search_toggle = None


    def show_additem(self, button):
        self.additem_window = AddItem(self, self.settings, self.utils, self.tr, self.font)
        self.additem_window._impl.native.ShowDialog(self._impl.native)


    def stop_market_server(self, button):
        self.server.stop()
        self.notify.hide()
        self.update_host_button("stop")
        self.server.host = None
        self.server.port = None


    def update_host_button(self, option):
        if option == "start":
            self.start_server.text = "Stop"
            self.start_server._impl.native.MouseEnter -= self.start_server_mouse_enter
            self.start_server._impl.native.MouseLeave -= self.start_server_mouse_leave
            self.start_server._impl.native.MouseEnter += self.stop_server_mouse_enter
            self.start_server._impl.native.MouseLeave += self.stop_server_mouse_leave
            self.start_server.on_press = self.stop_market_server

        elif option == "stop":
            self.start_server.text = "Host"
            self.start_server._impl.native.MouseEnter -= self.stop_server_mouse_enter
            self.start_server._impl.native.MouseLeave -= self.stop_server_mouse_leave
            self.start_server._impl.native.MouseEnter += self.start_server_mouse_enter
            self.start_server._impl.native.MouseLeave += self.start_server_mouse_leave
            self.start_server.on_press = self.start_market_server


    def _handle_on_resize(self, sender, event:Sys.EventArgs):
        min_width = 916
        min_height = 646
        self._impl.native.MinimumSize = Drawing.Size(min_width, min_height)

    def add_button_mouse_enter(self, sender, event):
        self.add_button.style.color = BLACK
        self.add_button.style.background_color = GREENYELLOW

    def add_button_mouse_leave(self, sender, event):
        self.add_button.style.color = GRAY
        self.add_button.style.background_color = rgb(30,33,36)

    def orders_button_mouse_enter(self, sender, event):
        self.orders_button.style.color = BLACK
        self.orders_button.style.background_color = YELLOW

    def orders_button_mouse_leave(self, sender, event):
        self.orders_button.style.color = GRAY
        self.orders_button.style.background_color = rgb(30,33,36)

    def start_server_mouse_enter(self, sender, event):
        self.start_server.style.color = BLACK
        self.start_server.style.background_color = GREENYELLOW

    def start_server_mouse_leave(self, sender, event):
        self.start_server.style.color = GRAY
        self.start_server.style.background_color = rgb(30,33,36)

    def stop_server_mouse_enter(self, sender, event):
        self.start_server.style.color = BLACK
        self.start_server.style.background_color = RED

    def stop_server_mouse_leave(self, sender, event):
        self.start_server.style.color = GRAY
        self.start_server.style.background_color = rgb(30,33,36)


    def close_market_window(self, widget):
        self.main.marketplace_toggle = None
        self.close()