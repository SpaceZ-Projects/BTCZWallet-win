
import asyncio
import clr
from pathlib import Path
from typing import Optional, Union, List, Callable
import re
import inspect
import math

clr.AddReference(r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\PresentationFramework.dll")
clr.AddReference(r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\WindowsFormsIntegration.dll")

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('System.Threading')
clr.AddReference("WindowsFormsIntegration")
clr.AddReference('PresentationCore')
clr.AddReference("PresentationFramework")
clr.AddReference("WindowsBase")

import System as Sys
import System.IO as Os
import System.Drawing as Drawing
import System.Windows.Forms as Forms
import System.Threading.Tasks as Tasks
import Microsoft.Win32 as Win32

from System.Windows.Media.Media3D import (
    PerspectiveCamera, DirectionalLight, Model3DGroup, GeometryModel3D, MeshGeometry3D,
    Point3D, Vector3D, DiffuseMaterial, ModelVisual3D, AxisAngleRotation3D, RotateTransform3D
)
from System.Windows import Point
from System.Windows.Media import Colors, SolidColorBrush, ImageBrush, Stretch
from System.Windows.Media.Imaging import BitmapImage
from System.Windows.Controls import Viewport3D, UserControl
from System.Windows.Threading import DispatcherTimer



def get_app_path():
    script_path = Os.Path.GetDirectoryName(Os.Path.GetFullPath(__file__))
    app_path = Os.Path.GetDirectoryName(script_path)
    return app_path

def run_async(action):
    task_action = Sys.Action(lambda: asyncio.run(action))
    Tasks.Task.Factory.StartNew(task_action)

class FontStyle:
    REGULAR = Drawing.FontStyle.Regular
    BOLD = Drawing.FontStyle.Bold
    ITALIC = Drawing.FontStyle.Italic
    
class AlignContent:
    LEFT = Drawing.ContentAlignment.MiddleLeft
    CENTER = Drawing.ContentAlignment.MiddleCenter
    RIGHT = Drawing.ContentAlignment.MiddleRight

class AlignTable:
    MIDCENTER = Forms.DataGridViewContentAlignment.MiddleCenter
    MIDLEFT = Forms.DataGridViewContentAlignment.MiddleLeft

class AlignRichLabel:
    CENTER = Forms.HorizontalAlignment.Center
    RIGHT = Forms.HorizontalAlignment.Right
    LEFT = Forms.HorizontalAlignment.Left

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
    GREENYELLO = Drawing.Color.GreenYellow
    CYAN = Drawing.Color.Cyan
    BLUEVIOLET = Drawing.Color.BlueViolet

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
    MAXIMIZED = Forms.FormWindowState.Maximized

class FormBorderStyle:
    NONE = Forms.FormBorderStyle(0)
    SIZABLE = Forms.FormBorderStyle.Sizable

class BorderStyle:
    NONE = Forms.BorderStyle(0)


class FlatStyle:
    FLAT = Forms.FlatStyle.Flat
    STANDARD = Forms.FlatStyle.Standard


class Relation:
    IMAGEBEFORETEXT = Forms.TextImageRelation.ImageBeforeText
    TEXTBEFORIMAGE = Forms.TextImageRelation.TextBeforeImage
    

class ClipBoard(Forms.Clipboard):
    def __init__(self):
        super().__init__()

    def copy(self, value):
        self.SetText(value)

    def paste(self):
        if self.ContainsText():
            return self.GetText()
        return ""

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
    HAND = Forms.Cursors.Hand
    
    
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
    Up = Forms.Keys.Up
    Down = Forms.Keys.Down

    F1 = Forms.Keys.F1
    F4 = Forms.Keys.F4
    F12 = Forms.Keys.F12
    A = Forms.Keys.A
    C = Forms.Keys.C
    Q = Forms.Keys.Q
    N = Forms.Keys.N
    L = Forms.Keys.L
    R = Forms.Keys.R



class CustomFont:
    def __init__(self, settings):
        lang = settings.language()
        if lang:
            if lang == "Arabic":
                font = 'fonts/Cairo.ttf'
            else:
                font = 'fonts/Monda.ttf'
        else:
            font = 'fonts/Monda.ttf'
        self.font_path = Os.Path.Combine(get_app_path(), font)
        self.font_collection = Drawing.Text.PrivateFontCollection()
        self.font_collection.AddFontFile(self.font_path)
        self.font_family = self.font_collection.Families[0]

        self.font_cache = {}

    def get(self, size, bold=False):
        style = FontStyle.BOLD if bold else FontStyle.REGULAR
        key = (size, style)
        if key not in self.font_cache:
            self.font_cache[key] = Drawing.Font(self.font_family, size, style)
        return self.font_cache[key]
    


class BTCZControl(UserControl):
    def __init__(self, face_image, back_image, speed):

        UserControl.__init__(self)
        self.viewport = Viewport3D()
        self.Content = self.viewport

        radius = 1.0
        thickness = 0.2
        segments = 64

        self._speed = speed

        camera = PerspectiveCamera()
        camera.Position = Point3D(0, 3, 0)
        camera.LookDirection = Vector3D(0, -1, 0)
        camera.UpDirection = Vector3D(0, 0, -1)
        camera.FieldOfView = 60
        self.viewport.Camera = camera

        light1 = DirectionalLight(Colors.White, Vector3D(-1, -2, 1))
        light2 = DirectionalLight(Colors.White, Vector3D(1, 2, -1))

        mesh = self.create_coin_mesh(radius, thickness, segments)
        body_material = DiffuseMaterial(SolidColorBrush(Colors.Gold))
        self.coin_model = GeometryModel3D(mesh, body_material)

        face_path = Os.Path.Combine(get_app_path(), face_image)
        top_uri = Sys.Uri(face_path, Sys.UriKind.Absolute)
        top_brush = ImageBrush(BitmapImage(top_uri))
        top_brush.Stretch = Stretch.Fill
        self.top_face_model = self.create_face(radius, thickness/2, segments, top_brush, is_top=True)

        back_path = Os.Path.Combine(get_app_path(), back_image)
        bottom_uri = Sys.Uri(back_path, Sys.UriKind.Absolute)
        bottom_brush = ImageBrush(BitmapImage(bottom_uri))
        bottom_brush.Stretch = Stretch.Fill
        self.bottom_face_model = self.create_face(radius, -thickness/2, segments, bottom_brush, is_top=False)

        self.group = Model3DGroup()
        self.group.Children.Add(light1)
        self.group.Children.Add(light2)
        self.group.Children.Add(self.coin_model)
        self.group.Children.Add(self.top_face_model)
        self.group.Children.Add(self.bottom_face_model)

        self.rotation = AxisAngleRotation3D(Vector3D(0, 0, 1), 0)
        rotate_transform = RotateTransform3D(self.rotation)
        self.group.Transform = rotate_transform

        visual = ModelVisual3D()
        visual.Content = self.group
        self.viewport.Children.Add(visual)

        self.timer = DispatcherTimer()
        self.timer.Interval = Sys.TimeSpan.FromMilliseconds(20)
        self.timer.Tick += self.update_rotation
        self.timer.Start()

    
    def create_coin_mesh(self, radius=1.0, thickness=0.2, segments=64):
        mesh = MeshGeometry3D()
        top_center = Point3D(0, thickness/2, 0)
        bottom_center = Point3D(0, -thickness/2, 0)
        mesh.Positions.Add(top_center)
        mesh.Positions.Add(bottom_center)

        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            mesh.Positions.Add(Point3D(x, thickness/2, z))
            mesh.Positions.Add(Point3D(x, -thickness/2, z))

        for i in range(segments):
            next_i = (i + 1) % segments
            top_i = 2 + i*2
            bottom_i = top_i + 1
            next_top_i = 2 + next_i*2
            next_bottom_i = next_top_i + 1

            mesh.TriangleIndices.Add(0)
            mesh.TriangleIndices.Add(next_top_i)
            mesh.TriangleIndices.Add(top_i)

            mesh.TriangleIndices.Add(1)
            mesh.TriangleIndices.Add(bottom_i)
            mesh.TriangleIndices.Add(next_bottom_i)

            mesh.TriangleIndices.Add(top_i)
            mesh.TriangleIndices.Add(next_top_i)
            mesh.TriangleIndices.Add(bottom_i)

            mesh.TriangleIndices.Add(next_top_i)
            mesh.TriangleIndices.Add(next_bottom_i)
            mesh.TriangleIndices.Add(bottom_i)

        return mesh
    
    def create_face(self, radius, y_pos, segments, brush, is_top=True):
        mesh = MeshGeometry3D()
        mesh.Positions.Add(Point3D(0, y_pos, 0))
        mesh.TextureCoordinates.Add(Point(0.5, 0.5))
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            mesh.Positions.Add(Point3D(x, y_pos, z))
            u = 0.5 + (x / (2 * radius))
            v = 0.5 + (z / (2 * radius))
            mesh.TextureCoordinates.Add(Point(u, v))

        for i in range(segments):
            next_i = (i + 1) % segments
            if is_top:
                mesh.TriangleIndices.Add(0)
                mesh.TriangleIndices.Add(next_i + 1)
                mesh.TriangleIndices.Add(i + 1)
            else:
                mesh.TriangleIndices.Add(0)
                mesh.TriangleIndices.Add(i + 1)
                mesh.TriangleIndices.Add(next_i + 1)

        material = DiffuseMaterial(brush)
        return GeometryModel3D(mesh, material)
    

    def update_rotation(self, sender, e):
        self.rotation.Angle += self._speed
        if self.rotation.Angle >= 360:
            self.rotation.Angle = 0


class Separator(Forms.ToolStripSeparator):
    def __init__(self):
        super().__init__()


class MenuStrip(Forms.ContextMenuStrip):
    def __init__(self, rtl: bool = None):
        super().__init__()

        if rtl:
            self.RightToLeft = RightToLeft.YES


class Toolbar(Forms.MenuStrip):
    def __init__(
        self,
        color: Optional[Color] = None,
        background_color: Optional[Color] = None,
        rtl: bool = None
    ):
        super().__init__()

        self.commands = []
        
        self._color = color
        self._background_color = background_color
        self._rtl = rtl

        if self._color:
            self.ForeColor = self._color

        if self._background_color:
            self.BackColor = self._background_color

        if self._rtl:
            self.RightToLeft = RightToLeft.YES

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
        dockstyle: Optional[DockStyle] = None,
        rtl: bool = None
    ):
        super().__init__()

        self.items = []
        self._color = color
        self._background_color = background_color
        self._dockstyle = dockstyle
        self._rtl = rtl

        if self._color:
            self.ForeColor = self._color

        if self._background_color:
            self.BackColor = self._background_color

        if self._dockstyle:
            self.Dock = self._dockstyle
        if self._rtl:
            self.RightToLeft = RightToLeft.YES
        
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
        font = None,
        color : Optional[Color] = None,
        background_color :Optional[Color] = None,
        text_align:Optional[AlignContent] = None,
        image_align:Optional[AlignContent] =None,
        spring : bool = None,
        autotooltip:bool = False,
        rtl: bool = None
    ):
        super().__init__()

        self._text = text
        self._image_path = image
        self._font = font
        self._color = color
        self._background_color = background_color
        self._text_align = text_align
        self._image_align = image_align
        self._spring = spring
        self._autotooltip = autotooltip
        self._rtl = rtl

        self.app_path  = get_app_path()

        if self._text:
            self.Text = self._text
        if self._image_path:
            self._set_image(self._image_path)
        self.Font = self._font
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
        if self._autotooltip:
            self.AutoToolTip = self._autotooltip
        if self._rtl:   
            self.RightToLeft = RightToLeft.YES

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
        font = None,
        background_color :Optional[Color] = None,
        mouse_enter: Optional[Callable] = None,
        mouse_leave: Optional[Callable] = None,
        mouse_up: Optional[Callable] = None,
        mouse_down : Optional[Callable] = None,
        checked: Optional[bool] = False,
        checked_changed: Optional[Callable[[], None]] = None,
        drop_opened: Optional[Callable[[], None]] = None,
        drop_closed: Optional[Callable[[], None]] = None,
        shortcut_key: Optional[Keys] = None,
        tooltip: Optional[str] = None,
        rtl: bool = False
    ):
        super().__init__(title)

        self._title = title
        self._action = action
        self._sub_commands = sub_commands
        self._icon = icon
        self._color = color
        self._font = font
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
        self._tooltip = tooltip
        self._rtl = rtl

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
        self.Font = self._font
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
        if self._tooltip:
            self.ToolTipText = self._tooltip
        if self._rtl:
            self.RightToLeft = RightToLeft.YES
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
            sig = inspect.signature(self._action)
            param_count = len(sig.parameters)
            try:
                if param_count == 0:
                    self._action()
                elif param_count == 1:
                    self._action(sender)
                else:
                    self._action(sender, event)
            except Exception as e:
                print(f"Error invoking action for {self._title}: {e}")


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
            sig = inspect.signature(self._mouse_enter)
            param_count = len(sig.parameters)
            try:
                if param_count == 0:
                    self._mouse_enter()
                elif param_count == 1:
                    self._mouse_enter(sender)
                else:
                    self._mouse_enter(sender, event)
            except Exception as e:
                print(f"Error invoking mouse_enter for {self._title}: {e}")

    def _handle_mouse_leave(self, sender, event):
        if self._mouse_leave:
            sig = inspect.signature(self._mouse_leave)
            param_count = len(sig.parameters)
            try:
                if param_count == 0:
                    self._mouse_leave()
                elif param_count == 1:
                    self._mouse_leave(sender)
                else:
                    self._mouse_leave(sender, event)
            except Exception as e:
                print(f"Error invoking mouse_leave for {self._title}: {e}")

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



class TextBox(Forms.ToolStripTextBox):
    def __init__(self, font):
        super().__init__()

        self.ReadOnly = True
        self.AutoSize = False
        self.BorderStyle = BorderStyle.NONE
        self.Width = 180
        self.Font = font

    @property
    def text(self) -> str:
        return self.Text

    @text.setter
    def text(self, value: str):
        self.Text = value



class NotifyIcon(Forms.NotifyIcon):
    def __init__(
        self,
        text: Optional[str] = None,
        icon: Path = None,
        double_click: Optional[Callable] = None,
        commands: Optional[List[type]] = None
    ):
        super().__init__()
        self._text = text
        self._icon = icon
        self._double_click = double_click
        self._commands = commands

        self.app_path = get_app_path()

        if self._icon:
            full_path = str(Os.Path.Combine(self.app_path , self._icon))
            self.Icon = Drawing.Icon(str(full_path))

        if self._text:
            self.Text = self._text

        if self._double_click:
            self.MouseDoubleClick += self._on_double_click

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

    @property
    def icon(self) -> Optional[Path]:
        return self._icon

    @icon.setter
    def icon(self, value: Path):
        self._icon = value
        if self._icon:
            full_path = str(Os.Path.Combine(self.app_path, self._icon))
            self.Icon = Drawing.Icon(full_path)

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

    def _on_double_click(self, sender, event):
        if self._double_click:
            self._double_click()

    def show(self):
        self.Visible = True

    def show_context(self):
        if self.ContextMenuStrip:
            self.ContextMenuStrip.Show(Forms.Cursor.Position)

    def hide(self):
        if self.Visible:
            self.Visible = False
    
    def dispose(self):
        self.Dispose()



class Table(Forms.DataGridView):
    def __init__(
        self,
        location: tuple[int, int] = None,
        text_color: Optional[Color] = None,
        background_color: Optional[Color] = None,
        cell_color: Optional[Color] = None,
        align: Optional[AlignContent] = None,
        font = None,
        cell_font = None,
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
        on_double_click: Optional[Callable[[Forms.DataGridViewCellEventArgs], None]] = None,
        rtl: bool = None
    ):
        super().__init__()
        
        self._location = location
        self._text_color = text_color
        self._background_color = background_color
        self._cell_color = cell_color
        self._align = align
        self._font = font
        self._cell_font = cell_font
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
        self._rtl = rtl

        self.app_path = get_app_path()

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
        self.DefaultCellStyle.Font = self._cell_font
        self.Font = self._font
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
        if self._rtl:
            self.RightToLeft = RightToLeft.YES

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

    def disable_sorting(self):
        for column in self.Columns:
            column.SortMode = Forms.DataGridViewColumnSortMode.NotSortable

    def set_data_source(self, data: Optional[Union[List[dict], List[List]]]):
        self.Rows.Clear()
        self.Columns.Clear()
        
        if not data:
            return

        if isinstance(data[0], dict):
            for i, (key, value) in enumerate(data[0].items()):
                if isinstance(value, str) and value.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    column = Forms.DataGridViewImageColumn()
                    column.Name = key
                    column.HeaderText = key
                else:
                    column = Forms.DataGridViewTextBoxColumn()
                    column.Name = key
                    column.HeaderText = key
                self.Columns.Add(column)
            
            for row in data:
                formatted_row = []
                for k in row:
                    value = row[k]
                    if isinstance(value, str) and value.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                        try:
                            full_path = str(Os.Path.Combine(self.app_path , value))
                            if Os.File.Exists(full_path):
                                image = Drawing.Image.FromFile(full_path)
                                formatted_row.append(image)
                        except Exception as e:
                            print(f"Failed to load image '{value}': {e}")
                            formatted_row.append(None)
                    else:
                        formatted_row.append(value)
                self.Rows.Add(*formatted_row)
        
        elif isinstance(data[0], list):
            for i, value in enumerate(data[0]):
                if isinstance(value, str) and value.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    column = Forms.DataGridViewImageColumn()
                else:
                    column = Forms.DataGridViewTextBoxColumn()
                self.Columns.Add(column)
            
            for row in data:
                formatted_row = []
                for value in row:
                    if isinstance(value, str) and value.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                        try:
                            full_path = str(Os.Path.Combine(self.app_path , value))
                            if Os.File.Exists(full_path):
                                image = Drawing.Image.FromFile(full_path)
                                formatted_row.append(image)
                        except Exception as e:
                            print(f"Failed to load image '{value}': {e}")
                            formatted_row.append(None)
                    else:
                        formatted_row.append(value)
                self.Rows.Add(formatted_row)

        self.update_column_widths()
        self.Invoke(Forms.MethodInvoker(lambda: self._resize_columns()))
        self.disable_sorting()


    
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
                        if isinstance(value, str) and value.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                            try:
                                full_path = str(Os.Path.Combine(self.app_path, value))
                                if Os.File.Exists(full_path):
                                    image = Drawing.Image.FromFile(full_path)
                                    value = image
                            except Exception as e:
                                print(f"Failed to load image from '{value}': {e}")
                                value = None
                        row[col_index] = value
                    else:
                        raise ValueError(f"Column '{key}' not found.")
            else:
                row = [None] * self.ColumnCount
                for col_index, value in row_data.items():
                    if 0 <= col_index < self.ColumnCount:
                        if isinstance(value, str) and value.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                            try:
                                full_path = str(Os.Path.Combine(self.app_path, value))
                                if Os.File.Exists(full_path):
                                    image = Drawing.Image.FromFile(full_path)
                                    value = image
                            except Exception as e:
                                print(f"Failed to load image from '{value}': {e}")
                                value = None
                        row[col_index] = value
                    else:
                        raise IndexError(f"Column index {col_index} is out of range.")
        elif isinstance(row_data, list):
            if len(row_data) != self.ColumnCount:
                raise ValueError("Row data length does not match the number of columns.")
            row = []
            for value in row_data:
                if isinstance(value, str) and value.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    try:
                        full_path = str(Os.Path.Combine(self.app_path, value))
                        if Os.File.Exists(full_path):
                            image = Drawing.Image.FromFile(full_path)
                            value = image
                    except Exception as e:
                        print(f"Failed to load image from '{value}': {e}")
                        value = None
                row.append(value)
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
        font = None,
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
        mouse_wheel: Optional[Callable] = None,
        mouse_move: bool = False
    ):
        super().__init__()

        self._text = text
        self._font = font
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
        self._mouse_move = mouse_move

        self.tooltip = Forms.ToolTip()
        self.tooltip_visible = None

        if self._text:
            self.Text = self._text
        if self._font is None:
            try:
                self.Font = Drawing.Font("Segoe UI Emoji", 10.5)
            except:
                self.Font = Drawing.Font("Segoe UI Symbol", 10.5)
        else:
            self.Font = self._font
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
        if self._mouse_move:
            self.MouseMove += self.on_mouse_move
            self.MouseLeave += self.on_mouse_leave
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
        if Forms.Control.ModifierKeys == Keys.Control:
            if self._urls_click:
                self._urls_click(event.LinkText)

    
    def on_mouse_move(self, sender, event):
        pos = event.Location
        link_pos = self.GetCharIndexFromPosition(pos)
        link_text = self.get_url_at_position(link_pos)
        if link_text:
            if not self.tooltip_visible:
                self.tooltip.Show(f"Open link (ctrl + click)", self, pos.X, pos.Y - 25)
                self.tooltip_visible = True
            else:
                self.tooltip.Show(f"Open link (ctrl + click)", self, pos.X, pos.Y - 25)
            self.LinkCursor = Cursors.DEFAULT
        else:
            if self.tooltip_visible:
                self.tooltip.Hide(self)
                self.tooltip_visible = False

    
    def on_mouse_leave(self, sender, event):
        if self.tooltip_visible:
            self.tooltip.Hide(self)
            self.tooltip_visible = False
            

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