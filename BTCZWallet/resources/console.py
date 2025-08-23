
from datetime import datetime
import webbrowser

from toga import Window, Box, TextInput, Label, ImageView
from ..framework import (
    FormBorderStyle, RichLabel, DockStyle, Color,
    BorderStyle, Sys, Forms, Keys, ToolTip, MenuStrip,
    ClipBoard
)
from toga.style.pack import Pack
from toga.colors import rgb, GRAY
from toga.constants import COLUMN, CENTER, ROW, YELLOW, BLACK


class Console(Window):
    def __init__(self, main:Window, settings, utils, commands, font):
        super().__init__(
            closable=False
        )

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

        self.log_toggle = None
        self.shell_toggle = None
        self.detach_toggle = None

        self.shell_cmds = []
        self.shell_history_index = None

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
        self.console_input._impl.native.KeyDown += Forms.KeyEventHandler(self.on_key_down)
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
                self._impl.native.Top = self.main._impl.native.Bottom + 5
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
        self._impl.native.Top = self.main._impl.native.Bottom + 10
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
            side = self.detect_touch(self.main._impl.native, self._impl.native, tolerance=0)
            if side:
                self.attach_console()

    def detect_touch(self, main, console, tolerance: int = 0):
        m = main.Bounds
        o = console.Bounds
        overlap_x = (o.Right > m.Left) and (o.Left < m.Right)
        if abs(o.Top - m.Bottom) <= tolerance and overlap_x:
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


    def log(self, text, color):
        self.console_output_logs.SelectionStart = self.console_output_logs.TextLength
        self.console_output_logs.SelectionLength = 0
        self.console_output_logs.SelectionColor = color
        self.console_output_logs.AppendText(text + "\n")
        self.console_output_logs.SelectionColor = Color.WHITE
        self.console_output_logs.ScrollToCaret()

    def shell(self, text, color, bottom:bool = True):
        self.console_output_shell.SelectionStart = self.console_output_shell.TextLength
        self.console_output_shell.SelectionLength = 0
        self.console_output_shell.SelectionColor = color
        self.console_output_shell.AppendText(text + "\n")
        self.console_output_shell.SelectionColor = Color.WHITE
        if bottom:
            self.console_output_shell.ScrollToCaret()


    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def info_log(self, text):
        self.log(f"{self.timestamp()} - {text}", Color.WHITE)

    def command_shell(self, text):
        self.shell_cmds.append(text)
        self.shell_history_index = None
        self.shell(f"{self.timestamp()} - {text}", Color.GREENYELLO)

    def result_shell(self, text):
        self.shell(f"{self.timestamp()} - {text}", Color.rgb(114,137,218), False)
    
    def error_log(self, text):
        self.log(f"{self.timestamp()} - {text}", Color.RED)
    
    def error_shell(self, text):
        self.shell(f"{self.timestamp()} - {text}", Color.RED)

    def warning_log(self, text):
        self.log(f"{self.timestamp()} - {text}", Color.YELLOW)

    def server_log(self, text):
        self.log(f"{self.timestamp()} - {text}", Color.GREEN)


    async def verify_command(self, input):
        if not self.console_input.value:
            return
        value = self.console_input.value.strip()
        self.command_shell(value)
        self.console_input.value = ""

        if value in ["c", "clear"]:
            self.console_output_shell.Text = ""

        elif value in ["h", "help"]:
            self.result_shell(
                "📜 Usage :\n"
                "================================================\n"
                " → h or help :   Show this help message with available commands\n"
                " → c or clear :   Clear the console output window\n"
                " → data :   Open the BitcoinZ blockchain data directory\n"
                " → appdata :   Open the general application data directory\n"
                " → appconfig :   Open the application configuration directory\n"
                " → appcache :   Open the application cache directory\n"
                "================================================\n"
                " 👉 Slash commands (RPC calls):\n\n"
                "     Any input that starts with '/' will be\n"
                "     treated as a direct RPC command sent to\n"
                "     the BitcoinZ node.\n\n"
                " 👉 Examples:\n"
                " → /getinfo :   show blockchain info\n"
                " → /getblockcount :   get current block height\n"
                " → /getblockhash 100 :   get hash of block 100\n"
                " → /getwalletinfo :   display wallet information\n"
                "================================================"
            )

        elif value in ["appdata", "appconfig", "appcache", "data"]:
            self.result_shell(f"open directory...")
            self.exlporer_dir(value)

        elif value.startswith("/"):
            command_line = value[1:]
            command = f'{self.commands.bitcoinz_cli_file} {command_line}'
            result, error_message = await self.commands._run_command(command)
            if error_message:
                self.error_shell(error_message)
            else:
                self.result_shell(result)


    def exlporer_dir(self, value):
        if value == "appdata":
            dir = str(self.app.paths.data)
        elif value == "appconfig":
            dir = str(self.app.paths.config)
        elif value == "appcache":
            dir = str(self.app.paths.cache)
        elif value == "data":
            dir = self.utils.get_bitcoinz_path()

        psi = Sys.Diagnostics.ProcessStartInfo()
        psi.FileName = "explorer.exe"
        psi.Arguments = dir
        psi.UseShellExecute = True
        Sys.Diagnostics.Process.Start(psi)

    
    def open_url(self, url):
        webbrowser.open(url)

    def on_key_down(self, sender, e):
        if e.KeyCode == Keys.F12:
            self.main.show_app_console()

        elif e.KeyCode == Keys.Up:
            if self.shell_cmds:
                if self.shell_history_index is None:
                    self.shell_history_index = len(self.shell_cmds) - 1
                elif self.shell_history_index > 0:
                    self.shell_history_index -= 1
                self.console_input._impl.native.Text = self.shell_cmds[self.shell_history_index]

        elif e.KeyCode == Keys.Down:
            if self.shell_cmds and self.shell_history_index is not None:
                if self.shell_history_index < len(self.shell_cmds) - 1:
                    self.shell_history_index += 1
                    self.console_input._impl.native.Text = self.shell_cmds[self.shell_history_index]
                else:
                    self.shell_history_index = None
                    self.console_input._impl.native.Text = ""

    
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