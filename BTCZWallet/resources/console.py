
import asyncio
from datetime import datetime
import webbrowser
import json
import re
from PIL import Image

from toga import Window, Box, TextInput, Label, ImageView
from ..framework import (
    FormBorderStyle, RichLabel, DockStyle, Color,
    BorderStyle, Sys, Forms, Keys, ToolTip, MenuStrip,
    ClipBoard, Os, run_async
)
from toga.style.pack import Pack
from toga.colors import rgb, GRAY
from toga.constants import COLUMN, CENTER, ROW, YELLOW, BLACK


class Console(Window):
    def __init__(self, main:Window, settings, utils, commands, font):
        super().__init__()

        self.main = main
        self.settings = settings
        self.utils = utils
        self.commands = commands
        self.font = font

        self.tooltip = ToolTip()
        self.clipboard = ClipBoard()

        self.title = "Console"
        self._impl.native.BackColor = Color.rgb(30,30,30)
        self._impl.native.Owner = self.main._impl.native
        self._impl.native.FormBorderStyle = FormBorderStyle.NONE
        self._impl.native.ShowInTaskbar = False
        self._impl.native.Move += self._on_console_move
        self._impl.native.KeyDown += Forms.KeyEventHandler(self.on_key_down)
        self._impl.native.Activated += self._handle_on_activated
        self._impl.native.Deactivate += self._handle_on_deactivated
        self.on_close = self.on_close_console

        self._is_active = False
        self.log_toggle = None
        self.shell_toggle = None
        self.detach_toggle = None
        self.inside_toggle = None

        self.shell_cmds = []
        self.shell_history_index = None

        self.recording = None
        self.recording_path = None
        self.recording_temp = None
        self.frame_index = 0

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,30,30),
                flex = 1,
                alignment = CENTER
            )
        )

        self.console_output_logs = RichLabel(
            readonly=True,
            dockstyle=DockStyle.FILL,
            background_color=Color.rgb(20,20,20),
            wrap=True,
            urls=True,
            borderstyle=BorderStyle.NONE,
            urls_click=self.open_url
        )
        self.console_output_shell = RichLabel(
            readonly=True,
            dockstyle=DockStyle.FILL,
            background_color=Color.rgb(20,20,20),
            wrap=True,
            urls=True,
            borderstyle=BorderStyle.NONE,
            urls_click=self.open_url,
            mouse_move=True
        )
        self.console_output_logs.KeyDown += Forms.KeyEventHandler(self.on_key_down)
        self.console_output_shell.KeyDown += Forms.KeyEventHandler(self.on_key_down)
        self.console_output_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(20,20,20),
                flex = 1,
                padding = (5,0,0,5)
            )
        )

        self.input_label = Label(
            text="BTCZ :",
            style=Pack(
                color = GRAY,
                background_color = rgb(0,0,0),
                padding = (2,0,0,5)
            )
        )
        self.input_label._impl.native.Font = self.font.get(9)

        self.console_input = TextInput(
            style=Pack(
                color = YELLOW,
                background_color = BLACK,
                flex = 1,
                padding = (2,0,2,0)
            ),
            on_confirm=self.verify_command
        )
        self.console_input._impl.native.Font = self.font.get(10)
        self.console_input._impl.native.BorderStyle = BorderStyle.NONE
        self.console_input._impl.native.KeyDown += Forms.KeyEventHandler(self.on_shell_key_down)
        self.console_input._impl.native.MouseUp += self.on_mouse_up
        self.console_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(0,0,0)
            )
        )
        self.console_input_box.add(
            self.input_label,
            self.console_input
        )

        self.output_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(20,20,20),
                flex = 1
            )
        )

        self.detach_button = ImageView(
            image="images/detach_i.png",
            style=Pack(
                background_color = rgb(20,20,20),
                width = 17,
                height =17,
                padding = (0,0,30,0)
            )
        )
        self.tooltip.insert(self.detach_button._impl.native, "Detach console")
        self.detach_button._impl.native.MouseEnter += self.detach_button_mouse_enter
        self.detach_button._impl.native.MouseLeave += self.detach_button_mouse_leave
        self.detach_button._impl.native.Click += self.detach_button_click

        self.log_button = ImageView(
            image="images/log_i.png",
            style=Pack(
                background_color = rgb(30,30,30),
                width = 25,
                height =25,
                padding = 5
            )
        )
        self.tooltip.insert(self.log_button._impl.native, "Logs")
        self.log_button._impl.native.MouseEnter += self.log_button_mouse_enter
        self.log_button._impl.native.MouseLeave += self.log_button_mouse_leave
        self.log_button._impl.native.Click += self.log_button_click

        self.shell_button = ImageView(
            image="images/shell_i.png",
            style=Pack(
                background_color = rgb(30,30,30),
                width = 25,
                height =25,
                padding = 5
            )
        )
        self.tooltip.insert(self.shell_button._impl.native, "Shell cmd")
        self.shell_button._impl.native.MouseEnter += self.shell_button_mouse_enter
        self.shell_button._impl.native.MouseLeave += self.shell_button_mouse_leave
        self.shell_button._impl.native.Click += self.shell_button_click

        self.tabs_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(20,20,20),
                alignment = CENTER,
                padding = (5,0,0,0)
            )
        )

        self.console_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(20,20,20),
                flex = 1,
                padding = 3
            )
        )

        self.content = self.main_box

        self.console_box.add(
            self.output_box
        )
        self.output_box.add(
            self.console_output_box
        )

        self.insert_menustrip()


    def insert_menustrip(self):
        context_menu = MenuStrip(self.rtl)
        self.console_input._impl.native.ContextMenuStrip = context_menu


    def show_console(self, startup:bool = None):
        if startup:
            self.size = (self.main.size.width + 2, self.main.size.height + 32)
            self._impl.native.Left = self.main._impl.native.Right - 7
            self._impl.native.Top = self.main._impl.native.Top
            self.main_box.add(self.console_box)
        else:
            self.size = (self.main.size.width + 2, int(self.main.size.height / 3))
            self._impl.native.Left = self.main._impl.native.Left + 7
            self.console_box.insert(0, self.tabs_box)
            self.tabs_box.add(
                self.log_button,
                self.shell_button
            )
            if self.detach_toggle:
                self._impl.native.Top = self.main._impl.native.Bottom + 15
                self._impl.native.Left = self.main._impl.native.Left - 30
            else:
                self.tabs_box.insert(0, self.detach_button)
                self._impl.native.Top = self.main._impl.native.Bottom - 8
            if self.main._is_maximized or self.main._is_snapped_left or self.main._is_snapped_right:
                self.main.main_box.insert(4, self.console_box)
            else:
                self.main_box.add(self.console_box)
                
        if not self.log_toggle and not self.shell_toggle:
            self.display_log()
        else:
            if self.log_toggle:
                self.display_log()
            else:
                self.display_shell()   
        self.show()
        self.main._impl.native.Activate()


    def detach_button_click(self, sender, event):
        if not self.detach_toggle:
            self.detach_console()


    def detach_console(self):
        self.tabs_box.remove(self.detach_button)
        self.hide()
        self._impl.native.ShowInTaskbar = True
        mode = 0
        if self.utils.get_app_theme() == "dark":
            mode = 1
        self.utils.apply_title_bar_mode(self, mode)
        self._impl.native.FormBorderStyle = FormBorderStyle.SIZABLE
        self._impl.native.Top = self.main._impl.native.Bottom + 15
        self._impl.native.Left = self.main._impl.native.Left - 30
        self.show()
        self.detach_toggle = True

    def attach_console(self):
        self.tabs_box.insert(0, self.detach_button)
        self.hide()
        self._impl.native.ShowInTaskbar = False
        self._impl.native.FormBorderStyle = FormBorderStyle.NONE
        self.show()
        self.detach_toggle = None
        self.resize()
        self.move()


    def _on_console_move(self, sender, event):
        if self.detach_toggle:
            side = self.detect_touch(self.main._impl.native, self._impl.native)
            if side:
                self.attach_console()


    def detect_touch(self, main, console, tolerance: int = 5, side_tolerance: int = 25):
        m = main.Bounds
        o = console.Bounds
        vertical_touch = abs(o.Top - m.Bottom) <= tolerance
        within_horizontal_bounds = (
            (o.Left >= m.Left - side_tolerance) and
            (o.Right <= m.Right + side_tolerance)
        )
        if vertical_touch and within_horizontal_bounds:
            return True
        return None


    def log_button_click(self, sender, event):
        if not self.log_toggle:
            self.display_log()

    def shell_button_click(self, sender, event):
        if not self.shell_toggle:
            self.display_shell()

    def display_log(self):
        self.log_button.image = "images/log_a.png"
        self.log_button.style.background_color = GRAY
        if self.shell_toggle:
            self.shell_button.image = "images/shell_i.png"
            self.shell_button.style.background_color = rgb(30,30,30)
            self.output_box.remove(self.console_input_box)
            self.console_output_box._impl.native.Controls.Remove(self.console_output_shell)
        self.console_output_box._impl.native.Controls.Add(self.console_output_logs)
        self.console_output_logs.ScrollToCaret()
        self.console_output_logs.Focus()
        self.log_toggle = True
        self.shell_toggle = None

    def display_shell(self):
        self.shell_button.image = "images/shell_a.png"
        self.shell_button.style.background_color = GRAY
        if self.log_toggle:
            self.log_button.image = "images/log_i.png"
            self.log_button.style.background_color = rgb(30,30,30)
            self.console_output_box._impl.native.Controls.Remove(self.console_output_logs)
        self.console_output_box._impl.native.Controls.Add(self.console_output_shell)
        self.output_box.add(self.console_input_box)
        self.console_output_shell.ScrollToCaret()
        self.console_input.focus()
        self.shell_toggle = True
        self.log_toggle = None


    def move(self, startup:bool = None):
        if not self.detach_toggle:
            if startup:
                self._impl.native.Left = self.main._impl.native.Right - 7
                self._impl.native.Top = self.main._impl.native.Top
            else:
                self._impl.native.Left = self.main._impl.native.Left + 7
                self._impl.native.Top = self.main._impl.native.Bottom - 8

    def resize(self):
        if not self.detach_toggle:
            self.size = (self.main.size.width + 2, int(self.main.size.height / 3))
            self._impl.native.Width = self.main._impl.native.Width - 15
            self._impl.native.Top = self.main._impl.native.Bottom - 8

    def move_inside(self):
        if not self.detach_toggle:
            self.main_box.remove(self.console_box)
            self.main.main_box.insert(4, self.console_box)
            if self.log_toggle:
                self.console_output_logs.ScrollToCaret()
            else:
                self.console_output_shell.ScrollToCaret()
            self.hide()
            self.inside_toggle = True

    def move_outside(self):
        if not self.detach_toggle:
            self.size = (self.main.size.width + 2, int(self.main.size.height / 3))
            self.main.main_box.remove(self.console_box)
            self.main_box.add(self.console_box)
            self.show()
            if self.log_toggle:
                self.console_output_logs.ScrollToCaret()
            else:
                self.console_output_shell.ScrollToCaret()
            self.inside_toggle = None


    def log(self, text, color):
        self.console_output_logs.SelectionStart = self.console_output_logs.TextLength
        self.console_output_logs.SelectionLength = 0
        self.console_output_logs.SelectionColor = color
        self.console_output_logs.AppendText(text + "\n")
        self.console_output_logs.SelectionColor = Color.WHITE
        self.console_output_logs.ScrollToCaret()

    def shell(self, text, color):
        self.console_output_shell.SelectionStart = self.console_output_shell.TextLength
        self.console_output_shell.SelectionLength = 0
        self.console_output_shell.SelectionColor = color
        self.console_output_shell.AppendText(text + "\n")
        self.console_output_shell.SelectionColor = Color.WHITE
        self.console_output_shell.ScrollToCaret()


    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def invoke(self, func):
        self._impl.native.Invoke(Forms.MethodInvoker(func))

    def info_log(self, text):
        self.invoke(lambda: self.log(f"{self.timestamp()} - {text}", Color.WHITE))

    def info_shell(self, text):
        self.invoke(lambda: self.shell(f"{text}", Color.rgb(114,137,218)))

    def command_shell(self, text):
        self.shell_cmds.append(text)
        self.shell_history_index = None
        self.invoke(lambda: self.shell(f"{self.timestamp()} - {text}", Color.GREENYELLO))
    
    def error_log(self, text):
        self.invoke(lambda: self.log(f"{self.timestamp()} - {text}", Color.RED))
    
    def error_shell(self, text):
        self.invoke(lambda: self.shell(f"{self.timestamp()} - {text}", Color.RED))

    def warning_log(self, text):
        self.invoke(lambda: self.log(f"{self.timestamp()} - {text}", Color.YELLOW))

    def server_log(self, text):
        self.invoke(lambda: self.log(f"{self.timestamp()} - {text}", Color.GREEN))

    def mining_log(self, text):
        self.invoke(lambda: self.log(f"{self.timestamp()} - {text}", Color.CYAN))


    async def verify_command(self, input):
        if not self.console_input.value:
            return
        value = self.console_input.value.strip()
        self.command_shell(value)
        self.console_input.value = ""

        if value in ["c", "clear"]:
            self.console_output_shell.Text = ""

        elif value in ["h", "help"]:
            self.info_shell(
                "\n📜 Usage :\n"
                "================================================\n"
                " → h or help :   Show this help message with available commands\n"
                " → c or clear :   Clear the console output window\n"
                " → data :   Open the BitcoinZ blockchain data directory\n"
                " → appdata :   Open the general application data directory\n"
                " → appconfig :   Open the application configuration directory\n"
                " → appcache :   Open the application cache directory\n"
                " → applogs :   Open the application logs directory\n"
                " → capture :   captures the application current visual state\n"
                " → record start/stop :   Record the current application window as an animated GIF (16 FPS)\n"
                "================================================\n"
                " → merge <address>: ! Merge all transparent balances from your wallet into a single address\n"
                "                     Usage: merge <address>\n"
                "                     Example: merge t1abc123def...\n\n"
                "================================================\n"
                " 👉 Slash commands (RPC calls):\n\n"
                "     Any input that starts with ' / ' will be\n"
                "     treated as a direct RPC command sent to\n"
                "     the BitcoinZ node.\n\n"
                " 👉 Examples:\n"
                " → /getinfo :   show blockchain info\n"
                " → /getblockcount :   get current block height\n"
                " → /getblockhash 100 :   get hash of block 100\n"
                " → /getwalletinfo :   display wallet information\n"
                "================================================"
            )

        elif value in ["appdata", "appconfig", "appcache", "applogs", "data"]:
            self.info_shell(f"open directory...")
            self.exlporer_dir(value)

        elif value == "capture":
            self.create_app_screenshot()

        elif value.startswith("record"):
            parts = value.split()
            if len(parts) < 2:
                self.error_shell("Usage: record start/stop")
            elif len(parts) > 2:
                self.error_shell("Too many arguments")
            else:
                option = parts[1]
                if option == "start":
                    if self.recording:
                        self.error_shell(f"Already recoding")
                        return
                    await self.record_app_window()
                elif option == "stop":
                    if not self.recording:
                        self.error_shell(f"Already stopped")
                        return
                    run_async(self.save_record())
                else:
                    self.error_shell(f"Invalid argument")

        elif value.startswith("merge"):
            parts = value.split()
            if len(parts) < 2:
                self.error_shell("Usage: merge <address>")
            elif len(parts) > 2:
                self.error_shell("Too many arguments")
            else:
                address = parts[1]
                if await self.is_valid(address):
                    self.info_shell(f"Merging to address : {address}")
                    await self.start_merging(address)
                else:
                    self.error_shell(f"Invalid address")

        elif value.startswith("/"):
            command_line = value[1:]
            command = f'{self.commands.bitcoinz_cli_file} {command_line}'
            result, error_message = await self.commands._run_command(command)
            if error_message:
                self.error_shell(float(error_message))
            else:
                self.info_shell(result)


    async def start_merging(self, address):
        balance = await self.get_transparent_balance()
        operation, error_message = await self.commands.sendToAddress(address, balance)
        if error_message:
            match = re.search(r"at least (\d+\.\d+)", error_message)
            if match:
                min_fee = float(match.group(1)) + 0.00000001
                self.info_shell(f"Merging fee : {min_fee:.8f}")
                balance = float(balance) - min_fee
                self.info_shell(balance)
                operation, error_message = await self.commands.sendToAddress(address, f"{balance:.8f}")
                if error_message:
                    self.error_shell(error_message)
                    return
        if operation:
            self.info_shell(f"Operation Result : {operation}")


    async def is_valid(self, address):
        result,_ = await self.commands.validateAddress(address)
        if result is not None:
            result = json.loads(result)
            is_valid = result.get('isvalid')
            if is_valid is True:
                return True
            return None


    async def get_transparent_balance(self):
        total_balances, _ = await self.commands.z_getTotalBalance()
        if total_balances:
            balances = json.loads(total_balances)
            transparent = balances.get('transparent')
            return transparent


    def exlporer_dir(self, value):
        if value == "appdata":
            dir = str(self.app.paths.data)
        elif value == "appconfig":
            dir = str(self.app.paths.config)
        elif value == "appcache":
            dir = str(self.app.paths.cache)
        elif value == "applogs":
            dir = str(self.app.paths.logs)
        elif value == "data":
            dir = self.utils.get_bitcoinz_path()

        psi = Sys.Diagnostics.ProcessStartInfo()
        psi.FileName = "explorer.exe"
        psi.Arguments = dir
        psi.UseShellExecute = True
        Sys.Diagnostics.Process.Start(psi)


    def create_app_screenshot(self):
        async def on_result(widget, result):
            if result:
                await asyncio.sleep(1)
                size = self.main._impl.native.Size
                if self.main.console_toggle and not self.detach_toggle and not self.inside_toggle:
                    size.Height += self._impl.native.Size.Height
                left = self.main._impl.native.Left
                top = self.main._impl.native.Top
                self.utils.capture_screenshot(size, left, top, str(result))
                self.info_shell(f"Secrenshot saved : {result}")
        self.save_file_dialog(
            title="Save screenshot",
            suggested_filename="BTCZWallet",
            file_types=["png"],
            on_result=on_result
        )


    async def record_app_window(self):
        async def on_result(widget, result):
            if result:
                self.info_shell(f"Start Recording")
                self.recording_path = str(result)
                self.recording_temp = Os.Path.Combine(str(self.app.paths.cache), "btcz_record")
                if not Os.Directory.Exists(self.recording_path):
                    Os.Directory.CreateDirectory(self.recording_temp)
                self.frame_index = 0
                self.recording = True
                await asyncio.sleep(0.2)
                run_async(self.start_recording())
        if not self.recording:
            self.save_file_dialog(
                title="Save record",
                suggested_filename="BTCZWallet",
                file_types=["gif"],
                on_result=on_result
            )


    async def start_recording(self):
        while self.recording:
            size = self.main._impl.native.Size
            if self.main.console_toggle and not self.detach_toggle and not self.inside_toggle:
                size.Height += self._impl.native.Size.Height
            left = self.main._impl.native.Left
            top = self.main._impl.native.Top
            frame = self.utils.record_screen(size, left, top)
            frame_path = Os.Path.Combine(self.recording_temp, f"frame_{self.frame_index:05d}.png")
            frame.save(frame_path, "PNG")
            self.frame_index += 1
            await asyncio.sleep(0.1)


    async def save_record(self):
        self.recording = None
        if not self.recording_temp:
            return
        files = list(Os.Directory.GetFiles(self.recording_temp, "frame_*.png"))
        files.sort()
        if not files:
            return
        self.info_shell(f"Saving record...")
        frames = [Image.open(f) for f in files]
        frames[0].save(
            self.recording_path,
            save_all=True,
            append_images=frames[1:],
            duration=160,
            loop=0
        )
        frames.clear()
        for f in files:
            Os.File.Delete(f)
        Os.Directory.Delete(self.recording_temp)
        self.info_shell(f"Record saved : {self.recording_path}")
        self.recording_temp = None


    def open_url(self, url):
        webbrowser.open(url)

    def on_key_down(self, sender, e):
        if e.KeyCode == Keys.F12:
            self.main.show_app_console()

    def on_shell_key_down(self, sender, e):
        self.event = e
        if e.KeyCode == Keys.F12:
            self.main.show_app_console()

        if e.KeyCode == Keys.Up:
            if self.shell_cmds:
                if self.shell_history_index is None:
                    self.shell_history_index = len(self.shell_cmds) - 1
                elif self.shell_history_index > 0:
                    self.shell_history_index -= 1
                self.console_input._impl.native.Text = self.shell_cmds[self.shell_history_index]
                asyncio.ensure_future(self.selection_to_end())

        elif e.KeyCode == Keys.Down:
            if self.shell_cmds and self.shell_history_index is not None:
                if self.shell_history_index < len(self.shell_cmds) - 1:
                    self.shell_history_index += 1
                    self.console_input._impl.native.Text = self.shell_cmds[self.shell_history_index]
                    asyncio.ensure_future(self.selection_to_end())
                else:
                    self.shell_history_index = None
                    self.console_input._impl.native.Text = ""


    async def selection_to_end(self):
        await asyncio.sleep(0.0)
        self.console_input._impl.native.SelectionStart = self.console_input._impl.native.TextLength

    
    def on_mouse_up(self, sender, e):
        if e.Button == Forms.MouseButtons.Right:
            value = self.clipboard.paste()
            self.console_input._impl.native.Text = value
            self.console_input._impl.native.SelectionStart = self.console_input._impl.native.TextLength


    def detach_button_mouse_enter(self, sender, event):
        self.detach_button.image = "images/detach_a.png"

    def detach_button_mouse_leave(self, sender, event):
        self.detach_button.image = "images/detach_i.png"


    def log_button_mouse_enter(self, sender, event):
        if not self.log_toggle:
            self.log_button.style.background_color = GRAY

    def log_button_mouse_leave(self, sender, event):
        if not self.log_toggle:
            self.log_button.style.background_color = rgb(30,30,30)

    def shell_button_mouse_enter(self, sender, event):
        if not self.shell_toggle:
            self.shell_button.style.background_color = GRAY

    def shell_button_mouse_leave(self, sender, event):
        if not self.shell_toggle:
            self.shell_button.style.background_color = rgb(30,30,30)

    def _handle_on_activated(self, sender, event):
        self._is_active = True

    def _handle_on_deactivated(self, sender, event):
        self._is_active = False


    def on_close_console(self, widget):
        self.attach_console()