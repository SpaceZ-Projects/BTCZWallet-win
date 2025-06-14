
import psutil

from toga import App, Window
from ..framework import NotifyIcon, Command, FormState, TextBox


class Notify(NotifyIcon):
    def __init__(self, app:App, main:Window, home_page, mining_page, settings, commands, tr, font):

        self.app = app
        self.main = main
        self.home_page = home_page
        self.mining_page = mining_page
        
        self.settings = settings
        self.commands = commands
        self.tr = tr

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.stop_exit_cmd = Command(
            title=self.tr.text("notifystopexit_cmd"),
            action=self.stop_node_exit,
            icon="images/stop.ico",
            font=font.get(9),
            rtl=self.rtl
        )

        self.exit_cmd = Command(
            title=self.tr.text("notifyexit_cmd"),
            action=self.exit_app,
            icon="images/exit.ico",
            font=font.get(9),
            rtl=self.rtl
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
        if self.mining_page.mining_status:
            self.main.notifymining.hide()
        if self.main._is_hidden:
            self.main.show()
            self.main._is_hidden = None
        if self.main._is_minimized:
            self.main._impl.native.WindowState = FormState.NORMAL
        if self.app.current_window is not self.main:
            self.main._impl.native.Activate()
            

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
            title=self.tr.title("exit_dialog"),
            message=self.tr.message("exit_dialog"),
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
            title=self.tr.title("stopexit_dialog"),
            message=self.tr.message("stopexit_dialog"),
            on_result=on_result
        )


class NotifyMining(NotifyIcon):
    def __init__(self, font):

        self.solutions = TextBox(font.get(8))
        self.balance = TextBox(font.get(8))
        self.immature = TextBox(font.get(8))
        self.paid = TextBox(font.get(8))

        super().__init__(
            icon="images/mining_notify.ico",
            text = "Mining",
            commands=[
                self.solutions,
                self.balance,
                self.immature,
                self.paid
            ]
        )



class NotifyTx(NotifyIcon):
    def __init__(self, icon = None):
        super().__init__(
            icon=icon,
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
