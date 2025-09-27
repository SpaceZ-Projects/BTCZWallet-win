
import asyncio
import uuid
from datetime import datetime, timezone
import json

from toga import (
    Window, Box, Button, Label, TextInput, ImageView,
    MultilineTextInput, Selection, ScrollContainer, App,
    NumberInput
)
from ..framework import (
    Sys, Drawing, FlatStyle, Forms, Cursors, Os, RichLabel,
    ToolTip, Command, Color, ClipBoard, DockStyle, BorderStyle
)
from toga.constants import COLUMN, CENTER, ROW, LEFT, RIGHT
from toga.style import Pack
from toga.colors import (
    rgb, GRAY, WHITE, RED, BLACK, GREENYELLOW,
    YELLOW, ORANGE
)

from .storage import StorageMarket, StorageMessages



class DisplayImage(Window):
    def __init__(self, main, font, image):
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
        position_center = self.utils.windows_screen_center(self.main, self)
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
        position_center = self.utils.windows_screen_center(self.main, self)
        self.position = position_center
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

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
        self.app.loop.create_task(self.make_request())

    async def make_request(self):
        url = f"http://{self.market[0]}/place_order"
        params = {
            "id": str(self.item_id),
            "contact_id": str(self.contact_id),
            "total_price": str(self.total_price),
            "quantity": str(self.order_quantity),
            "comment": str(self.comment_input.value.strip())
        }
        result = await self.utils.make_request(self.contact_id, self.market[1], url, params)
        if not result or "error" in result:
            self.cancel_button.enabled = True
            self.place_order_button.enabled = True
            return
        self.close()
        self.app.current_window = self.main
        if "failed" in result:
            self.app.loop.create_task(self.item_view.failed_dialog())
            return
        self.app.loop.create_task(self.item_view.result_dialog())


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
            text=item_description,
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
        self.buy_button._impl.native.MouseEnter += self.buy_button_mouse_enter
        self.buy_button._impl.native.MouseLeave += self.buy_button_mouse_leave

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

        self.app.loop.create_task(self.display_image())


    async def display_image(self):
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
            self.app.loop.create_task(self.display_image())


    async def show_item(self, button):
        self.view_button.enabled = False
        params = {"get": "quantity"}
        url = f"http://{self.market[0]}/item/{self.item_id}"
        result = await self.utils.make_request(self.contact_id, self.market[1], url, params)
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
            result = await self.utils.make_request(self.contact_id, self.market[1], url)
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


    def result_dialog(self):
        self.hide_item()
        self.main.info_dialog(
            title="Order Placed",
            message="Your order was placed successfully."
        )

    def failed_dialog(self):
        self.hide_item()
        self.main.error_dialog(
            title="Order Failed",
            message="You already have a pending order for this item"
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
            image_window = DisplayImage(self.main, self.font, self.image_stream)
            image_window._impl.native.ShowDialog(self.main._impl.native)


    def view_button_mouse_enter(self, sender, event):
        self.view_button.style.color = BLACK
        self.view_button.style.background_color = YELLOW

    def view_button_mouse_leave(self, sender, event):
        self.view_button.style.color = GRAY
        self.view_button.style.background_color = rgb(30,33,36)

    def buy_button_mouse_enter(self, sender, event):
        self.buy_button.style.color = BLACK
        self.buy_button.style.background_color = GREENYELLOW

    def buy_button_mouse_leave(self, sender, event):
        self.buy_button.style.color = GRAY
        self.buy_button.style.background_color = rgb(30,33,36)



class OrderView(Box):
    def __init__(self, main:Window, storage, utils, units, commands, font, order, contact_id):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 55,
                alignment = CENTER
            )
        )
        
        self.main = main
        self.utils = utils
        self.units = units
        self.commands = commands
        self.font = font
        self.storage = storage

        self.order = order
        self.contact_id = contact_id

        self.pay_toggle = None

        self.order_id = order.get('order_id')
        self.item_id = order.get('item_id')
        self.item_title = order.get('item_title')
        self.total_price = order.get('total_price')
        self.order_quantity = order.get('quantity')
        self.order_comment = order.get('comment')
        self.order_status = order.get('status')
        self.order_remaining = order.get('remaining')

        if self.order_status == "completed":
            color = GREENYELLOW
        elif self.order_status == "pending":
            color = WHITE
        elif self.order_status == "expired":
            color = RED
        elif self.order_status == "paid":
            color = YELLOW
        elif self.order_status == "cancelled":
            color = ORANGE

        if self.order_remaining <= 0 or self.order_status != "pending":
            remaining_time = ""
            remaining_background_color = rgb(40,43,48)
            remaining_enabled = False
        else:
            remaining_time = self.units.create_timer(self.order_remaining, True)
            remaining_background_color = rgb(30,33,36)
            remaining_enabled = True

        self.order_icon = ImageView(
            image="images/product.png",
            style=Pack(
                background_color = rgb(40,43,48),
                width = 45,
                height = 45,
                padding = (5,15,0,5)
            )
        )

        self.order_id_label = Label(
            text=f"{self.order_id[:15]}...",
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 2
            )
        )
        self.order_id_label._impl.native.Font = self.font.get(10, True)

        self.status_label = Label(
            text=self.order_status,
            style=Pack(
                color = color,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.status_label._impl.native.Font = self.font.get(10, True)

        self.remaining_label = TextInput(
            value="",
            readonly=True,
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                background_color = remaining_background_color,
                width = 80,
                padding = (0,20,0,0)
            )
        )
        self.remaining_label._impl.native.Font = self.font.get(9, True)
        self.remaining_label._impl.native.Text = remaining_time
        self.remaining_label._impl.native.BorderStyle = BorderStyle.NONE
        self.remaining_label._impl.native.Enabled = remaining_enabled

        self.order_info = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                height = 50,
                alignment = CENTER
            )
        )

        self.item_title_label = Label(
            text=f"Item Title : {self.item_title}",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                padding = (5,0,0,10)
            )
        )
        self.item_title_label._impl.native.Font = self.font.get(10, True)

        self.comment_label = Label(
            text="Comment :",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                padding = (5,0,0,10)
            )
        )
        self.comment_label._impl.native.Font = self.font.get(10, True)

        self.comment_value = RichLabel(
            text=self.order_comment,
            font= self.font.get(9, True),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            wrap=True,
            readonly=True,
            dockstyle=DockStyle.FILL,
            borderstyle=BorderStyle.NONE
        )

        self.comment_value_box = Box(
            style=Pack(
                background_color=rgb(30,33,36),
                padding = (5,0,0,20),
                flex = 1
            )
        )

        self.quantity_value = Label(
            text=f"Quantity : {self.order_quantity}",
            style=Pack(
                color = WHITE,
                background_color=rgb(30,33,36),
                padding = (5,0,5,10)
            )
        )
        self.quantity_value._impl.native.Font = self.font.get(10, True)

        self.order_details = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                padding = (10,5,5,10),
                height = 200,
                alignment = CENTER
            )
        )

        self.pay_button = Button(
            text="Pay",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 80,
                padding = (0,10,0,0)
            ),
            on_press=self.pay_order
        )
        self.pay_button._impl.native.Font = self.font.get(9, True)
        self.pay_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.pay_button._impl.native.MouseEnter += self.pay_button_mouse_enter
        self.pay_button._impl.native.MouseLeave += self.pay_button_mouse_leave

        self.cancel_button = Button(
            text="Cancel",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 80,
                padding = (0,10,0,0)
            ),
            on_press=self.cancel_order
        )
        self.cancel_button._impl.native.Font = self.font.get(9, True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.more_button = Button(
            text="More",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                padding = (0,10,0,0)
            ),
            on_press=self.show_more
        )
        self.more_button._impl.native.Font = self.font.get(9, True)
        self.more_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.more_button._impl.native.MouseEnter += self.more_button_mouse_enter
        self.more_button._impl.native.MouseLeave += self.more_button_mouse_leave

        self.add(
            self.order_info
        )
        self.order_info.add(
            self.order_icon,
            self.order_id_label,
            self.status_label,
            self.remaining_label
        )
        if self.order_status == "pending":
            self.order_info.add(
                self.pay_button,
                self.cancel_button
            )
            self.pay_toggle = True
        self.order_info.add(
            self.more_button
        )


    async def show_more(self, button):
        self.more_button.enabled = False
        self.style.height = 280
        self.more_button.text = "Less"
        self.add(self.order_details)
        self.order_details.add(
            self.item_title_label,
            self.comment_label,
            self.comment_value_box,
            self.quantity_value
        )
        self.comment_value_box._impl.native.Controls.Add(self.comment_value)
        self.more_button.on_press = self.show_less
        self.more_button.enabled = True


    async def show_less(self, button):
        self.more_button.enabled = False
        self.style.height = 55
        self.more_button.text = "More"
        self.comment_value_box._impl.native.Controls.Remove(self.comment_value)
        self.order_details.remove(
            self.item_title_label,
            self.comment_label,
            self.comment_value_box,
            self.quantity_value
        )
        self.remove(self.order_details)
        self.more_button.on_press = self.show_more
        self.more_button.enabled = True


    async def pay_order(self, button):
        async def on_result(widget, result):
            if result is True:
                self.main.operation_toggle = True
                self.cancel_button.enabled = False
                self.pay_button.enabled = False
                address = self.storage.get_identity("address")
                market_address = self.storage.get_contact_address(self.contact_id)
                amount = float(self.total_price) + 0.0001
                txfee = 0.0001
                memo = {"type":"payment","order_id":self.order_id}
                memo_str = json.dumps(memo)
                await self.send_payment(address[0], market_address[0], amount, txfee, memo_str)
                     
        if not self.main.operation_toggle:
            if self.total_price >= float(self.main.balance):
                return
            self.main.question_dialog(
                title="Pay Order",
                message=f"Are you sure you want to pay this order ?\nTotal Price : {self.total_price} BTCZ",
                on_result=on_result
            )


    async def send_payment(self, address, market_address, amount, txfee, memo):
        operation, _= await self.commands.SendMemo(address, market_address, amount, txfee, memo)
        if operation:
            transaction_status, _= await self.commands.z_getOperationStatus(operation)
            transaction_status = json.loads(transaction_status)
            if isinstance(transaction_status, list) and transaction_status:
                status = transaction_status[0].get('status')
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
                                self.main.operation_toggle = None
                                self.cancel_button.enabled = True
                                self.pay_button.enabled = True
                                return
                            elif status == "executing":
                                pass
                            elif status == "success":
                                self.storage.tx(txid)
                                self.order_info.remove(self.pay_button, self.cancel_button)
                                self.status_label.text = "paid"
                                self.status_label.style.color = YELLOW
                                self.remaining_label.value = ""
                                self.remaining_label.style.background_color = rgb(40,43,48)
                                self.remaining_label._impl.native.Enbaled = False
                                self.main.operation_toggle = None
                                return
                        await asyncio.sleep(3)
                else:
                    self.main.operation_toggle = None
                    self.cancel_button.enabled = True
                    self.pay_button.enabled = True
        else:
            self.main.operation_toggle = None
            self.cancel_button.enabled = True
            self.pay_button.enabled = True
            


    async def cancel_order(self, button):
        async def on_result(widget, result):
            if result is True:
                self.main.operation_toggle = True
                self.cancel_button.enabled = False
                self.pay_button.enabled = False
                market, secret = self.storage.get_hostname(self.contact_id)
                params = {"order_id": self.order_id}
                url = f'http://{market}/cancel_order'
                response = await self.utils.make_request(self.contact_id, secret, url, params)
                self.main.operation_toggle = None
                if not response or "error" in response:
                    self.cancel_button.enabled = True
                    self.pay_button.enabled = True
                    return

                result_value = response.get("result")

                if result_value == "failed":
                    self.order_info.remove(self.pay_button, self.cancel_button)
                    self.status_label.text = "cancelled"
                    self.status_label.style.color = ORANGE
                    self.remaining_label.value = ""
                    self.remaining_label.style.background_color = rgb(40,43,48)
                    self.remaining_label._impl.native.Enbaled = False
                    self.main.info_dialog(
                        title="Already Cancelled",
                        message=f"Order #{self.order_id} was already cancelled."
                    )
                    return

                if result_value == "expired":
                    self.order_info.remove(self.pay_button, self.cancel_button)
                    self.status_label.text = "expired"
                    self.status_label.style.color = RED
                    self.remaining_label.value = ""
                    self.remaining_label.style.background_color = rgb(40,43,48)
                    self.remaining_label._impl.native.Enbaled = False
                    self.main.info_dialog(
                        title="Order Expired",
                        message=f"Order #{self.order_id} has expired and cannot be cancelled."
                    )
                    return
                if result_value == "success":
                    self.order_info.remove(self.pay_button, self.cancel_button)
                    self.status_label.text = "cancelled"
                    self.status_label.style.color = ORANGE
                    self.remaining_label.value = ""
                    self.remaining_label.style.background_color = rgb(40,43,48)
                    self.remaining_label._impl.native.Enbaled = False
                    self.main.info_dialog(
                        title="Order Cancelled",
                        message=f"Order #{self.order_id} has been successfully cancelled"
                    )

        if not self.main.operation_toggle:
            self.main.question_dialog(
                title="Cancel Order",
                message="Are you sure you want to cancel this order ?\nThis action cannot be undone",
                on_result=on_result
            )



    def pay_button_mouse_enter(self, sender, event):
        self.pay_button.style.color = BLACK
        self.pay_button.style.background_color = GREENYELLOW

    def pay_button_mouse_leave(self, sender, event):
        self.pay_button.style.color = GRAY
        self.pay_button.style.background_color = rgb(30,33,36)

    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = BLACK
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = GRAY
        self.cancel_button.style.background_color = rgb(30,33,36)


    def more_button_mouse_enter(self, sender, event):
        self.more_button.style.color = WHITE

    def more_button_mouse_leave(self, sender, event):
        self.more_button.style.color = GRAY



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
        self._impl.native.Icon = self.window_icon("images/Market.ico")
        self.size = (900,607)
        position_center = self.utils.windows_screen_center(self.main, self)
        self.position = position_center
        self._impl.native.Resize += self._handle_on_resize
        self.on_close = self.close_market_window

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.storage = StorageMessages(self.app)
        self.tooltip = ToolTip()
        self.market_status = None
        self.marketplace_toggle = True
        self.items_toggle = None
        self.orders_toggle = None
        self.items_data = {}
        self.orders_data = {}
        self.operation_toggle = None

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

        self.refresh_button = ImageView(
            image="images/refresh.png",
            style=Pack(
                width = 20,
                height = 20,
                background_color = rgb(40,43,48),
                padding = (12,0,0,10)
            )
        )
        self.tooltip.insert(self.refresh_button._impl.native, "Refresh")
        self.refresh_button._impl.native.Click += self.refresh_market

        self.orders_button = Button(
            text="My Orders",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 100,
                padding =(5,10,0,0)
            ),
            enabled=False,
            on_press=self.show_orders_list
        )
        self.orders_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.orders_button._impl.native.Font = self.font.get(9, True)
        self.orders_button._impl.native.MouseEnter += self.orders_button_mouse_enter
        self.orders_button._impl.native.MouseLeave += self.orders_button_mouse_leave

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
                height = 40,
                padding = (0,0,10,0)
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

        self.app.loop.create_task(self.update_balance())
        self.app.loop.create_task(self.get_status())


    async def update_balance(self):
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


    async def get_status(self):
        market, secret = self.storage.get_hostname(self.contact_id)
        url = f'http://{market}/status'
        result = await self.utils.make_request(self.contact_id, secret, url)
        if not result or "error" in result:
            self.menu_box.insert(0, self.refresh_button)
            self.status_label.text = "Status : Offline"
            self.status_label.style.color = RED
            return
        self.status_label.text = "Status : Online"
        self.status_label.style.color = GREENYELLOW

        self.app.loop.create_task(self.update_status())
        self.app.loop.create_task(self.get_market_items())
        self.app.loop.create_task(self.update_items_list())
        self.app.loop.create_task(self.update_orders_list())


    async def update_status(self, widget):
        market, secret = self.storage.get_hostname(self.contact_id)
        url = f'http://{market}/status'
        while True:
            if not self.marketplace_toggle:
                return
            result = await self.utils.make_request(self.contact_id, secret, url)
            if not result or "error" in result:
                self.market_status = None
                self.status_label.text = "Status : Offline"
                self.status_label.style.color = RED
            else:
                self.market_status = True
                self.status_label.text = "Status : Online"
                self.status_label.style.color = GREENYELLOW

            await asyncio.sleep(60)


    def refresh_market(self, sender, event):
        self.menu_box.remove(self.refresh_button)
        self.status_label.text = "Status : Loading..."
        self.status_label.style.color = WHITE
        self.app.loop.create_task(self.get_status())


    async def get_market_items(self):
        market = self.storage.get_hostname(self.contact_id)
        url = f'http://{market[0]}/items'
        result = await self.utils.make_request(self.contact_id, market[1], url)
        if not result:
            self.items_toggle = True
            self.orders_button.enabled = True
            return
        for item in result:
            item_id = item.get('id')
            item_view = ItemView(
                self.app, self, self.utils, self.units, self.tr, self.font, item, market, self.contact_id
            )
            self.items_data[item_id] = item_view
            self.items_list.add(item_view)
        self.items_toggle = True
        await asyncio.sleep(1)
        self.orders_button.enabled = True


    async def update_items_list(self):
        market, secret = self.storage.get_hostname(self.contact_id)
        url = f'http://{market}/items'
        while True:
            if not self.marketplace_toggle:
                return
            if not self.items_toggle:
                await asyncio.sleep(1)
                continue
            result = await self.utils.make_request(self.contact_id, secret, url)
            if not result:
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
                        self.items_data[item_id] = item_view
                        self.items_list.insert(0, item_view)

                for item_view in self.items_list.children:
                    if item_view.item_id not in current_ids:
                        self.items_list.remove(item_view)
                        del self.items_data[item_view.item_id]

            await asyncio.sleep(60)


    async def get_market_orders(self):
        market, secret = self.storage.get_hostname(self.contact_id)
        url = f'http://{market}/orders'
        param = {"contact_id": self.contact_id}
        result = await self.utils.make_request(self.contact_id, secret, url, param)
        if not result or "error" in result:
            self.orders_toggle = True
            self.orders_button.enabled = True
            return
        for order in result:
            order_id = order.get('order_id')
            order_view = OrderView(
                self, self.storage, self.utils, self.units, self.commands, self.font, order, self.contact_id
            )
            self.orders_data[order_id] = order_view
            self.items_list.add(order_view)
        self.orders_toggle = True
        await asyncio.sleep(1)
        self.orders_button.enabled = True



    async def update_orders_list(self):
        market, secret = self.storage.get_hostname(self.contact_id)
        url = f'http://{market}/orders'
        param = {"contact_id": self.contact_id}
        while True:
            if not self.marketplace_toggle:
                return
            if not self.orders_toggle:
                await asyncio.sleep(1)
                continue
            result = await self.utils.make_request(self.contact_id, secret, url, param)
            if "error" in result:
                pass
            else:
                current_ids = set()
                for order in result:
                    order_id = order.get('order_id')
                    order_status = order.get('status')
                    order_remaining = order.get('remaining')
                    current_ids.add(order_id)
                    if order_id not in self.orders_data:
                        order_view = OrderView(
                            self, self.storage, self.utils, self.units, self.commands, self.font, order, self.contact_id
                        )
                        self.orders_data[order_id] = order_view
                        self.items_list.insert(0, order_view)
                    else:
                        existing_order = self.orders_data[order_id]
                        if order_status == "completed":
                            color = GREENYELLOW
                        elif order_status == "pending":
                            color = WHITE
                        elif order_status == "expired":
                            color = RED
                            if not existing_order.pay_toggle:
                                existing_order.order_info.remove(existing_order.pay_button)
                                existing_order.order_info.remove(existing_order.cancel_button)
                                existing_order.pay_toggle = True
                        elif order_status == "paid":
                            color = YELLOW
                        elif order_status == "cancelled":
                            color = ORANGE
                        if order_remaining <= 0 or order_status != "pending":
                            remaining_time = ""
                            remaining_background_color = rgb(40,43,48)
                            remaining_enabled = False
                        else:
                            remaining_time = self.units.create_timer(order_remaining)
                            remaining_background_color = rgb(30,33,36)
                            remaining_enabled = True

                        if existing_order.status_label.text != order_status:    
                            existing_order.status_label._impl.native.Text = order_status
                            existing_order.status_label.style.color = color
                        existing_order.remaining_label._impl.native.Text = remaining_time
                        existing_order.remaining_label.style.background_color = remaining_background_color
                        existing_order.remaining_label._impl.native.Enabled = remaining_enabled

                for order_view in self.items_list.children:
                    if order_view.order_id not in current_ids:
                        self.items_list.remove(order_view)
                        del self.items_data[order_view.order_id]
            
            await asyncio.sleep(60)

    

    def show_items_list(self, button):
        if not self.items_toggle:
            self.orders_toggle = None
            self.orders_button.enabled = False
            self.orders_button.text = "My Orders"
            self.items_list.clear()
            self.items_data.clear()
            self.app.add_background_task(self.get_market_items)
            self.orders_button.on_press = self.show_orders_list


    def show_orders_list(self, button):
        if not self.orders_toggle:
            self.items_toggle = None
            self.orders_button.enabled = False
            self.orders_button.text = "Market"
            self.items_list.clear()
            self.orders_data.clear()
            self.app.add_background_task(self.get_market_orders)
            self.orders_button.on_press = self.show_items_list


    def _handle_on_resize(self, sender, event:Sys.EventArgs):
        min_width = 916
        min_height = 646
        self._impl.native.MinimumSize = Drawing.Size(min_width, min_height)


    def orders_button_mouse_enter(self, sender, event):
        self.orders_button.style.color = BLACK
        self.orders_button.style.background_color = YELLOW

    def orders_button_mouse_leave(self, sender, event):
        self.orders_button.style.color = GRAY
        self.orders_button.style.background_color = rgb(30,33,36)

    def window_icon(self, path):
        icon_path = Os.Path.Combine(str(self.app.paths.app), path)
        icon = Drawing.Icon(icon_path)
        return icon


    def close_market_window(self, widget):
        self.marketplace_toggle = None
        self.chat.marketplace_toggle = None
        self.close()



class AddItem(Window):
    def __init__(self, main:Window, settings, utils, tr, font):
        super().__init__(
            resizable=False
        )

        self.main = main
        self.settings = settings
        self.utils = utils
        self.tr = tr
        self.font = font

        self.storage = StorageMarket(self.app)

        self.title = "Add Item"
        self.size = (500, 450)
        position_center = self.utils.windows_screen_center(self.main, self)
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

        self.title_label = Label(
            text="Title :",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                padding = (21,0,0,0)
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
                padding = (92,0,0,0)
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
                padding = (20,15,0,15)
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

        text = self.tr.text("character_count")
        value = "0 / 2000"

        self.character_count = Label(
            text=f"{text} {value}",
            style=Pack(
                background_color = rgb(40,43,48),
                text_align = RIGHT,
                color = GRAY,
                flex = 1,
                padding = (0,15,0,0)
            )
        )
        self.character_count._impl.native.Font = self.font.get(8)

        self.description_input = MultilineTextInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                padding = (0,15,0,15)
            ),
            on_change=self.update_character_count
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
            self.character_count,
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

        description = self.description_input.value.strip()
        character_count = len(description)
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
        elif character_count > 2000:
            self.main.error_dialog(
                title="Description Too Long",
                message="Description exceeds the maximum length of 2000 characters."
            )
            return
        quantity = int(self.quantity_input.value)
        if quantity < 1:
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

        price = self.price_input.value
        currency = self.currencies_selection.value.currency
        timestamp = int(datetime.now(timezone.utc).timestamp())
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


    def update_character_count(self, input):
        message = self.description_input.value
        text = self.tr.text("character_count")
        value = "0 / 2000"
        if not message:
            self.character_count.text = f"{text} {value}"
            return
        character_count = len(message)
        if character_count > 2000:
            self.character_count.style.color = RED
        elif character_count < 2000:
            self.character_count.style.color = GRAY
        elif character_count == 2000:
            self.character_count.style.color = YELLOW
        value = f"{character_count} / 2000"
        self.character_count.text = f"{text} {value}"


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



class AddQuantity(Window):
    def __init__(self, main:Window, utils, tr, font, item_id):
        super().__init__()

        self.main = main
        self.utils = utils
        self.tr = tr
        self.font = font

        self.storage = StorageMarket(self.app)

        self.title = "Add Quantity"
        self.size = (200, 100)
        position_center = self.utils.windows_screen_center(self.main, self)
        self.position = position_center
        self._impl.native.ControlBox = False
        self._impl.native.ShowInTaskbar = False

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.item_id = item_id

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.quantity_input = NumberInput(
            value=1,
            step=1,
            min=1,
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                flex = 1,
                text_align = CENTER,
                padding = (0,10,0,0)
            )
        )
        self.quantity_input._impl.native.Font = self.font.get(11, True)

        self.add_button = Button(
            text="Add",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36)
            ),
            on_press=self.add_quantity
        )
        self.add_button._impl.native.Font = self.font.get(9, True)
        self.add_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.add_button._impl.native.MouseEnter += self.add_button_mouse_enter
        self.add_button._impl.native.MouseLeave += self.add_button_mouse_leave

        self.inputs_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                flex = 1,
                alignment = CENTER,
                padding = (10,10,15,10)
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
            on_press=self.close_addquantity
        )
        self.cancel_button._impl.native.Font = self.font.get(self.tr.size("cancel_button"), True)
        self.cancel_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.cancel_button._impl.native.MouseEnter += self.cancel_button_mouse_enter
        self.cancel_button._impl.native.MouseLeave += self.cancel_button_mouse_leave

        self.content = self.main_box

        self.main_box.add(
            self.inputs_box,
            self.cancel_button
        )
        self.inputs_box.add(
            self.quantity_input,
            self.add_button
        )


    async def add_quantity(self, button):
        quantity = int(self.quantity_input.value)
        if not quantity:
            return
        if quantity < 1:
            return
        item = self.storage.get_item(self.item_id)
        new_quantity = quantity + item[6]
        self.storage.update_item_quantity(self.item_id, new_quantity)
        self.close()
        self.app.current_window = self.main


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


    def close_addquantity(self, button):
        self.close()
        self.app.current_window = self.main



class Item(Box):
    def __init__(self, app:App ,main:Window, storage, utils, tr, font, item):
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
        self.storage = storage
        self.utils = utils
        self.tr = tr
        self.font = font
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
            title="Copy item id",
            icon="images/copy_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.copy_id_cmd_mouse_enter,
            mouse_leave=self.copy_id_cmd_mouse_leave,
            action=self.copy_item_id
        )
        self.add_quantity_cmd = Command(
            title="Add quantity",
            icon="images/add_i.ico",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.add_quantity_cmd_mouse_enter,
            mouse_leave=self.add_quantity_cmd_mouse_leave,
            action=self.add_quantity_to_item
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
            self.add_quantity_cmd,
            self.remove_item_cmd
        ]
        for command in commands:
            context_menu.Items.Add(command)
        self._impl.native.ContextMenuStrip = context_menu
        self.item_image._impl.native.ContextMenuStrip = context_menu
        self.item_title._impl.native.ContextMenuStrip = context_menu
        self.item_id_label._impl.native.ContextMenuStrip = context_menu
        self.item_price._impl.native.ContextMenuStrip = context_menu
        self.item_currency._impl.native.ContextMenuStrip = context_menu
        self.item_quantity._impl.native.ContextMenuStrip = context_menu


    def copy_item_id(self):
        self.clipboard.copy(self.item_id)
        self.main.info_dialog(
            title="Copied",
            message="The item id has copied to clipboard.",
        )

    
    def add_quantity_to_item(self):
        add_quantity_window = AddQuantity(self.main, self.utils, self.tr, self.font, self.item_id)
        add_quantity_window._impl.native.ShowDialog(self.main._impl.native)


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

    def add_quantity_cmd_mouse_enter(self):
        self.add_quantity_cmd.icon = "images/add_a.ico"
        self.add_quantity_cmd.color = Color.BLACK

    def add_quantity_cmd_mouse_leave(self):
        self.add_quantity_cmd.icon = "images/add_i.ico"
        self.add_quantity_cmd.color = Color.WHITE

    def remove_item_cmd_mouse_enter(self):
        self.remove_item_cmd.icon = "images/remove_item_a.ico"
        self.remove_item_cmd.color = Color.BLACK

    def remove_item_cmd_mouse_leave(self):
        self.remove_item_cmd.icon = "images/remove_item_i.ico"
        self.remove_item_cmd.color = Color.WHITE




class Order(Box):
    def __init__(self, main:Window, storage, units, font, order):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 55,
                alignment = CENTER
            )
        )

        self.main = main
        self.storage = storage
        self.units = units
        self.font = font
        self.tootip = ToolTip()
        self.clipboard = ClipBoard()

        self.paid_toggle = None

        self.order_id, self.item_id, contact_id, total_price, quantity, comment, status, created, expired = order
        now = int(datetime.now(timezone.utc).timestamp())
        remaining_seconds = expired - now
        if remaining_seconds <= 0 or status != "expired":
            remaining_time = ""
            remaining_background_color = rgb(40,43,48)
            remaining_enabled = False
        else:
            remaining_time = self.units.create_timer(remaining_seconds, True)
            remaining_background_color = rgb(30,33,36)
            remaining_enabled = True

        if status == "completed":
            color = GREENYELLOW
        elif status == "pending":
            color = WHITE
        elif status == "expired":
            color = RED
        elif status == "paid":
            color = YELLOW
        elif status == "cancelled":
            color = ORANGE

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
            text=f"{self.order_id[:15]}...",
            style=Pack(
                color = WHITE,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 2
            )
        )
        self.order_id_label._impl.native.Font = self.font.get(10, True)
        self.tootip.insert(self.order_id_label._impl.native, self.order_id)

        self.item_id_label = Label(
            text=f"{self.item_id[:15]}...",
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.item_id_label._impl.native.Font = self.font.get(9, True)

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
                color = color,
                text_align = CENTER,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )
        self.status_label._impl.native.Font = self.font.get(10, True)

        self.remaining_label = TextInput(
            value="",
            readonly=True,
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                background_color = remaining_background_color,
                width = 80,
                padding = (0,20,0,0)
            )
        )
        self.remaining_label._impl.native.Font = self.font.get(10, True)
        self.remaining_label._impl.native.Text = remaining_time
        self.remaining_label._impl.native.BorderStyle = BorderStyle.NONE
        self.remaining_label._impl.native.Enabled = remaining_enabled

        self.order_info = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                height = 50,
                alignment = CENTER
            )
        )

        self.item_title = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                padding = (5,0,0,10)
            )
        )
        self.item_title._impl.native.Font = self.font.get(10, True)

        self.comment_label = Label(
            text="Comment :",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                padding = (5,0,0,10)
            )
        )
        self.comment_label._impl.native.Font = self.font.get(10, True)

        self.comment_value = RichLabel(
            text=comment,
            font= self.font.get(9, True),
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            wrap=True,
            readonly=True,
            dockstyle=DockStyle.FILL,
            borderstyle=BorderStyle.NONE
        )

        self.comment_value_box = Box(
            style=Pack(
                background_color=rgb(30,33,36),
                padding = (5,0,0,20),
                flex = 1
            )
        )

        self.quantity_value = Label(
            text=f"Quantity : {quantity}",
            style=Pack(
                color = WHITE,
                background_color=rgb(30,33,36),
                padding = (5,0,5,10)
            )
        )
        self.quantity_value._impl.native.Font = self.font.get(10, True)

        self.order_details = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                padding = (10,5,5,10),
                height = 200,
                alignment = CENTER
            )
        )

        self.more_button = Button(
            text="More",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                padding = (0,10,0,0)
            ),
            on_press=self.show_more
        )
        self.more_button._impl.native.Font = self.font.get(9, True)
        self.more_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.more_button._impl.native.MouseEnter += self.more_button_mouse_enter
        self.more_button._impl.native.MouseLeave += self.more_button_mouse_leave

        self.confirm_button = Button(
            text="Confirm",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                width = 80,
                padding = (0,10,0,0)
            ),
            on_press=self.confirm_order
        )
        self.confirm_button._impl.native.Font = self.font.get(9, True)
        self.confirm_button._impl.native.FlatStyle = FlatStyle.FLAT
        self.confirm_button._impl.native.MouseEnter += self.pay_button_mouse_enter
        self.confirm_button._impl.native.MouseLeave += self.pay_button_mouse_leave

        self.add(
            self.order_info
        )
        self.order_info.add(
            self.order_icon,
            self.order_id_label,
            self.total_price_label,
            self.status_label,
            self.remaining_label
        )
        if status == "paid":
            self.order_info.add(
                self.confirm_button
            )
            self.paid_toggle = True
        self.order_info.add(
            self.more_button
        )


    async def show_more(self, button):
        self.more_button.enabled = False
        self.style.height = 280
        self.more_button.text = "Less"
        item = self.storage.get_item(self.item_id)
        self.item_title.text = f"Item Title : {item[1]}"
        self.add(self.order_details)
        self.order_details.add(
            self.item_title,
            self.comment_label,
            self.comment_value_box,
            self.quantity_value
        )
        self.comment_value_box._impl.native.Controls.Add(self.comment_value)
        self.more_button.on_press = self.show_less
        self.more_button.enabled = True


    async def show_less(self, button):
        self.more_button.enabled = False
        self.style.height = 55
        self.more_button.text = "More"
        self.comment_value_box._impl.native.Controls.Remove(self.comment_value)
        self.order_details.remove(
            self.item_title,
            self.comment_label,
            self.comment_value_box,
            self.quantity_value
        )
        self.remove(self.order_details)
        self.more_button.on_press = self.show_more
        self.more_button.enabled = True


    async def confirm_order(self, button):
        def on_result(widget, result):
            if result is True:
                self.storage.update_order_status(self.order_id, "completed")
                self.order_info.remove(self.confirm_button)
        self.main.question_dialog(
            title="Confirm Completion",
            message="Are you sure you want to mark this order as complete ?",
            on_result=on_result
        )


    def pay_button_mouse_enter(self, sender, event):
        self.confirm_button.style.color = BLACK
        self.confirm_button.style.background_color = GREENYELLOW

    def pay_button_mouse_leave(self, sender, event):
        self.confirm_button.style.color = GRAY
        self.confirm_button.style.background_color = rgb(30,33,36)


    def more_button_mouse_enter(self, sender, event):
        self.more_button.style.color = WHITE

    def more_button_mouse_leave(self, sender, event):
        self.more_button.style.color = GRAY



class MarketPlace(Window):
    def __init__(self, main:Window, notify, settings, utils, units, tr, font, server):
        super().__init__()

        self.main = main
        self.notify = notify
        self.settings = settings
        self.utils = utils
        self.units = units
        self.tr = tr
        self.font = font
        self.server = server

        self.market_storage = StorageMarket(self.app)
        self.message_storage = StorageMessages(self.app)

        self.title = "Market Place"
        self._impl.native.Icon = self.window_icon("images/Market.ico")
        self.size = (900,607)
        self._impl.native.Opacity = self.main._impl.native.Opacity
        position_center = self.utils.windows_screen_center(self.main, self)
        self.position = position_center
        self._impl.native.Resize += self._handle_on_resize
        self.on_close = self.close_market_window

        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)

        self.items_data = {}
        self.orders_data = {}
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
            self.menu_box
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

        self.app.loop.create_task(self.load_items_list())
        self.app.loop.create_task(self.updating_items_list())
        self.app.loop.create_task(self.updating_orders_list())



    async def load_items_list(self):
        market_items = self.market_storage.get_market_items()
        if market_items:
            sorted_items = sorted(market_items, key=lambda x: x[7], reverse=True)
            for item in sorted_items[:20]:
                item_id = item[0]
                item_info = Item(self.app, self, self.market_storage, self.utils, self.tr, self.font, item)
                self.items_data[item_id] = item_info
                self.items_list.add(item_info)
        await asyncio.sleep(0.5)
        self.main_box.add(self.items_scroll)
        self.orders_button.enabled = True
        self.items_toggle = True


    async def load_orders_list(self):
        market_orders = self.market_storage.get_market_orders()
        if market_orders:
            sorted_orders = sorted(market_orders, key=lambda x: x[7], reverse=True)
            for order in sorted_orders[:20]:
                order_id = order[0]
                order_info = Order(self, self.market_storage, self.units, self.font, order)
                self.orders_data[order_id] = order_info
                self.items_list.add(order_info)
        await asyncio.sleep(0.5)
        self.main_box.add(self.items_scroll)
        self.orders_button.enabled = True
        self.orders_toggle = True


    async def updating_items_list(self):
        while True:
            if not self.main.marketplace_toggle:
                return
            if not self.items_toggle:
                await asyncio.sleep(1)
                continue
            market_items = self.market_storage.get_market_items()
            if market_items:
                sorted_items = sorted(market_items, key=lambda x: x[7], reverse=True)
                for item in sorted_items[:20]:
                    item_id = item[0]
                    if item_id not in self.items_data:
                        item_info = Item(self.app, self, self.market_storage, self.utils, self.tr, self.font, item)
                        self.items_data[item_id] = item_info
                        if not self.search_toggle:
                            self.items_list.insert(0, item_info)
                            if len(self.items_data) > 20:
                                child = self.items_list.children[20]
                                self.items_list.remove(child)
                    else:
                        existing_item = self.items_data[item_id]
                        if existing_item.item_quantity.text != f"QN: {item[6]}":
                            existing_item.item_quantity.text = f"QN: {item[6]}"

            await asyncio.sleep(3)


    async def updating_orders_list(self):
        while True:
            if not self.main.marketplace_toggle:
                return
            if not self.orders_toggle:
                await asyncio.sleep(1)
                continue
            market_orders = self.market_storage.get_market_orders()
            if market_orders:
                sorted_orders = sorted(market_orders, key=lambda x: x[7], reverse=True)
                for order in sorted_orders[:20]:
                    order_id = order[0]
                    order_status = order[6]
                    order_expired = order[8]
                    if order_id not in self.orders_data:
                        order_info = Order(self, self.market_storage, self.units, self.font, order)
                        self.orders_data[order_id] = order_info
                        if not self.search_toggle:
                            self.items_list.insert(0, order_info)
                            if len(self.orders_data) > 20:
                                child = self.items_list.children[20]
                                self.items_list.remove(child)
                    else:
                        now = int(datetime.now(timezone.utc).timestamp())
                        existing_order = self.orders_data[order_id]
                        if order_status == "completed":
                            color = GREENYELLOW
                        elif order_status == "pending":
                            color = WHITE
                        elif order_status == "expired":
                            color = RED
                        elif order_status == "paid":
                            color = YELLOW
                            if not existing_order.paid_toggle:
                                existing_order.order_info.insert(5, existing_order.confirm_button)
                                existing_order.paid_toggle = True
                        elif order_status == "cancelled":
                            color = ORANGE
                        if order_expired <= now or order_status != "pending":
                            remaining_time = ""
                            remaining_background_color = rgb(40,43,48)
                            remaining_enabled = False
                        else:
                            expired = datetime.fromtimestamp(order_expired, tz=timezone.utc)
                            remaining_time = self.units.create_timer(expired, True)
                            remaining_background_color = rgb(30,33,36)
                            remaining_enabled = True

                        if existing_order.status_label.text != order_status:
                            existing_order.status_label._impl.native.Text = order_status
                            existing_order.status_label.style.color = color
                        existing_order.remaining_label._impl.native.Text = remaining_time
                        existing_order.remaining_label.style.background_color = remaining_background_color
                        existing_order.remaining_label._impl.native.Enabled = remaining_enabled

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
            self.main_box.remove(self.items_scroll)
            self.menu_box.remove(self.add_button)
            self.orders_button._impl.native.Text = "Items"
            self.search_input.placeholder = " Order ID"
            self.search_input.value = ""
            self.search_input.on_confirm = self.search_order
            self.orders_button.on_press = self.show_items_list
            self.items_list.clear()
            self.items_data.clear()
            self.app.loop.create_task(self.load_orders_list())


    async def show_items_list(self, button):
        if not self.items_toggle:
            self.orders_toggle = None
            self.orders_button.enabled = False
            self.main_box.remove(self.items_scroll)
            self.orders_button._impl.native.Text = "Orders"
            self.search_input.placeholder=" Item ID or Title"
            self.search_input.value = ""
            self.search_input.on_confirm = self.search_item
            self.orders_button.on_press = self.show_orders_list
            self.items_list.clear()
            self.orders_data.clear()
            self.app.loop.create_task(self.load_items_list())
            self.menu_box.insert(0, self.add_button)


    def search_item(self, input):
        if not input.value:
            return
        item = self.market_storage.get_item(input.value.strip())
        if item:
            self.items_list.clear()
            info_item = Item(self, self.market_storage, self.utils, self.tr, self.font, item)
            self.items_list.add(info_item)
            self.search_toggle = True
        else:
            market_items = self.market_storage.search_title(input.value.strip())
            if market_items:
                self.items_list.clear()
                sorted_items = sorted(market_items, key=lambda x: x[7], reverse=True)
                for item in sorted_items:
                    info_item = Item(self.app, self, self.market_storage, self.utils, self.tr, self.font, item)
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
        order = self.market_storage.get_order(input.value.strip())
        if order:
            self.items_list.clear()
            info_order = Order(self, self.market_storage, self.font, order)
            self.items_list.add(info_order)
            self.search_toggle = True
        else:
            self.error_dialog(
                title="Not Found",
                message="The order is not found."
            )

        
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

    def window_icon(self, path):
        icon_path = Os.Path.Combine(str(self.app.paths.app), path)
        icon = Drawing.Icon(icon_path)
        return icon


    def close_market_window(self, widget):
        self.main.marketplace_toggle = None
        self.close()
        self.app.current_window = self.main