
from toga import App
from ..framework import NotifyIcon, Command


class Notify(NotifyIcon):
    def __init__(self, app:App, home_page, mining_page):

        self.app = app
        self.home_page = home_page
        self.mining_page = mining_page

        self.exit_cmd = Command(
            title="Exit",
            action=self.exit_app
        )
        super().__init__(
            icon="images/BitcoinZ.ico",
            text = "BitcoinZ Wallet",
            commands=[self.exit_cmd]
        )

    def exit_app(self):
        if self.mining_page.mining_status:
            return
        self.home_page.bitcoinz_curve.image = None
        self.home_page.clear_cache()
        self.hide()
        self.app.exit()



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
