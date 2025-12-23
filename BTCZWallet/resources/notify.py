
from toga import App, Window
from ..framework import NotifyIcon, Command, FormState, TextBox


class Notify(NotifyIcon):
    def __init__(self, app:App, main:Window, settings, utils, rpc, tr, font):

        self.app = app
        self.main = main
        
        self.settings = settings
        self.utils = utils
        self.rpc = rpc
        self.tr = tr

        self.rtl = None
        lang = self.settings.language()
        if lang:
            if lang == "Arabic":
                self.rtl = True

        self.restart_cmd = Command(
            title="Restart",
            action=lambda : self.exit_app("restart"),
            icon="images/restart_a.ico",
            font=font.get(9),
            rtl = self.rtl
        )
        self.stop_exit_cmd = Command(
            title=self.tr.text("notifystopexit_cmd"),
            action=lambda : self.exit_app("full"),
            icon="images/stop.ico",
            font=font.get(9),
            rtl=self.rtl
        )

        self.exit_cmd = Command(
            title=self.tr.text("notifyexit_cmd"),
            action=lambda : self.exit_app("default"),
            icon="images/exit.ico",
            font=font.get(9),
            rtl=self.rtl
        )
        super().__init__(
            icon="images/BitcoinZ.ico",
            text = "BitcoinZ Wallet",
            double_click=self.show_menu,
            commands=[
                self.restart_cmd,
                self.stop_exit_cmd,
                self.exit_cmd
            ]
        )

    def show_menu(self):
        if self.main.mining_page.mining_status:
            self.main.notifymining.hide()
        if self.main._is_hidden:
            self.main.show()
            self.main._is_hidden = None
            if self.main.console_toggle:
                self.app.console.show()
        if self.main._is_minimized:
            self.main._impl.native.WindowState = FormState.NORMAL
        if self.app.current_window is not self.main:
            self.main._impl.native.TopMost = True
            self.main._impl.native.TopMost = False


    def exit_app(self, option):
        async def on_result(widget, result):
            if result is True:
                if option == "full":
                    self.utils.stop_tor()
                    await self.rpc.stopNode()

                elif option == "restart":
                    result = self.utils.restart_app()
                    if not result:
                        return
                    self.utils.stop_tor()
                    await self.rpc.stopNode()

                self.main.home_page.bitcoinz_curve.image = None
                if self.main.console_toggle:
                    self.app.console._impl.native.Close()
                self.main.home_page.clear_cache()
                self.main.notify.hide()
                self.main.notify.dispose()
                if self.main.market_server.server_status:
                    self.main.notifymarket.hide()
                    self.main.notifymarket.dispose()
                if self.main.mobile_server.server_status:
                    self.main.notifymobile.hide()
                    self.main.notifymobile.dispose()
                self.app.exit()

        if self.main.mining_page.mining_status:
            return
        if option == "full":
            title=self.tr.title("stopexit_dialog")
            message=self.tr.message("stopexit_dialog")

        elif option == "restart":
            title="Restart App"
            message="Are you sure you want to restart the application ?"

        else:
            title=self.tr.title("exit_dialog")
            message=self.tr.message("exit_dialog")

        self.main.question_dialog(
            title=title,
            message=message,
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


class NotifyMarket(NotifyIcon):
    def __init__(self):
        super().__init__(
            icon="images/Market.ico",
            text = "Marketplace Server"
        )


class NotifyMobile(NotifyIcon):
    def __init__(self):
        super().__init__(
            icon="images/Mobile.ico",
            text = "Mobile Server"
        )
