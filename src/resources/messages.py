
import asyncio

from toga import App, Box, Label
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.colors import rgb, WHITE, GRAY

from .storage import Storage


class NewMessenger(Box):
    def __init__(self):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )

        self.new_label = Label(
            text="There no messages address for this wallet, click the button to create new messages address",
            style=Pack(
                text_align = CENTER,
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight = BOLD,
                font_size = 12
            )
        )
        self.create_label = Label(
            text="New Messenger",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1,
                padding_top = 6
            )
        )
        self.create_button = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(30,33,36),
                alignment = CENTER,
                padding_top = 10,
                width = 200,
                height = 40
            )
        )
        self.create_button._impl.native.MouseEnter += self.create_button_mouse_enter
        self.create_button._impl.native.MouseLeave += self.create_button_mouse_leave
        self.create_label._impl.native.MouseEnter += self.create_button_mouse_enter
        self.create_label._impl.native.MouseLeave += self.create_button_mouse_leave

        self.add(
            self.new_label,
            self.create_button
        )
        self.create_button.add(
            self.create_label
        )

    
    def create_button_mouse_enter(self, sender, event):
        self.create_label.style.color = WHITE
        self.create_label.style.background_color = rgb(114,137,218)
        self.create_button.style.background_color = rgb(114,137,218)

    def create_button_mouse_leave(self, sender, event):
        self.create_label.style.color = GRAY
        self.create_label.style.background_color = rgb(30,33,36)
        self.create_button.style.background_color = rgb(30,33,36)


class Messages(Box):
    def __init__(self, app:App):
        super().__init__(
            style=Pack(
                direction = ROW,
                flex = 1,
                background_color = rgb(40,43,48),
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )

        self.app = app
        self.storage = Storage(self.app)

        self.messages_toggle = None

        
    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.messages_toggle:
            data = self.storage.is_exists()
            if data:
                pass
            else:
                self.new_messenger = NewMessenger()
                self.add(
                    self.new_messenger
                )
            self.messages_toggle = True