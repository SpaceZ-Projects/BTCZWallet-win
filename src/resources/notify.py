
import psutil

from toga import App, Window
from ..framework import NotifyIcon, Command

from .client import Client


class Notify(NotifyIcon):
    def __init__(self, app:App, main:Window, home_page, mining_page):

        self.app = app
        self.main = main
        self.home_page = home_page
        self.mining_page = mining_page

        self.commands = Client(self.app)

        self.stop_exit_cmd = Command(
            title="Stop node",
            action=self.stop_node_exit,
            icon="images/stop.ico"
        )

        self.exit_cmd = Command(
            title="Exit",
            action=self.exit_app,
            icon="images/exit.ico"
        )
        super().__init__(
            icon="images/BitcoinZ.ico",
            text = "BitcoinZ Wallet",
            double_click=self.show_menu,
            commands=[
                self.stop_exit_cmd,
                self.exit_cmd
            ]
        )

    def show_menu(self):
        self.main.show()

    def exit_app(self):
        def on_result(widget, result):
            if result is True:
                self.home_page.bitcoinz_curve.image = None
                self.home_page.clear_cache()
                self.hide()
                self.app.exit()
        if self.mining_page.mining_status:
            return
        self.main.question_dialog(
            title="Exit app",
            message="Are you sure you want to exit the application ?",
            on_result=on_result
        )

    def stop_tor(self):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "tor.exe":
                    proc.kill()
        except Exception as e:
            pass

    def stop_node_exit(self):
        async def on_result(widget, result):
            if result is True:
                self.stop_tor()
                await self.commands.stopNode()
                self.home_page.bitcoinz_curve.image = None
                self.home_page.clear_cache()
                self.hide()
                self.app.exit()

        if self.mining_page.mining_status:
            return
        self.main.question_dialog(
            title="Exit app",
            message="Are you sure you want to stop the node and exit the application ?",
            on_result=on_result
        )



class NotifyTx(NotifyIcon):
    def __init__(self):
        super().__init__(
            icon="images/tx.ico",
            text = "New Transaction"
        )


class NotifyRequest(NotifyIcon):
    def __init__(self):
        super().__init__(
            icon="images/new_request.ico",
            text = "New Request"
        )


class NotifyMessage(NotifyIcon):
    def __init__(self):
        super().__init__(
            icon="images/new_message.ico",
            text = "New Message"
        )
