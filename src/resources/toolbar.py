
from framework import App, Toolbar, Command, Color

class AppToolBar(Toolbar):
    def __init__(self):
        super().__init__()

        self.app = App()

        self.file_tool_active = None
        self.wallet_tool_active = None
        self.color=Color.WHITE
        self.background_color=Color.rgb(30,33,36)

        self.about_cmd = Command(
            title="About",
            color=Color.WHITE,
            background_color=Color.rgb(30,33,36),
            mouse_enter=self.about_cmd_mouse_enter,
            mouse_leave=self.about_cmd_mouse_leave
        )
        self.exit_cmd = Command(
            title="Exit",
            color=Color.RED,
            background_color=Color.rgb(30,33,36),
            action=self.exit_app
        )
        self.file_tool = Command(
            title="File",
            sub_commands=[
                self.about_cmd,
                self.exit_cmd
            ],
            drop_opened=self.file_tool_opened,
            drop_closed=self.file_tool_closed,
            mouse_enter=self.file_tool_mouse_enter,
            mouse_leave=self.file_tool_mouse_leave
        )
        self.wallet_tool = Command(
            title="Wallet",
            mouse_enter=self.wallet_tool_mouse_enter,
            mouse_leave=self.wallet_tool_mouse_leave
        )
        self.add_command(
            [
                self.file_tool,
                self.wallet_tool
            ]
        )


    def file_tool_opened(self):
        self.file_tool_active = True
        self.file_tool.color = Color.BLACK

    def file_tool_closed(self):
        self.file_tool_active = False
        self.file_tool.color = Color.WHITE

    def file_tool_mouse_enter(self):
        self.file_tool.color = Color.BLACK

    def file_tool_mouse_leave(self):
        if self.file_tool_active:
            return
        self.file_tool.color = Color.WHITE

    def wallet_tool_mouse_enter(self):
        self.wallet_tool.color = Color.BLACK

    def wallet_tool_mouse_leave(self):
        self.wallet_tool.color = Color.WHITE

    def about_cmd_mouse_enter(self):
        self.about_cmd.color = Color.BLACK

    def about_cmd_mouse_leave(self):
        self.about_cmd.color = Color.WHITE

    def exit_app(self, command):
        self.app._main_window.exit()