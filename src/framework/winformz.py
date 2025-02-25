
"""
WinformZ

This script extends the Toga library by integrating .NET Windows Forms UI components through the use of 
the CLR (Common Language Runtime) to interact with the Windows Forms API. The code provides abstractions 
for various UI elements and controls like fonts, colors, toolbars, status bars, and clipboard handling, etc... 
allowing for more complex and customized UI applications.

Key Features:
-------------
1. **Font and Style Management**:
    - Predefined font families: Serif, Monospace, and SansSerif.
    - Font styles such as Regular, Bold, and Italic.
    - Customizable font properties, allowing for flexible text styling across UI elements.

2. **Color Management**:
    - Predefined common colors (e.g., White, Black, Red, Green, etc.) and support for RGB color creation through `Color.rgb(r, g, b)`.
    - Full control over foreground and background colors of UI elements.
    - Easy integration of color management into toolbars, buttons, and other controls for a consistent design.

3. **UI Alignment and Layout**:
    - Common alignment options for UI components like labels and tables (e.g., Left, Center, Right).
    - DataGridView cell alignment customization for optimal table presentation.
    - Docking styles (Top, Bottom, Left, Right, Fill) to easily manage the layout of components within the window.

4. **Clipboard and ToolTip Integration**:
    - Streamlined clipboard handling with the ability to copy text to the system clipboard.
    - Tooltips for UI components (e.g., buttons, labels) to provide additional context or instructions when the user hovers over them.

5. **Toolbar and StatusBar**:
    - Customizable `Toolbar` class for creating menus with commands, colors, icons, and backgrounds.
    - `StatusBar` class to display status information at the bottom of the window with the ability to add items and customize the appearance.

6. **Keyboard Handling**:
    - Easy access to common key codes (e.g., Backspace, Enter, F1-F12) for handling keyboard input and assigning shortcut keys to commands.

7. **Asynchronous Operations**:
    - `run_async(action)` utility to execute tasks asynchronously in the background, making it easier to handle long-running operations without freezing the UI.

8. **DataGridView Customization**:
    - Extended `DataGridView` functionality with options for custom columns, row management, cell alignment, and more.
    - Specialized `ImageColumn` class for displaying images within the grid.
    - Configurable selection modes and clipboard handling within tables.

9. **System Tray and Context Menus**:
    - `NotifyIcon` class to display a system tray icon with custom text and icon.
    - Built-in support for context menus on system tray icons, allowing for easy addition, removal, and management of commands.

10. **Command Management**:
    - Custom `Command` class to create commands for toolbars, context menus, or other UI components.
    - Each command can be associated with an action, icon, color, and even keyboard shortcut keys.
    - Full event handling support for mouse interactions (e.g., mouse enter, leave, up, down), checked states, and dropdown menu interactions.

Classes and Components:
------------------------
1. **Font**: Defines predefined font families.
2. **FontStyle**: Defines commonly used font styles (Regular, Bold, Italic).
3. **AlignLabel**: Defines common alignment options for labels.
4. **AlignTable**: Defines alignment for DataGridView cells.
5. **DockStyle**: Defines docking styles for UI controls.
6. **ProgressStyle**: Defines progress bar styles.
7. **Color**: Handles predefined colors and custom RGB creation.
8. **SelectMode**: Defines selection modes for DataGridView controls.
9. **CopyMode**: Defines clipboard copy modes for DataGridView controls.
10. **BorderStyle**: Defines border styles for UI elements.
11. **ClipBoard**: Extends .NET's Clipboard class to provide text copying functionality.
12. **ToolTip**: Extends .NET's ToolTip class to associate tooltips with UI components.
13. **Keys**: Provides key codes for common keyboard inputs.
14. **Separator**: A custom class for creating separators in toolbars and menus.
15. **Toolbar**: A custom toolbar that can contain commands, set colors, and manage layout.
16. **StatusBar**: A custom status bar that displays information at the bottom of the window.
17. **Table**: A custom DataGridView implementation that allows customization of columns, rows, selection, and other table properties.
18. **Command**: A custom class for creating commands in toolbars or menus, with customizable actions, appearance, and events.
19. **NotifyIcon**: A custom class for creating system tray icons with context menus and commands.
20. **ImageColumn**: A custom class that extends the `DataGridViewImageColumn` to display images in a DataGridView.
21. **RichLabel**: A custom class that extends `RichTextBox` to provide enhanced functionality for displaying rich text content.

Note:
-----
This module is designed specifically for Windows-based applications using the .NET Windows Forms API,
and it leverages the Common Language Runtime (CLR) to facilitate integration with .NET libraries. The requirements for running this script are as follows:

1. A Python environment capable of interfacing with the .NET Framework, typically achieved through the `pythonnet` package or a similar CLR bridge.
2. The .NET Framework (or .NET Core) installed on the system to enable Windows Forms functionality.

This solution is **not cross-platform** and is intended for use only on Windows operating systems.

While it may be possible to run it on other platforms with tools like Mono,
such configurations are not officially supported and may require additional modifications for full compatibility.

"""


import asyncio
import clr
from pathlib import Path
from typing import Optional, Union, List, Callable
import re

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('System.Threading')

import System as Sys
import System.IO as Os
import System.Drawing as Drawing
import System.Windows.Forms as Forms
import System.Threading.Tasks as Tasks


def get_app_path():
    script_path = Os.Path.GetDirectoryName(Os.Path.GetFullPath(__file__))
    app_path = Os.Path.GetDirectoryName(script_path)
    return app_path

def run_async(action):
    task_action = Sys.Action(lambda: asyncio.run(action))
    Tasks.Task.Factory.StartNew(task_action)


class Font:
    SERIF = Drawing.FontFamily.GenericSerif
    MONOSPACE = Drawing.FontFamily.GenericMonospace
    SANSSERIF = Drawing.FontFamily.GenericSansSerif

class FontStyle:
    REGULAR = Drawing.FontStyle.Regular
    BOLD = Drawing.FontStyle.Bold
    ITALIC = Drawing.FontStyle.Italic

class AlignLabel:
    LEFT = Drawing.ContentAlignment.MiddleLeft
    CENTER = Drawing.ContentAlignment.MiddleCenter
    RIGHT = Drawing.ContentAlignment.MiddleRight

class AlignTable:
    MIDCENTER = Forms.DataGridViewContentAlignment.MiddleCenter
    MIDLEFT = Forms.DataGridViewContentAlignment.MiddleLeft

class AlignRichLabel:
    CENTER = Forms.HorizontalAlignment.Center

class DockStyle:
    NONE = Forms.DockStyle(0)
    TOP = Forms.DockStyle.Top
    BOTTOM = Forms.DockStyle.Bottom
    LEFT = Forms.DockStyle.Left
    RIGHT = Forms.DockStyle.Right
    FILL = Forms.DockStyle.Fill

class ProgressStyle:
    BLOCKS = Forms.ProgressBarStyle.Blocks
    MARQUEE = Forms.ProgressBarStyle.Marquee

class Color:
    WHITE = Drawing.Color.White
    BLACK = Drawing.Color.Black
    ORANGE = Drawing.Color.Orange
    RED = Drawing.Color.Red
    GREEN = Drawing.Color.Green
    LIGHT_GRAY = Drawing.Color.LightGray
    DARK_GRAY = Drawing.Color.DarkGray
    YELLOW = Drawing.Color.Yellow
    GRAY = Drawing.Color.Gray

    @staticmethod
    def rgb(r, g, b):
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return Drawing.Color.FromArgb(r, g, b)

class SelectMode:
    CELLSELECT = Forms.DataGridViewSelectionMode.CellSelect
    FULLROWSELECT = Forms.DataGridViewSelectionMode.FullRowSelect

class CopyMode:
    DISABLE = Forms.DataGridViewClipboardCopyMode.Disable


class FormState:
    NORMAL = Forms.FormWindowState.Normal
    MINIMIZED = Forms.FormWindowState.Minimized

class BorderStyle:
    NONE = Forms.BorderStyle(0)


class ComboStyle:
    FLAT = Forms.FlatStyle.Flat

class ClipBoard(Forms.Clipboard):
    def __init__(self):
        super().__init__()
    def copy(self, value):
        self.SetText(value)

class ToolTip(Forms.ToolTip):
    def __init__(self):
        super().__init__()
    def insert(self, widget, value):
        self.SetToolTip(widget, value)


class ScrollBars:
    NONE = Forms.RichTextBoxScrollBars(0)

class RightToLeft:
    NO = Forms.RightToLeft.No
    YES = Forms.RightToLeft.Yes

class Cursors:
    DEFAULT = Forms.Cursors.Default
    WAIT = Forms.Cursors.WaitCursor
    
    
class Keys:
    NoneKey = Forms.Keys(0)
    Backspace = Forms.Keys.Back
    Tab = Forms.Keys.Tab
    Enter = Forms.Keys.Enter
    Shift = Forms.Keys.Shift
    Control = Forms.Keys.Control
    Alt = Forms.Keys.Alt
    Pause = Forms.Keys.Pause
    CapsLock = Forms.Keys.CapsLock
    Escape = Forms.Keys.Escape
    Space = Forms.Keys.Space
    PageUp = Forms.Keys.PageUp
    PageDown = Forms.Keys.PageDown
    End = Forms.Keys.End

    F1 = Forms.Keys.F1
    F4 = Forms.Keys.F4
    A = Forms.Keys.A


class Separator(Forms.ToolStripSeparator):
    def __init__(self):
        super().__init__()


class MenuStrip(Forms.ContextMenuStrip):
    def __init__(self):
        super().__init__()


class Toolbar(Forms.MenuStrip):
    def __init__(
        self,
        color: Optional[Color] = None,
        background_color: Optional[Color] = None,
    ):
        super().__init__()

        self.commands = []
        
        self._color = color
        self._background_color = background_color

        if self._color:
            self.ForeColor = self._color

        if self._background_color:
            self.BackColor = self._background_color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value: Color):
        self._color = value
        self.ForeColor = value

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, value: Color):
        self._background_color = value
        self.BackColor = value

    def add_command(self, commands: list):
        if not isinstance(commands, list):
            raise ValueError("The 'commands' parameter must be a list of Command objects.")
        
        for command in commands:
            self.commands.append(command)
            self.Items.Add(command)


class StatusBar(Forms.StatusStrip):
    def __init__(
        self,
        color: Optional[Color] = None,
        background_color: Optional[Color] = None,
        dockstyle: Optional[DockStyle] = None
    ):
        super().__init__()

        self.items = []
        self._color = color
        self._background_color = background_color
        self._dockstyle = dockstyle

        if self._color:
            self.ForeColor = self._color

        if self._background_color:
            self.BackColor = self._background_color

        if self._dockstyle:
            self.Dock = self._dockstyle
        self.ShowItemToolTips = True

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value: Color):
        self._color = value
        self.ForeColor = value

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, value: Color):
        self._background_color = value
        self.BackColor = value

    @property
    def dockstyle(self):
        return self._dockstyle

    @dockstyle.setter
    def dockstyle(self, value: DockStyle):
        self._dockstyle = value
        self.Dock = value

    def add_items(self, items: list):
        if not isinstance(items, list):
            raise ValueError("The 'items' parameter must be a list of Command objects.")

        for item in items:
            self.items.append(item)
            self.Items.Add(item)


class StatusLabel(Forms.ToolStripStatusLabel):
    def __init__(
        self,
        text : str = "",
        image: Path = None,
        font: Optional[Font] = None,
        style: Optional[FontStyle] = None,
        font_size: Optional[int] = 9,
        color : Optional[Color] = None,
        background_color :Optional[Color] = None,
        text_align:Optional[AlignLabel] = None,
        image_align:Optional[AlignLabel] =None,
        spring : bool = None,
        size:tuple[int, int] = None,
        autotooltip:bool = False
    ):
        super().__init__()

        self._text = text
        self._image_path = image
        self._font = font
        self._style = style
        self._font_size = font_size
        self._color = color
        self._background_color = background_color
        self._text_align = text_align
        self._image_align = image_align
        self._spring = spring
        self._size = size
        self._autotooltip = autotooltip

        self.app_path  = get_app_path()
        if self._text:
            self.Text = self._text
        if self._image_path:
            self._set_image(self._image_path)
        if self._font:
            self._font_object = Drawing.Font(self._font, self._font_size, self._style)
            self.Font = self._font_object
        if self._color:
            self.ForeColor = self._color
        if self._background_color:
            self.BackColor = self._background_color
        if self._text_align:
            self.TextAlign = self._text_align
        if self._image_align:
            self.ImageAlign = self._image_align
        if self._spring:
            self.Spring = self._spring
        if self._size:
            self.Size = Drawing.Size(*self._size)
        if self._autotooltip:
            self.AutoToolTip = self._autotooltip

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        self.Text = value

    @property
    def image(self) -> Path:
        return self._image_path
    
    @image.setter
    def image(self, value):
        self._image_path = value
        if value:
            self._set_image(value)
        else:
            self.Image = None

    def _set_image(self, image_path: Path):
        try:
            full_path = str(Os.Path.Combine(self.app_path , image_path))
            image = Drawing.Bitmap(full_path)
            self.Image = image
        except Exception as e:
            print(f"Error loading image: {e}")
            self.Image = None


class Command(Forms.ToolStripMenuItem):
    def __init__(
        self,
        title: str = "",
        action=None,
        sub_commands=None,
        icon: Path = None,
        color: Optional[Color] = None,
        background_color :Optional[Color] = None,
        mouse_enter: Optional[Callable] = None,
        mouse_leave: Optional[Callable] = None,
        mouse_up: Optional[Callable] = None,
        mouse_down : Optional[Callable] = None,
        checked: Optional[bool] = False,
        checked_changed: Optional[Callable[[], None]] = None,
        drop_opened: Optional[Callable[[], None]] = None,
        drop_closed: Optional[Callable[[], None]] = None,
        shortcut_key: Optional[Keys] = None
    ):
        super().__init__(title)

        self._title = title
        self._action = action
        self._sub_commands = sub_commands
        self._icon = icon
        self._color = color
        self._background_color = background_color
        self._mouse_enter = mouse_enter
        self._mouse_leave = mouse_leave
        self._mouse_up = mouse_up
        self._mouse_down = mouse_down
        self._checked = checked
        self._checked_changed = checked_changed
        self._drop_opened = drop_opened
        self._drop_closed = drop_closed
        self._shortcut_key = shortcut_key

        self.app_path = get_app_path()

        if self._icon:
            self._set_icon(self._icon)
        if self._action:
            self.Click += self._handle_click
        if self._sub_commands:
            for sub_command in self._sub_commands:
                self.DropDownItems.Add(sub_command)
        if self._color:
            self.ForeColor = self._color
        if self._background_color:
            self.BackColor = self._background_color
        if self._mouse_enter:
            self.MouseEnter += self._handle_mouse_enter
        if self._mouse_leave:
            self.MouseLeave += self._handle_mouse_leave
        if self._mouse_up:
            self.MouseUp += self._handle_mouse_up
        if self._mouse_down:
            self.MouseDown += self._handle_mouse_down
        if self._checked_changed:
            self.CheckedChanged += self._handle_checked_changed
        if self._drop_opened:
            self.DropDownOpened += self._handle_drop_opened
        if self._drop_closed:
            self.DropDownClosed += self._handle_drop_closed
        if self._shortcut_key:
            self.ShortcutKeys = self._shortcut_key
        self.Checked = self._checked


    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value
        self.Text = value

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value
        if value:
            self.Click += value

    @property
    def sub_commands(self):
        return self._sub_commands

    @sub_commands.setter
    def sub_commands(self, value):
        self._sub_commands = value
        self.DropDownItems.Clear()
        if self._sub_commands:
            for sub_command in self._sub_commands:
                self.DropDownItems.Add(sub_command)

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value: Path):
        self._icon = value
        self._set_icon(value)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value: Optional[Color]):
        self._color = value
        self.ForeColor = value

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, value: Optional[Color]):
        self._background_color = value
        self.BackColor = value

    @property
    def mouse_enter(self) -> Optional[Callable[[], None]]:
        return self._mouse_enter
    
    @mouse_enter.setter
    def mouse_enter(self, value: Optional[Callable[[], None]]):
        if self._mouse_enter:
            self.MouseEnter -= self._handle_mouse_enter
        self._mouse_enter = value
        if self._mouse_enter:
            self.MouseEnter += self._handle_mouse_enter
    
    @property
    def mouse_leave(self) -> Optional[Callable[[], None]]:
        return self._mouse_leave

    @mouse_leave.setter
    def mouse_leave(self, value: Optional[Callable[[], None]]):
        if self._mouse_leave:
            self.MouseLeave -= self._handle_mouse_leave
        self._mouse_leave = value
        if self._mouse_leave:
            self.MouseLeave += self._handle_mouse_leave

    @property
    def mouse_up(self) -> Optional[Callable[[], None]]:
        return self._mouse_up

    @mouse_up.setter
    def mouse_up(self, value: Optional[Callable[[], None]]):
        if self._mouse_up:
            self.MouseUp -= self._handle_mouse_up
        self._mouse_up = value
        if self._mouse_up:
            self.MouseUp += self._handle_mouse_up

    @property
    def mouse_down(self) -> Optional[Callable[[], None]]:
        return self._mouse_down

    @mouse_down.setter
    def mouse_down(self, value: Optional[Callable[[], None]]):
        if self._mouse_down:
            self.MouseDown -= self._handle_mouse_down
        self._mouse_down = value
        if self._mouse_down:
            self.MouseDown += self._handle_mouse_down

    @property
    def checked(self) -> bool:
        return self._checked

    @checked.setter
    def checked(self, value: bool):
        self._checked = value
        self.Checked = value

    @property
    def checked_changed(self) -> Optional[Callable[[], None]]:
        return self._checked_changed

    @checked_changed.setter
    def checked_changed(self, value: Optional[Callable[[], None]]):
        if self._checked_changed:
            self.CheckedChanged -= self._handle_checked_changed
        self._checked_changed = value
        if self._checked_changed:
            self.CheckedChanged += self._handle_checked_changed

    @property
    def drop_opened(self) -> Optional[Callable[[], None]]:
        return self._drop_opened

    @drop_opened.setter
    def drop_opened(self, value: Optional[Callable[[], None]]):
        if self._drop_opened:
            self.DropDownOpened -= self._handle_drop_opened
        self._drop_opened = value
        if self._drop_opened:
            self.DropDownOpened += self._handle_drop_opened

    @property
    def drop_closed(self) -> Optional[Callable[[], None]]:
        return self._drop_closed

    @drop_closed.setter
    def drop_closed(self, value: Optional[Callable[[], None]]):
        if self._drop_closed:
            self.DropDownClosed -= self._handle_drop_closed
        self._drop_closed = value
        if self._drop_closed:
            self.DropDownClosed += self._handle_drop_closed

    @property
    def shortcut_key(self) -> Optional[Forms.Keys]:
        return self._shortcut_key

    @shortcut_key.setter
    def shortcut_key(self, value: Optional[Forms.Keys]):
        self._shortcut_key = value
        if value:
            self.ShortcutKeys = value
        else:
            self.ShortcutKeys = Forms.Keys(0)

    def _handle_click(self, sender, event):
        if self._action:
            self._action()


    def _set_icon(self, icon_path: Path):
        try:
            full_path = Os.Path.Combine(self.app_path, icon_path)
            image = Drawing.Bitmap(str(full_path))
            self.Image = image
        except Exception as e:
            print(f"Error loading image: {e}")
            self.Image = None

    def _handle_mouse_enter(self, sender, event):
        if self._mouse_enter:
            self._mouse_enter()

    def _handle_mouse_leave(self, sender, event):
        if self._mouse_leave:
            self._mouse_leave()

    def _handle_mouse_up(self, sender, event):
        if self._mouse_up:
            self._mouse_up()

    def _handle_mouse_down(self, sender, event):
        if self._mouse_down:
            self._mouse_down()

    def _handle_checked_changed(self, sender, event):
        if self._checked_changed:
            self._checked_changed()

    def _handle_drop_opened(self, sender, event):
        if self._drop_opened:
            self._drop_opened()

    def _handle_drop_closed(self, sender, event):
        if self._drop_closed:
            self._drop_closed()



class NotifyIcon(Forms.NotifyIcon):
    def __init__(
        self,
        text: Optional[str] = None,
        icon: Path = None,
        commands: Optional[List[type]] = None
    ):
        super().__init__()
        self._text = text
        self._icon = icon
        self._commands = commands

        self.app_path = get_app_path()

        if self._icon:
            full_path = str(Os.Path.Combine(self.app_path , self._icon))
            self.Icon = Drawing.Icon(str(full_path))

        if self._text:
            self.Text = self._text

        if self._commands:
            self.context_menu = Forms.ContextMenuStrip()
            for command in self._commands:
                self.context_menu.Items.Add(command)
            self.ContextMenuStrip = self.context_menu

    @property
    def text(self) -> Optional[str]:
        return self._text
    
    @text.setter
    def text(self, value: Optional[str]):
        self._text = value
        if self._text is not None:
            self.Text = self._text
        else:
            self.Text = ""

    def insert_command(self, command: type, index: Optional[int] = None):
        if not self.context_menu:
            self.context_menu = Forms.ContextMenuStrip()
            self.ContextMenuStrip = self.context_menu
        
        if index is None:
            self.context_menu.Items.Add(command)
        else:
            self.context_menu.Items.Insert(index, command)

    def remove_command(self, command: type):
        if self.context_menu:
            for item in self.context_menu.Items:
                if item.GetType() == command:
                    self.context_menu.Items.Remove(item)
                    break

    def send_note(self, title: str, text: str, timeout: int = 5, on_click:Callable = None):
        if on_click:
            self.BalloonTipClicked += on_click
        self.BalloonTipTitle = title
        self.BalloonTipText = text
        self.ShowBalloonTip(timeout)

    def show(self):
        self.Visible = True

    def hide(self):
        if self.Visible:
            self.Visible = False
            self.Dispose()



class ImageColumn(Forms.DataGridViewImageColumn):
    def __init__(
        self,
        image: Path = None
    ):
        super().__init__()
        self._image = image

        self.app_path = get_app_path()

        if self._image:
            self._set_image(self._image)

    def _set_image(self, image_path: Path):
        try:
            full_path = str(Os.Path.Combine(self.app_path , image_path))
            if Os.Path.Exists(full_path):
                image = Drawing.Bitmap(full_path)
                self.Image = image
        except Exception as e:
            print(f"Error loading image: {e}")
            self.Image = None



class Table(Forms.DataGridView):
    def __init__(
        self,
        size: tuple[int, int] = None,
        text_size: Optional[int] = 9,
        text_style: Optional[FontStyle] = FontStyle.REGULAR,
        location: tuple[int, int] = None,
        text_color: Optional[Color] = None,
        background_color: Optional[Color] = None,
        cell_color: Optional[Color] = None,
        font: Optional[Font] = Font.SERIF,
        align: Optional[AlignLabel] = None,
        data_source: Optional[Union[List[dict], List[List]]] = None,
        dockstyle: Optional[DockStyle] = None,
        column_count: Optional[int] = None,
        gird_color: Optional[Color] = None,
        column_visible: bool = True,
        row_visible: bool = True,
        column_widths: Optional[dict] = None,
        row_heights: Optional[int] = None,
        multiselect: bool = False,
        select_mode: Optional[SelectMode] = None,
        selection_backcolors: Optional[dict[int, Color]] = None,
        selection_colors: Optional[dict[int, Color]] = None,
        borderstyle : Optional[BorderStyle] = None,
        readonly: bool = False,
        column_types: Optional[dict[int, type]] = None,
        commands: Optional[List[type]] = None,
        on_select: Optional[Callable[[Forms.DataGridViewRow], None]] = None,
        on_scroll: Optional[Callable[[Forms.ScrollEventArgs], None]] = None,
        on_double_click: Optional[Callable[[Forms.DataGridViewCellEventArgs], None]] = None
    ):
        super().__init__()
        
        self._size = size
        self._text_size = text_size
        self._text_style = text_style
        self._location = location
        self._text_color = text_color
        self._background_color = background_color
        self._cell_color = cell_color
        self._font = font
        self._align = align
        self._data_source = data_source
        self._dockstyle = dockstyle
        self._column_count = column_count
        self._gird_color = gird_color
        self._column_visible = column_visible
        self._row_visible = row_visible
        self._column_widths = column_widths or {}
        self._row_heights = row_heights
        self._multiselect = multiselect
        self._select_mode = select_mode
        self._selection_backcolors = selection_backcolors or {}
        self._selection_colors = selection_colors or {}
        self._borderstyle = borderstyle
        self._readonly = readonly
        self._column_types = column_types or {}
        self._commands = commands
        self._on_select = on_select
        self._on_double_click = on_double_click

        self._font_object = Drawing.Font(self._font, self._text_size, self._text_style)

        if self._size:
            self.Size = Drawing.Size(*self._size)
        if self._location:
            self.Location = Drawing.Point(*self._location)
        if self._text_color:
            self.ForeColor = self._text_color
        if self._background_color:
            self.BackgroundColor = self._background_color
        if self._cell_color:
            self.DefaultCellStyle.BackColor = self._cell_color
        if self._dockstyle:
            self.Dock = self._dockstyle
        self.DefaultCellStyle.Font = self._font_object
        self.Font = self._font_object
        if self._align:
            self.DefaultCellStyle.Alignment = self._align
        if self._column_count:
            self.ColumnCount = self._column_count
        if self._gird_color:
            self.GridColor = self._gird_color
        self.RowHeadersVisible = self._row_visible
        self.ColumnHeadersVisible = self._column_visible
        if self._row_heights:
            self.RowTemplate.Height = self._row_heights
        self.MultiSelect = self._multiselect
        if self._select_mode:
            self.SelectionMode = self._select_mode
        if self._borderstyle:
            self.BorderStyle = self._borderstyle
        self.ReadOnly = self._readonly
        self.ColumnHeadersDefaultCellStyle.Alignment = AlignTable.MIDCENTER
        if self._commands:
            self.context_menu = Forms.ContextMenuStrip()
            for command in self._commands:
                self.context_menu.Items.Add(command)
            self.ContextMenuStrip = self.context_menu
        if self._on_select:
            self.SelectionChanged += self._on_selection_changed
        self._on_scroll = on_scroll
        if self._on_scroll:
            self.Scroll += self._on_scroll_handler
        if self._on_double_click:
            self.CellDoubleClick += self._on_cell_double_click

        self.AllowUserToAddRows = False
        self.AllowUserToDeleteRows = False
        self.AllowUserToResizeRows = False
        self.AllowUserToResizeColumns = True
        self.ClipboardCopyMode = CopyMode.DISABLE
        
        if self._data_source:
            self.set_data_source(self._data_source)
        self.Resize += self._on_resize
        self.CellFormatting += self._on_cell_formatting

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @size.setter
    def size(self, value: tuple[int, int]):
        self._size = value
        self.Invoke(Forms.MethodInvoker(lambda:self.update_size(value)))
    
    def update_size(self, value):
        self.Size = Drawing.Size(*value)

    @property
    def location(self) -> tuple[int, int]:
        return self._location

    @location.setter
    def location(self, value: tuple[int, int]):
        self._location = value
        self.Invoke(Forms.MethodInvoker(lambda:self.update_location(value)))

    def update_location(self, value):
        self.Location = Drawing.Point(*value)

    @property
    def background_color(self) -> Optional[Drawing.Color]:
        return self._background_color

    @background_color.setter
    def background_color(self, value: Optional[Drawing.Color]):
        self._background_color = value
        self.Invoke(Forms.MethodInvoker(lambda:self.update_background_color(value)))

    def update_background_color(self, value):
        self.BackgroundColor = value

    @property
    def data_source(self) -> Optional[Union[List[dict], List[List]]]:
        return self._data_source

    @data_source.setter
    def data_source(self, value: Optional[Union[List[dict], List[List]]]):
        self._data_source = value
        self.Invoke(Forms.MethodInvoker(lambda:self.set_data_source(value)))

    @property
    def columns(self) -> list[str]:
        return [column.Name for column in self.Columns]
    
    @property
    def rows(self) -> list[Forms.DataGridViewRow]:
        return [row for row in self.Rows]

    @property
    def selected_cells(self) -> Optional[Forms.DataGridViewCell]:
        return [cell for cell in self.SelectedCells]
    
    @property
    def column_widths(self) -> dict:
        return self._column_widths

    @column_widths.setter
    def column_widths(self, widths: dict):
        self._column_widths = widths
        self.Invoke(Forms.MethodInvoker(lambda:self.update_column_widths()))

    def update_column_widths(self):
        if self._column_widths:
            for index, width in self._column_widths.items():
                if 0 <= index < self.ColumnCount:
                    self.Columns[index].Width = width

    @property
    def column_types(self) -> dict:
        return self._column_types

    @column_types.setter
    def column_types(self, types: dict):
        self._column_types = types
        self.Invoke(Forms.MethodInvoker(lambda: self.update_column_types()))

    def update_column_types(self):
        for index, column_type in self._column_types.items():
            if 0 <= index < self.ColumnCount:
                self.Columns[index].ColumnType = column_type

    def set_data_source(self, data: Optional[Union[List[dict], List[List]]]):
        if isinstance(data, list):
            if data:
                if data and isinstance(data[0], list):
                    self.Rows.Clear()
                    for row in data:
                        self.Rows.Add(row)
                elif data and isinstance(data[0], dict):
                    self.Columns.Clear()
                    for key in data[0].keys():
                        self.Columns.Add(key, key)
                    self.Rows.Clear()
                    for row in data:
                        self.Rows.Add(*[row[key] for key in row.keys()])
                self.update_column_widths()
            else:
                self.Rows.Clear()
                self.Columns.Clear()
        else:
            raise ValueError("Data source must be a list of dictionaries or list of lists.")
        self.Invoke(Forms.MethodInvoker(lambda:self._resize_columns()))

    
    def add_column(self, name: str, header: str):
        self.Columns.Add(name, header)

    def _get_column_index_by_name(self, column_name: str) -> int:
        for index, column in enumerate(self.Columns):
            if column.Name == column_name:
                return index
        return None

    def add_row(self, index: int, row_data: Union[List, dict]):
        if isinstance(row_data, dict):
            if all(isinstance(key, str) for key in row_data.keys()):
                if not self.Columns:
                    raise ValueError("Cannot add a row because the table has no columns.")
                row = [None] * self.ColumnCount
                for key, value in row_data.items():
                    col_index = self._get_column_index_by_name(key)
                    if col_index is not None:
                        row[col_index] = value
                    else:
                        raise ValueError(f"Column '{key}' not found.")
            else:
                row = [None] * self.ColumnCount
                for col_index, value in row_data.items():
                    if 0 <= col_index < self.ColumnCount:
                        row[col_index] = value
                    else:
                        raise IndexError(f"Column index {col_index} is out of range.")
        elif isinstance(row_data, list):
            if len(row_data) != self.ColumnCount:
                raise ValueError("Row data length does not match the number of columns.")
            row = row_data
        else:
            raise ValueError("Row data must be a list or a dictionary.")
        if 0 <= index <= self.Rows.Count:
            self.Rows.Insert(index, row)
        else:
            raise IndexError("Index is out of bounds.")

    def _on_resize(self, sender, event):
        self.Invoke(Forms.MethodInvoker(lambda:self._resize_columns()))

    def _resize_columns(self):
        total_width = self.ClientSize.Width
        total_columns = self.ColumnCount
        if total_columns == 0 or total_width == 0:
            return
        total_current_column_width = sum([col.Width for col in self.Columns])
        for i, column in enumerate(self.Columns):
            if total_current_column_width > 0:
                proportion = column.Width / total_current_column_width
                new_width = total_width * proportion
                column.Width = int(new_width)
            else:
                column.Width = self._column_widths.get(i, 100)

    @property
    def selection_colors(self) -> dict:
        return self._selection_colors

    @selection_colors.setter
    def selection_colors(self, forecolors: dict):
        self._selection_colors = forecolors
        self.Invoke(Forms.MethodInvoker(lambda: self._apply_selection_colors()))

    def _apply_selection_colors(self):
        for index, forecolor in self._selection_colors.items():
            if 0 <= index < self.ColumnCount:
                self.Columns[index].DefaultCellStyle.SelectionForeColor = forecolor

    @property
    def selection_backcolors(self) -> dict:
        return self._selection_backcolors

    @selection_backcolors.setter
    def selection_backcolors(self, backcolors: dict):
        self._selection_backcolors = backcolors
        self.Invoke(Forms.MethodInvoker(lambda: self._apply_selection_backcolors()))

    def _apply_selection_backcolors(self):
        for index, backcolor in self._selection_backcolors.items():
            if 0 <= index < self.ColumnCount:
                self.Columns[index].DefaultCellStyle.SelectionBackColor = backcolor

    def _on_cell_formatting(self, sender, e):
        if e.RowIndex >= 0:
            column_index = e.ColumnIndex
            if column_index in self._selection_backcolors:
                self.Invoke(Forms.MethodInvoker(lambda:self.update_selection_backcolors(e ,column_index)))
            if column_index in self._selection_colors:
                self.Invoke(Forms.MethodInvoker(lambda:self.update_selection_forecolors(e ,column_index)))

    def update_selection_backcolors(self, e, index):
        e.CellStyle.SelectionBackColor = self._selection_backcolors[index]

    def update_selection_forecolors(self, e, index):
        e.CellStyle.SelectionForeColor = self._selection_colors[index]

    def _on_selection_changed(self, sender, e):
        if self._on_select:
            selected_rows = self.selected_cells
            self._on_select(selected_rows)

    def _on_scroll_handler(self, sender, event: Forms.ScrollEventArgs):
        if self._on_scroll:
            self._on_scroll(event)

    def _on_cell_double_click(self, sender, e: Forms.DataGridViewCellEventArgs):
        if self._on_double_click:
            self._on_double_click(sender, e)



class RichLabel(Forms.RichTextBox):
    def __init__(
        self,
        text: str = None,
        font: Optional[Font] = Font.SANSSERIF,
        style: Optional[FontStyle] = FontStyle.REGULAR,
        text_size: int = 11,
        readonly: bool = False,
        color: Optional[Color] = None,
        background_color: Optional[Color]= None,
        dockstyle: Optional[DockStyle] = None,
        borderstyle: Optional[BorderStyle] = None,
        urls: bool = False,
        wrap: bool = False,
        scrollbars: Optional[ScrollBars] = None,
        text_align: Optional[AlignRichLabel] = None,
        righttoleft: Optional[RightToLeft] = RightToLeft.NO,
        maxsize: tuple[int, int] = None,
        minsize: tuple[int, int] = None,
        urls_click: Optional[Callable] = None,
        mouse_wheel: Optional[Callable] = None
    ):
        super().__init__()

        self._text = text
        self._font = font
        self._style = style
        self._text_size = text_size
        self._readonly = readonly
        self._color = color
        self._background_color = background_color
        self._dockstyle = dockstyle
        self._borderstyle = borderstyle
        self._urls = urls
        self._wrap = wrap
        self._scrollbars = scrollbars
        self._text_align = text_align
        self._righttoleft = righttoleft
        self._maxsize = maxsize
        self._minsize = minsize
        self._urls_click = urls_click
        self._mouse_wheel = mouse_wheel

        self.tooltip = Forms.ToolTip()
        self.tooltip_visible = None

        if self._text:
            self.Text = self._text
        self._font_object = Drawing.Font(self._font, self._text_size, self._style)
        self.Font = self._font_object
        if self._color:
            self.ForeColor = self._color
        if self._background_color:
            self.BackColor = self._background_color
        if self._readonly:
            self.ReadOnly = self._readonly
        if self._dockstyle:
            self.Dock = self._dockstyle
        if self._borderstyle:
            self.BorderStyle = self._borderstyle
        if self._urls:
            self.DetectUrls = self._urls
        if self._wrap:
            self.WordWrap = self._wrap
        if self._scrollbars:
            self.ScrollBars = self._scrollbars
        if self._text_align:
            self.SelectionAlignment = self._text_align
        self.RightToLeft = self._righttoleft
        if self._maxsize:
            self.MaximumSize = Drawing.Size(*self._maxsize)
        if self._minsize:
            self.MinimumSize = Drawing.Size(*self._minsize)
        if self._urls_click:
            self.LinkClicked += self.on_link_clicked
            self.MouseMove += self.on_mouse_move
        if self._mouse_wheel:
            self.MouseWheel += self.on_mouse_wheel

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        self.Text = value

    @property
    def font(self) -> Optional[Font]:
        return self._font

    @font.setter
    def font(self, value: Optional[Font]):
        self._font = value
        self.Font = value

    @property
    def style(self) -> Optional[FontStyle]:
        return self._style

    @style.setter
    def style(self, value: Optional[FontStyle]):
        self._style = value
        self.Font = Drawing.Font(self._font, self._style, self._text_size)

    @property
    def text_size(self) -> int:
        return self._text_size

    @text_size.setter
    def text_size(self, value: int):
        self._text_size = value
        self.Font = Drawing.Font(self._font, self._style, self._text_size)

    @property
    def readonly(self) -> bool:
        return self._readonly

    @readonly.setter
    def readonly(self, value: bool):
        self._readonly = value
        self.ReadOnly = value

    @property
    def color(self) -> Optional[Color]:
        return self._color

    @color.setter
    def color(self, value: Optional[Color]):
        self._color = value
        self.ForeColor = value

    @property
    def background_color(self) -> Optional[Color]:
        return self._background_color

    @background_color.setter
    def background_color(self, value: Optional[Color]):
        self._background_color = value
        self.BackColor = value

    @property
    def dockstyle(self) -> Optional[DockStyle]:
        return self._dockstyle

    @dockstyle.setter
    def dockstyle(self, value: Optional[DockStyle]):
        self._dockstyle = value
        self.Dock = value

    @property
    def borderstyle(self) -> Optional[BorderStyle]:
        return self._borderstyle

    @borderstyle.setter
    def borderstyle(self, value: Optional[BorderStyle]):
        self._borderstyle = value
        self.BorderStyle = value

    @property
    def urls(self) -> bool:
        return self._urls

    @urls.setter
    def urls(self, value: bool):
        self._urls = value
        self.DetectUrls = value

    @property
    def wrap(self) -> bool:
        return self._wrap

    @wrap.setter
    def wrap(self, value: bool):
        self._wrap = value
        self.WordWrap = value

    @property
    def scrollbars(self) -> Optional[ScrollBars]:
        return self._scrollbars

    @scrollbars.setter
    def scrollbars(self, value: Optional[ScrollBars]):
        self._scrollbars = value
        self.ScrollBars = value

    @property
    def text_align(self) -> Optional[AlignRichLabel]:
        return self._text_align

    @text_align.setter
    def text_align(self, value: Optional[AlignRichLabel]):
        self._text_align = value
        self.SelectionAlignment = value

    @property
    def righttoleft(self) -> Optional[RightToLeft]:
        return self._righttoleft

    @righttoleft.setter
    def righttoleft(self, value: Optional[RightToLeft]):
        self._righttoleft = value
        self.RightToLeft = value

    @property
    def maxsize(self) -> tuple[int, int]:
        return self._maxsize

    @maxsize.setter
    def maxsize(self, value: tuple[int, int]):
        self._maxsize = value
        self.MaximumSize = Drawing.Size(*self._maxsize)

    @property
    def minsize(self) -> tuple[int, int]:
        return self._minsize

    @minsize.setter
    def minsize(self, value: tuple[int, int]):
        self._minsize = value
        self.MinimumSize = Drawing.Size(*self._minsize)

    
    def on_link_clicked(self, sender, event):
        if self._urls_click:
            self._urls_click(event.LinkText)

    
    def on_mouse_move(self, sender, event):
        pos = event.Location
        link_pos = self.GetCharIndexFromPosition(pos)
        link_text = self.get_url_at_position(link_pos)
        if link_text and not self.tooltip_visible:
            self.tooltip.Show(link_text, self, pos.X, pos.Y + 20, 2000)
            self.tooltip_visible = True
        elif not link_text and self.tooltip_visible:
            self.tooltip.Hide(self)
            self.tooltip_visible = None
            

    def get_url_at_position(self, position: int) -> str:
        if position == -1:
            return ""
        text = self.Text
        url_pattern = re.compile(r'(https?://[^\s]+)')
        urls = url_pattern.findall(text)
        for url in urls:
            start_pos = text.find(url)
            end_pos = start_pos + len(url)
            if start_pos <= position < end_pos:
                return url
        return ""
    

    def on_mouse_wheel(self, sender, event):
        if self._mouse_wheel:
            self._mouse_wheel(event.Delta)